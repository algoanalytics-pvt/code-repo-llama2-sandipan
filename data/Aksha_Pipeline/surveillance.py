from locale import currency
import sys
import os
import cv2
import numpy as np
import pymongo
import joblib
import datetime as dt
import logging
from logging.handlers import TimedRotatingFileHandler
import math
import object_detection as od
import prefilter
import postfilter
import notification
import data_preprocessor as dp
import my_alert_filters as maf
import random
import ast
import threading
import deletion
import json
import requests
from urllib.request import urlretrieve
import gzip 
import shutil
import configparser


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
        # print(base_path, "<<<<<<<<<< exe_base_path")
    except Exception as e:
        base_path = os.path.abspath(".")
        # print(base_path, "<<<<<<< base_path")
    return os.path.join(base_path, relative_path)

class Run:
    """
    This Class starts the program of Aksha PipeLine right from creating directories to writing frames to the
        respective paths based on predictions and alerts.
    """

    def __init__(self, config, camera_name, update_camera_name, rtsp_id, my_alerts, whats_app_service, telegram_service, video_path, skip_fps_sec,
                 output_size, object_detection, prefilter_threshold, email_autoalert,crowd_threshold, time_delta,
                 autoalert_display, email_alert, alert_display):
        """
        Initializes necessary varibles and starts the mai application logic. Instances of remaining
        classes of Surveillance.py file are created in here.

        Args:
            config (dict): holds the respective values for database connection string and SAS url for Aksha blob storage on azure depending on dev/prod environment
            camera_name (string): Name of the camera
            my_alerts (string): Customized Alerts 
            whats_app_service (bool): Enable WhatsApp service
            video_path (string): Path of video file: rtsp link
            skip_fps_sec (float): inferance interval in sec.
            output_size (int): size of the output image
            object_detection (bool): object detection service
            prefilter_threshold (float): threshold for deciding if two consequtive frames are similar or not
            email_autoalert (bool): Enable notification service for Autoalerts
        """        

        self.config = config
        self.camera_name = camera_name
        self.update_camera_name = update_camera_name
        self.rtsp_id = rtsp_id
        self.my_alerts = my_alerts
        self.video_path = video_path
        self.skip_fps_sec = skip_fps_sec
        self.output_size = output_size
        self.object_detection = object_detection
        self.prefilter_threshold = prefilter_threshold
        self.email_autoalert = email_autoalert
        self.crowd_threshold = crowd_threshold
        self.time_delta = time_delta
        self.autoalert_display = autoalert_display
        self.email_alert = email_alert
        self.alert_display = alert_display
        
        self.main_dir = 'Aksha/'
        # self.main_dir = '/home/algo39/kartikz/Aksha-Version-2/Aksha/'
        self.background_skip_frames = 120
        # self.frames_background_gen = {str(hour): [] for hour in range(24)}
        self.daily_frames = []
        self.daily_frames_temp = []
        self.date = dt.date.today()
        self.cap = None
        self.logger = self.create_logger()
        self.whats_app_service_status = ast.literal_eval(whats_app_service) if whats_app_service is not None else whats_app_service
        self.telegram_service_status = ast.literal_eval(telegram_service) if telegram_service is not None else telegram_service
        
  

        self.setup = Setup(self.config, self.camera_name, self.update_camera_name, self.rtsp_id, self.my_alerts, self.whats_app_service_status, self.telegram_service_status ,self.video_path, self.skip_fps_sec,
                    self.output_size, self.object_detection, self.prefilter_threshold, self.email_autoalert, self.main_dir,
                    self.daily_frames, self.daily_frames_temp, self.logger, self.crowd_threshold)

        self.insight_path = self.setup.create_dir("insight")
        self.frame_path = self.setup.create_dir("frame")
        self.alert_path = self.setup.create_dir("alerts")
        self.background_path = self.setup.create_dir("background")
        self.foreground_path = self.setup.create_dir("foreground")
        self.live_path = self.setup.create_dir("live")
        try:
            LOADING_IMG = cv2.imread(resource_path("LOADING_IMG.png"))
            cv2.imwrite(f"{self.live_path}/workday.jpg",LOADING_IMG)
            cv2.imwrite(f"{self.live_path}/holiday.jpg",LOADING_IMG)      
            self.logger.info(msg=f'Live loading in progress...')
        except Exception as e:
            self.logger.info(msg=f'Live loading error: {e}')
        self.spotlight_path = self.setup.create_dir("spotlight")
        self.reference_img_path = self.setup.create_dir("Reference_images")
        self.insight_report_path= self.setup.create_dir("insight_report")
        self.DATABASE, self.COLLECTION_Meta, self.COLLECTION_Alerts, self.COLLECTION_Resource = self.setup.load_database()
        self.LIST_MYALERT_CONFIG, self.previous_alert_statuses, self.no_object_alert = self.setup.create_alerts_config_list(self.COLLECTION_Alerts)
        self.folder_id = self.setup.notif_gdrive_folder_id()
        self.recipients, self.subscription = self.setup.notif_setup_email(self.COLLECTION_Resource)
        self.subscription, self.whats_app_service = self.setup.notif_setup_whatsapp(self.COLLECTION_Resource)
        self.subscription, self.telegram_service = self.setup.notif_setup_telegram(self.COLLECTION_Resource)
        self.camera_configuration = self.setup.camera_configuration(self.DATABASE)
        self.object_detection_service, self.class_names, self.colors = od.load_object_detection_model(resource_path("yolov7.onnx"),resource_path("coco.names"))
        self.RTSP_Down = False
        try:
            self.prev_spotlight = False
            while True:
                previous_image_status = False
                reference_image = False
                self.ANOMALY_MODEL = 25
                self.current_hour = 25
                self.cap = self.setup.read_video()
                skip_fps = math.floor(
                    int(self.cap.get(cv2.CAP_PROP_FPS)) * self.skip_fps_sec)
                self.background_skip_frames_local = math.floor(
                    int(self.cap.get(cv2.CAP_PROP_FPS)) * self.background_skip_frames)
                print("Skip fps ...", skip_fps)
                self.count = 0
                self.background_count = 0
                try:
                    while True:
                        self.no_object_status = False

                        try:
                            ret, self.frame = self.cap.read()
                            if ret:
                                self.im_name = dt.datetime.now().replace(microsecond=0)
                                if str(self.im_name.time()) == "09:00:00":
                                    self.setup.store_reference_image(self.frame, self.reference_img_path)
                                    reference_image = True
                                if not reference_image:
                                    self.setup.store_reference_image(self.frame, self.reference_img_path)
                                    reference_image = True

                        except Exception as e:                 
                            self.logger.info(msg=f"Reading frame issue {e}")
                                               
                        
                        if ret:
                            # self.logger.info(msg=f"ret success")
                            if self.RTSP_Down:
                                notification.error_notification(self.subscription, "RTSP working", self.recipients, self.camera_name, self.video_path, self.RTSP_Down)
                                self.RTSP_Down = False
                            try:
                                self.im_name = dt.datetime.now().replace(microsecond=0)
                                
                                if self.im_name.minute == 7 and self.im_name.second == 00:
                                    if self.im_name.hour != self.current_hour:
                                        self.current_hour = self.im_name.hour 
                                        t1 = threading.Thread(target= deletion.execute, args= (self.DATABASE, self.camera_name, self.main_dir, self.time_delta, self.logger))
                                        self.logger.info(msg=f"Thread for deletion: created")
                                        t1.start()
                                        self.logger.info(msg=f"Thread for deletion: started")
                                
                                if not self.im_name.minute % 5 and self.im_name.second == 00:
                                    self.setup.gen_daily_bgImage(self.im_name, self.background_path)


                                try:
                                    if self.background_count == self.background_skip_frames_local:
                                        self.background_count = 0
                                        # self.frames_background_gen[str(self.im_name.hour)].append(cv2.resize(self.frame, (256,256)))
                                        self.daily_frames.append(cv2.resize(self.frame, (256, 256)))
                                    else:
                                        self.background_count += 1
                                except Exception as e:
                                    print(e)
                                    self.logger.info(msg=f"saving frame in daily_frames list issue {e}")

                                if self.ANOMALY_MODEL != self.im_name.hour:
                                    self.ANOMALY_MODEL = self.im_name.hour
                                    self.FRAME_BASED_ANOMALY_DETECTION_MODEL, self.OBJECT_BASED_ANOMALY_DETECTION_MODEL = self.setup.load_anomaly_models(self.ANOMALY_MODEL)
                                    self.foreground_image_path = self.setup.create_foregroundImg_path(self.foreground_path, self.ANOMALY_MODEL, self.im_name)
                                else:
                                    pass

                            except Exception as e:
                                self.logger.info(msg=e)

                            try:
                                self.object_detection = True
                                if self.count == skip_fps:
                                    self.logger.info(msg= f"count, {self.count}/{skip_fps}")
                                    self.count = 1
                                    try:
                                        self.frame = cv2.resize(self.frame, self.output_size)
                                    except Exception as e:
                                        #print("frame resize error", e)
                                        self.logger.info(msg= f"frame resize error, {e}")

                                    # Frame Anomaly detection process started...
                                    self.frame_anomaly_status = False
                                    self.overlay = None
                                    if previous_image_status:
                                        _, ssim = prefilter.calc_diff(cv2.cvtColor(self.previous_image, cv2.COLOR_BGR2GRAY), cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY))
                                        if ssim > self.prefilter_threshold:
                                            self.logger.info(msg=f"Frame rejected, SSIM: {ssim}, prefilter_threshold: {self.prefilter_threshold}")
                                            cv2.imwrite(
                                                f'{self.live_path}/workday.jpg', self.frame)
                                            cv2.imwrite(
                                                f'{self.live_path}/holiday.jpg', self.frame)
                                            continue
                                        try:
                                            # self.logger.info(msg=f"Current frame is under process due to satisfied condation for SSIM: {ssim} less than prefilter_threshold: {self.prefilter_threshold}")
                                            self.detect_anomaly = AnomalyDetector(self.background_path, self.im_name,
                                                                                  self.frame,
                                                                                  self.foreground_image_path,
                                                                                  self.prefilter_threshold,
                                                                                  self.object_detection_service, self.class_names, self.colors,
                                                                                  self.FRAME_BASED_ANOMALY_DETECTION_MODEL,
                                                                                  self.OBJECT_BASED_ANOMALY_DETECTION_MODEL,
                                                                                  self.logger)
                                            
                                            self.frame_anomaly_status, self.overlay = self.detect_anomaly.frame_based_pred()

                                            self.previous_image = self.frame.copy()

                                        except Exception as e:
                                            self.logger.info(msg=f"getting error with this exception, {e}")
                                    else:
                                        try:
                                            self.logger.info(msg=f"Current frame is under process")
                                            self.detect_anomaly = AnomalyDetector(self.background_path, self.im_name,
                                                                                  self.frame,
                                                                                  self.foreground_image_path,
                                                                                  self.prefilter_threshold,
                                                                                  self.object_detection_service, self.class_names, self.colors,
                                                                                  self.FRAME_BASED_ANOMALY_DETECTION_MODEL,
                                                                                  self.OBJECT_BASED_ANOMALY_DETECTION_MODEL,
                                                                                  self.logger)

                                            self.previous_image = self.frame.copy()
                                            previous_image_status = True
                                        except Exception as e:
                                            self.logger.info(msg=f"getting error with this exception, {e}")

                                    self.logger.info(msg=f"Anomaly status: {self.frame_anomaly_status}")
                                    self.alert_results = []
                                    try:

                                        self.object_detection_results, self.object_anomaly_status, self.classes = self.detect_anomaly.object_based_pred()
                                        # print("$$$$$$$$$$$$$$$ Object detection results..", self.object_detection_results)
                                        self.alert_filter = PostPrediction(self.im_name, self.frame, self.LIST_MYALERT_CONFIG,
                                                                      self.object_detection_results, self.no_object_alert,
                                                                      self.frame_anomaly_status, self.object_anomaly_status,
                                                                      self.frame_path, self.COLLECTION_Meta, self.logger, self.crowd_threshold)

                                        self.alert_results, self.alert_result_config, self.no_object_status, self.alert_description, self.alert_notification_validity, self.noobj_alert_result_config = self.alert_filter.filter()
                                        print("!!!!!!!!!!!!!!!! alert results>>>", self.alert_results)

                                    except Exception as e:
                                        logging.error(
                                            msg=f'getting labels issue with exception, {e}')

                                    try:
                                        try:
                                            self.logger.info(
                                                msg=f'No Alert status is: {self.no_object_status}, db check is: {self.noobj_alert_result_config}')
                                        except Exception as e:
                                            logging.error(
                                                msg=f'No object data loading error: {e}')
                                        self.prepare = FrameAnnotation(self.im_name, self.frame, self.no_object_status, self.alert_result_config,
                                                              self.noobj_alert_result_config, self.frame_anomaly_status, self.overlay, self.object_anomaly_status,
                                                              self.object_detection_results, self.classes, self.live_path, self.logger)

                                        self.check, self.result_img, self.workday_img, self.holiday_img, self.frame_anomaly_validity, self.object_anomaly_validity = self.prepare.frame_prep()

                                        self.logger.info(
                                            msg=f"Previous alert data:{self.previous_alert_statuses}")
                                        self.logger.info(
                                            msg=f'Alert results:{self.alert_results}')

                                        self.notify = Notify(self.check, self.im_name, self.frame, self.result_img, self.workday_img, self.holiday_img,
                                                                    self.camera_name, self.main_dir, self.frame_anomaly_status, self.object_anomaly_status, self.no_object_status,
                                                                    self.alert_results, self.alert_description, self.alert_notification_validity, self.previous_alert_statuses,
                                                                    self.skip_fps_sec, self.alert_path, self.frame_path, self.live_path, self.spotlight_path,
                                                                    self.recipients, self.subscription, self.whats_app_service, self.telegram_service, self.config,
                                                                    self.email_autoalert, self.camera_configuration,
                                                                    self.prev_spotlight, self.object_detection_results, self.folder_id, self.autoalert_display, 
                                                                    self.email_alert, self.alert_display, self.logger)

                                        self.frame_anomaly_validity, self.object_anomaly_validity, self.alert_validity, self.no_object_validity, self.previous_alert_statuses, self.prev_spotlight = self.notify.classify()


                                    except Exception as e:
                                        print("frame__ saving error ", e)
                                        self.logger.info(msg=e)

                                else:
                                    self.count += 1
                                    continue

                            except Exception as e:
                                self.logger.info(msg=e)
                            try:
                                PUBLISH_API = 'http://node_backend:5000/api/monitor/'
                                PUBLISH_URL = f'http://localhost:5000/{self.camera_name}/live/workday.jpg?{self.im_name}'
                                headers = {'Content-type': 'application/json'}
                                data = { "camera_name": self.camera_name, "camera_img_url": PUBLISH_URL}
                                json_data = json.dumps(data)
                                responses = requests.post(PUBLISH_API, data=json_data, headers=headers)
                                print("Socket API")
                            except Exception as e:
                                self.logger.info(msg=f"Publish Image API error: {e}")
                        else:
                            self.logger.info(msg=f'ret failed')
                            try:
                                RTSP_ISSUE_IMG = cv2.imread(resource_path("RTSP_ISSUE_IMG.png"))
                                cv2.imwrite(f"{self.live_path}/workday.jpg",RTSP_ISSUE_IMG)
                                cv2.imwrite(f"{self.live_path}/holiday.jpg",RTSP_ISSUE_IMG)                                
                                self.logger.info(msg=f'Connection lost please check RSTP links ...')
                                if not self.RTSP_Down:
                                    notification.error_notification(self.subscription, "RTSP Error", self.recipients, self.camera_name, self.video_path, self.RTSP_Down)
                                    self.RTSP_Down = True
                            except Exception as err:
                                self.logger.info(msg=f'Connection lost handling error: {err}')
                            break
                        os.sync()
                except Exception as e:
                    print("Start video function failed, Reason:", e)
                self.cap.release()
                print("Restarting video streaming......")
 
        except Exception as e:
            print("Application failed because of this issue :", e)
            self.logger.error(e)

    def create_logger(self):
            """
            Creates/Validates Logger for Log maintainence.

            Returns:
                'logging.RootLogger': Logger Object
            """
            def namer(name):
                return name + ".gz"

            def rotator(source, dest):
                with open(source, 'rb') as f_in:
                    with gzip.open(dest, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(source)

            logfile_path = f'{self.main_dir}{self.camera_name}/log'
            # print(logfile_path)
            logfile_isexist = os.path.exists(logfile_path)
            if not logfile_isexist:
                os.makedirs(logfile_path)
            
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            handler = TimedRotatingFileHandler(f"{logfile_path}/{self.camera_name}.log",
                                        when="midnight",
                                        interval=1,
                                        backupCount=10)
            handler.rotator = rotator
            handler.namer = namer
            handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            logger.addHandler(handler)
            logger.info(msg=f"{logfile_path} ready for logging!")
            return logger
    
class Setup():
    
    def __init__(self, config, camera_name, update_camera_name, rtsp_id, my_alerts, whats_app_service, telegram_service, video_path, skip_fps_sec,
                output_size, object_detection, prefilter_threshold, email_autoalert, main_dir,
                daily_frames, daily_frames_temp, logger, crowd_threshold):
        
        """
        This class takes care of creating directories, coonecting to mongodb database, fetching alert configurations, fetching camera Configuration
        and also notificationrelated detail. Provides functionality for reading frames, creating weekly & daily background frames.

        Args:
            config (dict): dictionary loaded from environment files that has mongodb connection string and azure blob storage SAS URL.
            camera_name (str): name of the respective camera
            my_alerts (string): Customized Alerts as per users
            whats_app_service (bool): Enable WhatsApp service
            video_path (string): Path of video file: rtsp link
            skip_fps_sec (float): inferance interval in sec.
            output_size (int): size of the output image
            object_detection (bool): object detection service
            prefilter_threshold (float): threshold for deciding if two consequtive frames are similar or not
            email_autoalert (bool): Enable notification service for Autoalerts
            main_dir (str): Aksha Directory path
            logger (logging.RootLogger): logger for maintaing logs
        """

        
        self.config = config
        self.main_dir = main_dir
        self.camera_name = camera_name
        self.old_camera_name = camera_name
        self.camera_rename = False
        self.update_camera_name = update_camera_name
        if os.path.exists(f'{self.main_dir}{self.camera_name}/') and (self.update_camera_name!=self.camera_name):
            shutil.move(f'{self.main_dir}{self.camera_name}', f'{self.main_dir}{self.update_camera_name}')
            self.camera_name = self.update_camera_name
            self.camera_rename = True


        self.rtsp_id = rtsp_id
        self.my_alerts = my_alerts
        self.whats_app_service_status = whats_app_service
        self.telegram_service_status = telegram_service
        self.video_path = video_path
        self.skip_fps_sec = skip_fps_sec
        self.output_size = output_size
        self.object_detection = object_detection
        self.prefilter_threshold = prefilter_threshold
        self.email_autoalert = email_autoalert
        self.daily_frames = daily_frames
        self.daily_frames_temp = daily_frames_temp
        self.logger = logger
        self.crowd_threshold = crowd_threshold
        self.date = dt.date.today()
        self.previous_alert_statuses = {"object_alert": {"status": False, "count": 0},
                                        "frame_alert": {"status": False, "count": 0},
                                        "detection_alert": {},
                                        "no_object": {}
                                        }
        self.no_object_alert = []
        self.LIST_MYALERT_CONFIG = []



    def create_dir(self, dir_type):
        """ 
        Create directories for writing frames(accepted values >> 'insight', 'frame', 'alerts', 'background',
                        'foreground', 'live', 'spotlight', 'Reference_images', 'insight_report')
        Args:
            dir_type (str): name of directory
            
        Returns:
            str: directory path
        """  

        if dir_type== 'insight' or  dir_type=='frame' or dir_type=='alerts' or dir_type=='background' or dir_type== 'foreground' or dir_type=='live' or dir_type=='spotlight':
                if dir_type != 'background':
                        dir_path= f'{self.main_dir}{self.camera_name}/{dir_type}'
                        print(dir_path)
                        dir_path_isexist = os.path.exists(dir_path)
                        if not dir_path_isexist:
                            os.makedirs(dir_path)
                            self.logger.info(msg=f"{dir_path} created")
                        else:
                            self.logger.info(msg=f"{dir_path} already exist")
                        return dir_path
                else:
                        background_path = f'{self.main_dir}{self.camera_name}/background'
                        print(background_path)
                        background_isexist = os.path.exists(background_path)
                        if not background_isexist:
                            os.makedirs(background_path)
                            #M change
                            black = np.uint8(np.zeros((256,256)))
                            for hour in range(24):
                                cv2.imwrite(f'{background_path}/weekly_background_hour_{hour}.jpg', black)
                                cv2.imwrite(f'{background_path}/daily_background_hour_{hour}.jpg', black)

                                out = cv2.VideoWriter(f'{background_path}/background_data_{hour}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 5, (256,256))
                                out.release()

                            self.logger.info(msg=f"Video file generated")
                            self.logger.info(msg=f"{background_path} created and background images created")
                        else:
                            self.logger.info(msg=f"{background_path} already exist")
                        return background_path
                
                
        elif dir_type=='Reference_images' or dir_type=='insight_report':
                dir_path= f'{self.main_dir}{dir_type}'
                dir_path_isexist=os.path.exists(dir_path)
                if not dir_path_isexist:
                    os.makedirs(dir_path)
                    self.logger.info(msg=f"{dir_path} created")
                else:
                    self.logger.info(msg=f"{dir_path} already exist")
                return dir_path               

    def load_database(self):
        """
        Connects to Database (MongoDB) using the provided connection string and stores unique chat IDs in resource collection

        Returns:
            Database: DATABASE
            Collection: COLLECTION_Meta, COLLECTION_Alerts, COLLECTION_Resource
        """
        try:
            conn = pymongo.MongoClient(
                self.config["DATABASE_CONNECTION"], directConnection=True)
            # Defining DB name
            print(conn)
            DATABASE = conn["Aksha"]
            COLLECTION_Meta = DATABASE[f"meta_{self.old_camera_name}"]
            print("Meta Collection (old cam name): ", self.old_camera_name)
            if self.camera_rename:
                try:
                    print("Rename meta Collection (new cam name): ", self.update_camera_name)
                    COLLECTION_Meta.rename(f"meta_{self.update_camera_name}")
                    COLLECTION_Meta = DATABASE[f"meta_{self.update_camera_name}"]
                    self.logger.info(msg="Renaming the existing DB collection.")
                except Exception as e:
                    self.logger.error(f"Error Renaming collection based on update_camera_name - {e}")
            COLLECTION_Alerts = DATABASE["Alerts"]
            COLLECTION_Resource = DATABASE["Resource"]
            self.logger.info(msg="Connected successfully to DB --- line !!!")
            self.logger.info(msg=f"Meta collection name returned by load_database function: {COLLECTION_Meta}")
            return DATABASE, COLLECTION_Meta, COLLECTION_Alerts, COLLECTION_Resource

        except Exception as e:
            self.logger.info(
                msg=f"Error connecting to MongoDB, please check the server, with exception", exc_info=True)
            return e


    def create_alerts_config_list(self, COLLECTION_Alerts):
        """
        Creates Alert Configurations based on "my_alerts"

        Returns:
            list: LIST_MYALERT_CONFIG, no_object_alert
            dict: previous_alert_statuses
        """        
        self.COLLECTION_Alerts = COLLECTION_Alerts
        if self.my_alerts.split() == None:
            self.LIST_MYALERT_CONFIG = []
            return self.LIST_MYALERT_CONFIG, self.previous_alert_statuses, self.no_object_alert
        else:
            for i in self.my_alerts.split():
                self.previous_alert_statuses["detection_alert"][str(i)] = {
                    "status": False, "count": 0}
                print(self.COLLECTION_Alerts.find_one({"Alert_Name": str(i)}))
                self.LIST_MYALERT_CONFIG.append(
                    self.COLLECTION_Alerts.find_one({"Alert_Name": str(i)}))
            # check if no object status is True for any alert
            for alert in self.LIST_MYALERT_CONFIG:
                if not alert["No_Object_Status"]:
                    alert_filter_result = {
                        "Alert_Name": alert["Alert_Name"],
                        "Display_Activation": alert["Display_Activation"],
                        "Workday": alert["Workday_Status"],
                        "Holiday": alert["Holiday_Status"],
                        "Start_Time": alert["Start_Time"],
                        "End_Time": alert["End_Time"],
                        "Filtered_Objects": None,
                        "Area_of_Interest": alert["Object_Area"],
                        "Email_Activation": alert["Email_Activation"],
                        "Alert_Description": alert["Alert_Description"]
                    }
                    self.previous_alert_statuses["no_object"][alert["Alert_Name"]] = {
                        "status": False, "count": 0}
                    self.no_object_alert.append(alert_filter_result)

            self.logger.info(f"alerts config list = {self.LIST_MYALERT_CONFIG}")
            return self.LIST_MYALERT_CONFIG, self.previous_alert_statuses, self.no_object_alert

    def read_video(self):
        """
        function for capturing video from cameras using rtsp links

        Returns:
            capture object: cap
        """        

        try:
            if self.video_path.isnumeric():
                self.cap = cv2.VideoCapture(int(self.video_path))
                self.logger.info(msg="video capture successfully")
            else:
                self.cap = cv2.VideoCapture(self.video_path)
                self.logger.info(msg="video capture successfully")

        except Exception as e:
            print("error reading video path")
            self.logger.info(msg=e)
        return self.cap

    def camera_configuration(self, DATABASE):
        """ Collects camera_configuration from the database.

        Returns:
            dict: camera_configuration
        """        
        try:
            self.DATABASE = DATABASE
            COLLECTION_Config = self.DATABASE["config"]
            camera_configuration = COLLECTION_Config.find_one(
                {"Camera_Name": self.camera_name})
            return camera_configuration
        except Exception as e:
            self.logger.info(
                msg=f'Reading camera configuration is getting issue from database with exception: {e}')
            return {}

    def notif_gdrive_folder_id(self):
        '''
        Gets the specific folder_id for respective client for sending whatsapp notifications.
        '''
        try:
            app_config = configparser.RawConfigParser()
            app_config.read(f"{self.main_dir}/app.config")
            details_dict = dict(app_config.items('Client_data'))
            
            if details_dict['app_id'] == self.config['UT_app_id']:
                return self.config['PARENT_ID_UT']
            if details_dict['app_id'] == self.config['Shaarda_app_id']:
                return self.config['PARENT_ID_SHAARDA']
            if details_dict['app_id'] == self.config['Aksha_team_app_id']:
                return self.config['PARENT_ID_AKSHA_TEAM']
            self.logger.info(
                msg=f"folder_id fetched successfully!!")
        except Exception as e:
            self.logger.info(
                msg=f"unable to get folder_id, failed with exception: {e} ")

    
        
    def notif_setup_email(self, COLLECTION_Resource):
        """
        Setup needed for sending notifications is configured here.

        Returns:
            (recipients, subscription) tuple
        """        

        try:
            self.COLLECTION_Resource = COLLECTION_Resource
            Resource_Data = self.COLLECTION_Resource.find_one()
            if Resource_Data is None:
                print("Resource_Data is None")
                return [], None
            else:
                recipients = Resource_Data.get("notification_email")
                subscription = Resource_Data.get("username")              
                return recipients, subscription

        except Exception as e:
            self.logger.info(
                msg=f"Connection to Resource Collection failed with exception: {e} ")
            return [], None


    def notif_setup_whatsapp(self, COLLECTION_Resource):
    

        try:
            self.COLLECTION_Resource = COLLECTION_Resource
            Resource_Data = self.COLLECTION_Resource.find_one()
            subscription = Resource_Data["username"]
            #contact_number = Resource_Data["contact_number"]
            

            if self.whats_app_service_status:
                try:
                    contact_number = Resource_Data["contact_number"]
                    whats_app_service = {"service_status": True, "contact_number": contact_number}
                    

                except Exception as e:
                    self.logger.info(
                        msg=f"Whats service is enabled, but contact number not found. Please add a contact number.")
                    whats_app_service = {
                        "service_status": False, "contact_number": None}
                return subscription, whats_app_service

            elif self.whats_app_service_status == False:
                whats_app_service = {
                    "service_status": False, "contact_number": None}
                return subscription, whats_app_service

            else:
                whats_app_service = {
                    "service_status": None, "contact_number": None}
                return subscription, whats_app_service

        except Exception as e:
            self.logger.info(
                msg=f"Connection to Resource Collection failed with exception: {e} ")
            return None, None

    def notif_setup_telegram(self, COLLECTION_Resource):
   

        try:
            self.COLLECTION_Resource = COLLECTION_Resource
            Resource_Data = self.COLLECTION_Resource.find_one()
            subscription = Resource_Data["username"]
            #chat_ids = Resource_Data["chat_ids"]

            if self.telegram_service_status:
                try:
                    chat_ids = Resource_Data["chat_ids"]
                    bot_token = Resource_Data["bot_token"]
                    telegram_service = {"service_status": True, "chat_ids": chat_ids, "bot_token": bot_token}
                    self.logger.info(msg=f"telegram_service : {telegram_service}")
                   
                except Exception as e:
                    self.logger.info(
                        msg=f"Telegram service is enabled ,but chat Ids or bot token not found, please add chat Id or bot token")
                    telegram_service = {
                        "service_status": False, "chat_ids": None, "bot_token": None}
                return subscription, telegram_service

            elif self.telegram_service_status == False:
                telegram_service = {
                    "service_status": False, "chat_ids": None, "bot_token": None}
                return subscription, telegram_service

            else:
                telegram_service = {
                    "service_status": None, "chat_ids": None, "bot_token": None}
                return subscription, telegram_service

        except Exception as e:
            self.logger.info(
                msg=f"Connection to Resource Collection failed with exception: {e} ")
            return None, None


    def gen_daily_bgImage(self, im_name, background_path):
        """
        to generate daily background image (every 5 minutes) and add frames into the background video file.

        Args:
            im_name (datetime.datetime): frame timestamp
            background_path: path for saving background frames
        """
        try:
            self.im_name = im_name
            self.background_path = background_path
            hour = self.im_name.hour
            # cv2.imwrite(f'{self.background_path}/daily_background_hour_{hour}.jpg',
            #             np.median(self.frames_background_gen[str(hour)][-30:], axis=0).astype(dtype=np.uint8))
            if not self.daily_frames_temp:
                cv2.imwrite(f'{background_path}/daily_background_hour_{hour}.jpg', np.median(self.daily_frames + self.daily_frames_temp[:-(30- len(self.daily_frames))], axis=0).astype(dtype=np.uint8) )
                self.logger.info(msg = f"Daily lengths are: daily{len(self.daily_frames)}, daily temp[:-30...] {self.daily_frames_temp[:-(30- len(self.daily_frames))]}")
            else:    
                cv2.imwrite(f'{background_path}/daily_background_hour_{hour}.jpg', np.median(self.daily_frames, axis=0).astype(dtype=np.uint8) )
                self.logger.info(msg = f"Daily lengths are: daily{len(self.daily_frames)}")

            if self.im_name.minute == 00 and self.im_name.second == 00:
                if self.im_name.hour == 00:
                    hour = 23
                else:
                    hour = self.im_name.hour - 1
                self.logger.info(
                    msg=f"Inside {hour}th hour")
                # if self.start_index[int(hour)][0] == 0:
                #     self.start_index[int(hour)][0] = len(self.frames_background_gen[str(hour)]) - self.start_index[int(hour)][1]
                
                # if len(self.frames_background_gen[str(hour)]) >= 210:
                #     self.start_index[int(hour)][1] = len(self.frames_background_gen[str(hour)]) - self.start_index[int(hour)][0]
                #     del self.frames_background_gen[str(hour)][:self.start_index[int(hour)][0]]
                #     self.start_index[int(hour)][0] = 0

                video = cv2.VideoCapture(f'{self.background_path}/background_data_{hour}.mp4')
                frames = []
                while(video.isOpened()):
                    ret, frame = video.read()
                    if ret == False:
                        break
                    frames.append(frame)
                if len(frames) >= 70:
                    del frames[:len(frames)-70]
                if len(self.daily_frames) < 10:
                    frames = frames + self.daily_frames
                else:
                    frames = frames + random.sample(self.daily_frames, 10)
                video.release()
                out = cv2.VideoWriter(f'{self.background_path}/background_data_{hour}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 5, (256,256))
                for j in frames:
                    out.write(j)
                out.release()

                cv2.imwrite(f'{self.background_path}/daily_background_hour_{hour}.jpg', np.median(self.daily_frames, axis=0).astype(dtype=np.uint8) )
                self.daily_frames_temp = self.daily_frames.copy()
                self.daily_frames.clear()


        except Exception as e:
            self.logger.info(
                msg=f"Daily background generation failed with exception: {e} ")

    def store_reference_image(self, frame, reference_img_path):
        """
        to store reference image to reference_img_path (at "9:00:00")

        Args:
            frame (numpy.ndarray): current frame
            reference_img_path: path for saving reference iamges
        """        
        try:
            self.frame = frame
            self.reference_img_path = reference_img_path
            ref_img = cv2.resize(
                self.frame, self.output_size)
            cv2.imwrite(
                f"{self.reference_img_path}/{self.rtsp_id}.jpg", ref_img)
            self.logger.info(
                msg="Reference image stored !!!")

        except Exception as e:
            print("Reference image storing error", e)

    def load_anomaly_models(self, ANOMALY_MODEL):
        """
        Loads the frame based and object based anomaly models as trained by the anomaly trainer module for a particular hour specified by the ANOMALY_MODEL variable.

        Args:
            ANOMALY_MODEL (int): used to fetch the model for the required hour.
        Returns:
            FRAME_BASED_ANOMALY_DETECTION_MODEL 
            OBJECT_BASED_ANOMALY_DETECTION_MODEL
        """        
        try:
            self.ANOMALY_MODEL = ANOMALY_MODEL
            # Defining path to the Anomaly Models hour wise.
            frame_object_paths = {
                'frame': f"{self.main_dir}{self.camera_name}/anomaly_models/framebase/{self.ANOMALY_MODEL}.pkl",
                'object': f"{self.main_dir}{self.camera_name}/anomaly_models/objectbase/{self.ANOMALY_MODEL}.pkl"
            }

            for key, path in frame_object_paths.items():
                if os.path.exists(path):
                    # Load anomaly detection model for current hour.
                    if key == 'frame':
                        FRAME_BASED_ANOMALY_DETECTION_MODEL = joblib.load(path)
                        print("Framebased anomaly base model loaded")
                        self.logger.info(msg="Frame based anomaly model loaded")
                    else:
                        OBJECT_BASED_ANOMALY_DETECTION_MODEL = joblib.load(path)
                        print("Object anomaly base model loaded")
                        self.logger.warning("Object based anomaly model loaded")
                else:
                    if key == 'frame':
                        FRAME_BASED_ANOMALY_DETECTION_MODEL = False
                        print("Frame based anomaly model does not exist")
                        self.logger.info(msg="Frame based anomaly model does not exist")
                    else:
                        OBJECT_BASED_ANOMALY_DETECTION_MODEL = False
                        print("Object based anomaly model doesn't exist")
                        self.logger.warning("Object based anomaly model doesn't exist")

            return FRAME_BASED_ANOMALY_DETECTION_MODEL, OBJECT_BASED_ANOMALY_DETECTION_MODEL

        except Exception as e:
            self.logger.exception(f'Anomaly model loading issue {e}')
            return False, False
        
    def create_foregroundImg_path(self, foreground_path, ANOMALY_MODEL, im_name):
        """
        to create forground image path for storing foreground images as per date and hour

        Args:
            foreground_path (str): generic foreground image path ("Aksha-test/test_cam/foreground")
            ANOMALY_MODEL (int): used to create folder for that hour
            im_name (datetime.datetime) : to create folders according to dates

        Returns:
            str: foreground_image_path ("Aksha/cam_501/foreground/2023-05-09/14")
        """        
        self.foreground_path = foreground_path
        self.ANOMALY_MODEL = ANOMALY_MODEL
        self.im_name = im_name
        foreground_image_path = f'{self.foreground_path}/{str(self.im_name.strftime("%Y-%m-%d"))}/{self.ANOMALY_MODEL}'
        os.makedirs(foreground_image_path, exist_ok=True)
        
        return foreground_image_path


class AnomalyDetector():   

    def __init__(self, background_path, im_name, frame, foreground_image_path, prefilter_threshold, object_detection_service,
                class_names, colors, FRAME_BASED_ANOMALY_DETECTION_MODEL, OBJECT_BASED_ANOMALY_DETECTION_MODEL, logger):
        """
        This class take care of framebased anomaly prediction, object detection and objectbased anomaly prediction.

        Args:
            background_path (str): path to weekly/daily background frames
            im_name (datetime.datetime): timestamp for the current frame
            frame (numpy.ndarray): current frame
            foreground_image_path (str): path for saving the generated foreground image
            prefilter_threshold: threshold for deciding if the frame should be sent to model for prediction
            FRAME_BASED_ANOMALY_DETECTION_MODEL (pkl file): used for framebased anomaly prediction
            OBJECT_BASED_ANOMALY_DETECTION_MODEL (pkl file): used for objectbased anomaly prediction

        """ 
        self.background_path = background_path
        self.im_name = im_name
        self.frame = frame
        self.foreground_image_path = foreground_image_path
        self.prefilter_threshold = prefilter_threshold
        self.object_detection_service = object_detection_service
        self.class_names = class_names
        self.colors = colors
        self.FRAME_BASED_ANOMALY_DETECTION_MODEL = FRAME_BASED_ANOMALY_DETECTION_MODEL
        self.OBJECT_BASED_ANOMALY_DETECTION_MODEL = OBJECT_BASED_ANOMALY_DETECTION_MODEL
        self.logger = logger
        self.frame_anomaly_status = False

    def frame_based_pred(self):
        """
        this method creates a foreground image by passing the current frame, respective weekly_background_frame and respective daily_background_frame
        to the prefilter module and gives anomaly prediction using the already loaded framebased model.

        Returns:
            frame_anomaly_status (bool): True if frame is anomalous according to the model
            overlay (numpy.ndarray): overlay frame generated by the prefilter module 

        """

        try:
            self.logger.info(msg="Prefilter starting...")
            weekly_background_image = cv2.resize(
                cv2.imread(f'{self.background_path}/weekly_background_hour_{self.im_name.hour}.jpg', 0),
                (256,256))
            daily_background_image = cv2.resize(
                cv2.imread(f'{self.background_path}/daily_background_hour_{self.im_name.hour}.jpg', 0),
                (256,256))
            print(f"{self.frame.shape}, {weekly_background_image.shape}")   
                         
            foreground, overlay, ssim = prefilter.extract_foreground(cv2.resize(self.frame, (256,256)), weekly_background_image,
                                                                          daily_background_image)
            # print("ssim", ssim)
            # diff_save = cv2.resize(diff, args.output_size)
            cv2.imwrite(
                f'{self.foreground_image_path}/{str(self.im_name)}.jpg', foreground)
            # cv2.imwrite(f'{alert_path}/{str(im_name)}_overlay.jpg',overlay)

            foreground_flattened = np.expand_dims(
                foreground.flatten(), axis=0)
            if self.FRAME_BASED_ANOMALY_DETECTION_MODEL:
                try:
                    # print(
                    #     "In Anomaly Detection..")
                    frame_anomaly_prediction = self.FRAME_BASED_ANOMALY_DETECTION_MODEL.predict(foreground_flattened)[
                        0]
                    self.logger.info(
                        msg=f'frame based anomaly result is {frame_anomaly_prediction}')
                    # print(
                    #     f"predicted framebased anoamly is {frame_anomaly_prediction}")
                    if frame_anomaly_prediction == -1:
                        self.frame_anomaly_status = True
                    else:
                        self.frame_anomaly_status = False
                except Exception as e:
                    self.logger.info(
                        msg=f"Model unable to predict : {e}")

            return self.frame_anomaly_status, overlay #, skip_frame

        except Exception as e:
            # print("prefilter issue")
            self.logger.info(
                msg=f"frame unable to capture with error code: {e}")
            return False, False # False  # (frame_anomaly_status, overlay, skip_frame)

    def object_based_pred(self):
        """
        this method applies object detection as well as object based anomaly prediction on the current frame

        Returns:
            object_detection_results (list): list of objects detected in the frame
            object_anomaly_status (bool): represents if the frame is anomalous according to object based model
            classes (list): list of all clasess as per custom trained yolo model

        """

        try:
            boxes, confs, class_ids, classes = od.object_detection(self.frame, self.object_detection_service, self.class_names, self.colors)
            print("Proceed to get labels on co-ordinate...")

        except Exception as e:
            self.logger.info(
                msg=f"problem in yolo v7 {e} ")

        try:
            object_detection_results = od.get_labels(
                boxes, confs, class_ids, classes)
            print("get object cordinates are ",
                  object_detection_results)

        except Exception as e:
            print(f"get object error {e}")
            self.logger.info(msg=e)

        if object_detection_results:
            object_anomaly_status = False
            try:
                object_anomaly_preprocessed_data = dp.data_preprocess_object_based_anomaly(
                    classes, self.im_name, object_detection_results)
                print("object base data is:",
                      object_anomaly_preprocessed_data)

                if self.OBJECT_BASED_ANOMALY_DETECTION_MODEL:

                    object_anomaly_prediction = self.OBJECT_BASED_ANOMALY_DETECTION_MODEL.predict(
                        object_anomaly_preprocessed_data)[0]
                    print(
                        f"predicted object based anomaly is {object_anomaly_prediction}")
                    self.logger.info(
                        msg=f'object based anomaly result is {object_anomaly_prediction}')
                    if object_anomaly_prediction == -1:
                        object_anomaly_status = True
                    print(
                        f"predicted object based anomaly status is {object_anomaly_status}")

            except Exception as e:
                print(
                    "Object based anomaly is facing issue...")
                self.logger.info(
                    msg=f"Object based anomaly model facing the issue : {e}")

            return object_detection_results, object_anomaly_status, classes
        else:
            return object_detection_results, False, classes


class PostPrediction:

    def __init__(self, im_name, frame, LIST_MYALERT_CONFIG, object_detection_results, no_object_alert,
                 frame_anomaly_status, object_anomaly_status, frame_path, COLLECTION_Meta, logger, crowd_threshold):
        
        """
        this class takes care of selecting appropriate alerts according to the object dectection results 
        and user-defined alerts using the my_alert_filters module and pushes the frame metadata to the respective 
        camera collection in Aksha database in mongodb.

        Args:
            im_name (datetime.datetime): timestamp for the current frame
            frame (numpy.ndarray): current frame
            LIST_MYALERT_CONFIG (list): List of alerts as per the my_alerts argument
            object_detection_results (list): list of objects detected in the frame
            no_object_alert (list): list of alerts defined for no_object functionality
            frame_anomaly_status (bool): represents if frame is anomalous according to the framebased model
            object_anomaly_status (bool): represents if the frame is anomalous according to object based model
            frame_path (str): path for saving the frames to the "frame" folder in Aksha directory
            COLLECTION_Meta (COLLECTION): collection for the respective camera inside Aksha database
            logger (logging.RootLogger): logger for maintaing logs

        Returns:
            alert_results (list): selected alerts according to my_alert_filters
            alert_result_config (list): configuration of selected alerts
            self.no_object_status  (bool): Boolean representing if No_object_status is valid for the current frame
            alert_description (list): Description of selected alerts
            alert_notification_validity (list): list of boolean values representing email activation status for selected alerts

        """
        self.im_name = im_name
        self.frame = frame
        self.LIST_MYALERT_CONFIG = LIST_MYALERT_CONFIG
        self.object_detection_results = object_detection_results
        self.no_object_alert = no_object_alert
        self.frame_anomaly_status = frame_anomaly_status
        self.object_anomaly_status = object_anomaly_status
        self.frame_path = frame_path
        self.COLLECTION_Meta = COLLECTION_Meta
        self.logger = logger
        self.no_object_status = False
        self.crowd_threshold = crowd_threshold

    def filter(self):

        try:
            if self.object_detection_results:

                noobj_alert_result_config = []
                if self.LIST_MYALERT_CONFIG:

                    alert_results, alert_result_config, self.no_object_status = maf.apply_filter(
                        self.LIST_MYALERT_CONFIG, self.object_detection_results, self.crowd_threshold)
                    alert_description = []
                    alert_notification_validity = []
                    if len(alert_result_config) > 0:
                        
                        for i in alert_result_config:
                            alert_description.append(
                                i['Alert_Description'])
                            alert_notification_validity.append(
                                i['Email_Activation'])

                    self.logger.info(
                        msg=f'maf.apply_filer() processed: {alert_results} and config is  {alert_result_config}')

                else:
                    alert_results = []
                    alert_result_config = []
                    alert_description = []
                    alert_notification_validity = []

                    self.logger.info(
                        msg=f'No Alert applicable! ')

                self.write_frame(alert_results)

                return alert_results, alert_result_config, self.no_object_status, alert_description, alert_notification_validity, noobj_alert_result_config

            else:
                alert_results = []
                alert_result_config = []
                alert_description = []
                alert_notification_validity = []
                noobj_alert_result_config = []
                filtered_objects = []
                if self.no_object_alert:
                    self.no_object_status = False
                    for i in self.no_object_alert:
                        # print(dt.datetime.strptime(i["Start_Time"], '%H:%M').time() < dt.datetime.now().time() < dt.datetime.strptime(i["End_Time"], '%H:%M').time())
                        if (dt.datetime.strptime(i["Start_Time"], '%H:%M').time() < dt.datetime.now().time() < dt.datetime.strptime(i["End_Time"], '%H:%M').time()):
                            alert_results.append(
                                i["Alert_Name"])
                            alert_description.append(
                                i['Alert_Description'])
                            alert_notification_validity.append(
                                i['Email_Activation'])
                            alert_filter_result = {
                                                    "Alert_Name": i["Alert_Name"], 
                                                    "Display_Activation": i["Display_Activation"],
                                                    "Workday": i["Workday"], 
                                                    "Holiday": i["Holiday"],
                                                    "Filtered_Objects": filtered_objects,
                                                    "Area_of_Interest": i["Area_of_Interest"],
                                                    "Email_Activation":i["Email_Activation"],
                                                    "Alert_Description":i["Alert_Description"]
                                                    }
                            noobj_alert_result_config.append(alert_filter_result)
                            self.no_object_status = True

                self.logger.info(
                    msg="No object detected in frame")
                self.write_frame(alert_results)
                return alert_results, alert_result_config, self.no_object_status, alert_description, alert_notification_validity, noobj_alert_result_config

        except Exception as e:
            self.logger.info(
                msg=f'maf.apply_filer() function failed with exception : {e}')

    def write_frame(self, alert_results):
        """
        write result meta_data to the camera collection in Aksha Database inside mongodb.

        Args:
            alert_results (list): selected alerts according to my_alert_filters
        """

        self.alert_results = alert_results

        try:
            
            result_meta = {"Timestamp": self.im_name, "Results": self.object_detection_results,
                        "No_Object_Status": self.no_object_status, "Frame_Anomaly": self.frame_anomaly_status,
                        "Object_Anomaly": self.object_anomaly_status, "Alerts": self.alert_results}
            
            # print(result_meta)
            self.logger.info(
                msg=f'Result metadata is: {result_meta}')
            
        except Exception as e:
            print("frame saving error ", e)
            self.logger.info(msg=e)

        if self.object_detection_results or self.frame_anomaly_status or self.object_anomaly_status:
            try:
                self.COLLECTION_Meta.insert_one(
                    result_meta)
                print(
                    "record inserted successfully")
            except Exception as e:
                print(f"Mongo db Error, {e}")


class FrameAnnotation:

    def __init__(self, im_name, frame, no_object_status, alert_result_config, noobj_alert_result_config, frame_anomaly_status,
                 overlay, object_anomaly_status, object_detection_results, classes, live_path, logger):
        """
        This Class takes care of Annotating the frames by writing text and drawing boxes around detected objects (if any)
        and generates 3 frames namely result_img, workday_img & holiday_img, and classifies the frame into respective alert_type.

        Args:
            im_name (datetime.datetime): timestamp for the current frame
            frame (numpy.ndarray): current frame
            no_object_status  (bool): Boolean representing if No_object_status is valid for the current frame
            alert_result_config (list): configuration of selected alerts
            noobj_alert_result_config (list): list of filtered no object alerts defined for no_object functionality
            frame_anomaly_status (bool): represents if frame is anomalous according to the framebased model
            overlay (numpy.ndarray): overlay frame generated by the prefilter module 
            object_anomaly_status (bool): represents if the frame is anomalous according to object based model
            object_detection_results (list): list of objects detected in the frame
            classes (list): list of all clasess as per custom trained yolo model
            live_path (str): path to the live folder in Aksha Directory
            logger (logging.RootLogger): logger for maintaing logs

        """
        self.im_name = im_name
        self.frame = frame
        self.no_object_status = no_object_status
        self.alert_result_config = alert_result_config
        self.noobj_alert_result_config = noobj_alert_result_config
        self.frame_anomaly_status = frame_anomaly_status
        self.overlay = overlay
        self.object_anomaly_status = object_anomaly_status
        self.object_detection_results = object_detection_results
        self.classes = classes
        self.live_path = live_path
        self.logger = logger

    def frame_prep(self):
        """
        Frames classified into alerts by priority : No_Object_Status > Alert_result_config > frame_anomaly_status > object_anomaly_status
        Annotation performed on the frame according to the alert_result_config/ no_object_alert by using draw_filter function from my_alert_filter module

        Returns:
            check (bool): represents the alert type to which the current frame belongs
            result_img (numpy.ndarray): annotated frame
            workday_img (numpy.ndarray): annotated frame
            holiday_img (numpy.ndarray): annotated frame
            frame_anomaly_validity (bool): True if frame is classified as auto_alert using frame_anomaly_status
            object_anomaly_validity (bool): True if frame is classified as auto_alert using object_anomaly_status
        """
        frame_anomaly_validity = False
        object_anomaly_validity = False
        if self.no_object_status:
            check = "no_object"
            result_img = self.frame.copy()

            try:
                # self.logger.info(msg=f'Workday filter maf.draw_filter() function failed with exception {result}')
                if self.alert_result_config:
                    result_img, workday_img, holiday_img = maf.draw_filter(
                        self.alert_result_config, result_img, check)
                else:
                    try:
                        result_img, workday_img, holiday_img = maf.draw_filter(
                            self.noobj_alert_result_config, result_img, check)
                    except Exception as e:
                        self.logger.info(
                            msg=f'No detection, {e}')

            except Exception as e:
                self.logger.info(
                    msg=f'No Object Alert filter maf.draw_filter() function failed with exception {e}')

        elif len(self.alert_result_config) > 0:
            check = "my_alert"
            result_img = self.frame.copy()

            try:
                # self.logger.info(msg=f'Workday filter maf.draw_filter() function failed with exception {result}')
                result_img, workday_img, holiday_img = maf.draw_filter(
                    self.alert_result_config, result_img, check)

            except Exception as e:
                self.logger.info(
                    msg=f'Alert filter maf.draw_filter() function failed with exception {e}')

        elif self.frame_anomaly_status:
            frame_anomaly_validity = True
            check = "auto_alert"
            overlay_img = self.overlay.copy()
            font = cv2.FONT_HERSHEY_PLAIN
            points=np.array([[650,0],[650,50],[600,0]])
            cv2.fillPoly(
                overlay_img, pts=[points], color=(0,197,255))
            result_img = overlay_img.copy()
            workday_img = overlay_img.copy()
            holiday_img = overlay_img.copy()
            self.logger.info(
                msg=f"Frame based anomaly occured in the image for timestamp: {str(self.im_name)}")
            print(f"Frame based anomaly found")

        elif self.object_anomaly_status:
            if self.object_detection_results:
                object_anomaly_validity = True
                check = "auto_alert"
                result_img = od.draw_labels(
                    self.frame, self.object_detection_results, self.classes, self.live_path)
                workday_img = result_img.copy()
                holiday_img = result_img.copy()
                self.logger.info(
                    msg=f"Object Based Anomaly occured in the image for timestamp: {str(self.im_name)}")
                print(f"Object based Anomaly Found")
        else:
            check = "no_alert"
            result_img = self.frame.copy()
            workday_img = self.frame.copy()
            holiday_img = self.frame.copy()
            self.logger.info(
                msg=f"Image stored in Live with name latest with timestamp: {str(self.im_name)}")
            print(
                f"frame saved successfully at live latest.jpg")

        return check, result_img, workday_img, holiday_img, frame_anomaly_validity, object_anomaly_validity


class Notify:

    def __init__(self, check, im_name, frame, result_img, workday_img, holiday_img, camera_name, main_dir,
                 frame_anomaly_status, object_anomaly_status, no_object_status, alert_results, alert_description,
                 alert_notification_validity,
                 previous_alert_statuses, skip_fps_sec, alert_path, frame_path, live_path, spotlight_path,
                 recipients, subscription, whats_app_service, telegram_service, config, email_autoalert,
                 camera_configuration, prev_spotlight, object_detection_results, folder_id, autoalert_display, email_alert, alert_display, logger):
        """
        Applies postFilter logic to control the number of notifications sent to the user using postfilter & notication modules.
        Also writes the frames to the respective folders and also updates spotlight frame (given that no alert is generated for the frame)

        Args:
            check (bool): represents the alert type to which the current frame belongs
            im_name (datetime.datetime): timestamp for the current frame
            frame (numpy.ndarray): current frame
            result_img (numpy.ndarray): annotated frame
            workday_img (numpy.ndarray): annotated frame
            holiday_img (numpy.ndarray): annotated frame
            camera_name (str): name of the respective camera
            main_dir (str): Aksha Directory path
            frame_anomaly_status (bool): represents if frame is anomalous according to the framebased model
            object_anomaly_status (bool): represents if the frame is anomalous according to object based model
            no_object_status (bool): Boolean representing if No_object_status is valid for the current frame
            alert_results (list): selected alerts according to my_alert_filters
            alert_description (list): Description of selected alerts
            alert_notification_validity (list): list of boolean values representing email activation status for selected alerts
            previous_alert_statuses (dict): dictionary maintained across consequtive frames to remeber the details about alerts detected in previous frames 
            skip_fps_sec (int): used for calulating the number of frames to be skipped before capturing next frame
            alert_path (str): path to the alert folder in Aksha Directory for the respective camera
            frame_path (str): path to the frame folder in Aksha Directory for the respective camera
            live_path (str): path to the live folder in Aksha Directory for the respective camera
            spotlight_path (str):  path to the spotlight folder in Aksha Directory for the respective camera
            recipients (list): list of email-ids to send notification
            subscription (list): list of usernames
            whats_app_service (dict): dictionary representing whatsapp service status for user phone-numbers
            config (dict): dictionary loaded from environment files that has mongodb connection string and azure blob storage SAS URL.
            email_autoalert (bool): Enable notification service for Autoalerts
            camera_configuration (dict): dictionary specifying respective camera's configuration
            prev_spotlight (bool): boolean specifying if the previous spotlight frame is present or not.
            object_detection_results: used for saving frames with detected objects in the basic state(no alert, no anomaly)
            logger (logging.RootLogger): logger for maintaing logs

        """

        self.check = check
        self.im_name = im_name
        self.frame = frame
        self.result_img = result_img
        self.workday_img = workday_img
        self.holiday_img = holiday_img
        self.camera_name = camera_name
        self.main_dir = main_dir
        self.frame_anomaly_status = frame_anomaly_status
        self.object_anomaly_status = object_anomaly_status
        self.no_object_status = no_object_status
        self.alert_results = alert_results
        self.alert_description = alert_description
        self.alert_notification_validity = alert_notification_validity
        self.previous_alert_statuses = previous_alert_statuses
        self.skip_fps_sec = skip_fps_sec
        self.alert_path = alert_path
        self.frame_path = frame_path
        self.live_path = live_path
        self.spotlight_path = spotlight_path
        self.recipients = recipients
        self.subscription = subscription
        self.whats_app_service = whats_app_service
        self.telegram_service = telegram_service
        self.config = config
        self.email_autoalert = email_autoalert
        self.camera_configuration = camera_configuration
        self.prev_spotlight = prev_spotlight
        self.object_detection_results = object_detection_results
        self.folder_id = folder_id
        self.autoalert_display = autoalert_display
        self.email_alert = email_alert
        self.alert_display = alert_display
        self.logger = logger

    def classify(self):

        """
        This method applies the postfilter logic, then saves the frames to respective paths and
        sends notification to the user email-ids and phone-numbers.

        Returns:
            frame_anomaly_validity (bool): boolean value after applying postfilter logic
            object_anomaly_validity (bool): boolean value after applying postfilter logic 
            alert_validity (list): list of boolean values for user-defined alerts for the respective camera 
            no_object_validity (list): list of boolean values for alerts with no-object functionality
            previous_alert_statuses (dict): dictionary maintained across consequtive frames to remeber the details about alerts detected in previous frames 
            prev_spotlight (bool): boolean specifying if the previous spotlight frame is present or not

        """

        try:
            frame_anomaly_validity, object_anomaly_validity, alert_validity, no_object_validity, previous_alert_statuses = postfilter.email_status_check(
                self.frame_anomaly_status, self.object_anomaly_status, self.no_object_status, self.alert_results,
                self.previous_alert_statuses, self.skip_fps_sec)
        except Exception as e:
            self.logger.info(
                msg=f'Postfilter failed {e}')

        if self.check == "no_object":
            cv2.imwrite(
                f'{self.alert_path}/{str(self.im_name)}_alert.jpg', self.result_img)
            self.logger.info(
                msg=f"Current alert (no object) image stored in alert folder with name {str(self.im_name)}_alert.jpg!")
            cv2.imwrite(
                f'{self.frame_path}/{str(self.im_name)}.jpg', self.frame)
            cv2.imwrite(
                f'{self.live_path}/workday.jpg', self.workday_img)
            self.logger.info(
                msg=f"Current workday filter image stored in live folder")
            cv2.imwrite(
                f'{self.live_path}/holiday.jpg', self.holiday_img)
            self.logger.info(
                msg=f"Current holiday image stored in live folder")
            cv2.imwrite(
                f'{self.spotlight_path}/workday.jpg', self.workday_img)
            self.logger.info(
                msg=f"Current spotlight workday images stored in spotlight folder")
            cv2.imwrite(
                f'{self.spotlight_path}/holiday.jpg', self.holiday_img)
            self.logger.info(
                msg=f"Current spotlight holiday images stored in spotlight folder")
            if True in no_object_validity and len(self.recipients) > 0:
                notification_result = notification.send(self.subscription, self.recipients, self.camera_name,
                                                        "No Object Alert", self.main_dir, str(
                        self.im_name), self.config["SAS_URL"], self.folder_id, no_object_validity, self.alert_results, self.alert_description,
                                                        self.whats_app_service, self.telegram_service)
                self.logger.info(
                    msg=f"Alert notification_result: {notification_result}")
            prev_spotlight = True
 
        elif self.check == "my_alert":
            self.logger.info(
                msg=f"Val lists:{self.alert_notification_validity},{alert_validity}")

            for i in range(len(self.alert_notification_validity)):
                if alert_validity[i] and self.alert_notification_validity[i]:
                    self.alert_notification_validity[i] = True
                else:
                    self.alert_notification_validity[i] = False
            cv2.imwrite(
                f'{self.alert_path}/{str(self.im_name)}_alert.jpg', self.result_img)
            self.logger.info(
                msg=f"Current alert image stored in alert folder with name {str(self.im_name)}_alert.jpg!")
            cv2.imwrite(
                f'{self.frame_path}/{str(self.im_name)}.jpg', self.frame)
            if self.alert_display:
                cv2.imwrite(
                    f'{self.live_path}/workday.jpg', self.workday_img)
                cv2.imwrite(
                    f'{self.live_path}/holiday.jpg', self.holiday_img)
                self.logger.info(
                    msg=f"Current image stored in live folder (alert_display ON): {str(self.im_name)}")
            else:
                cv2.imwrite(
                    f'{self.live_path}/workday.jpg', self.frame)
                cv2.imwrite(
                    f'{self.live_path}/holiday.jpg', self.frame)
                self.logger.info(
                    msg=f"Current image(raw frame) stored in live folder (alert_display OFF) : {str(self.im_name)}")
            cv2.imwrite(
                f'{self.spotlight_path}/workday.jpg', self.workday_img)
            self.logger.info(
                msg=f"Current spotlight workday images stored in spotlight folder")
            cv2.imwrite(
                f'{self.spotlight_path}/holiday.jpg', self.holiday_img)
            self.logger.info(
                msg=f"Current spotlight holiday images stored in spotlight folder")
            if self.email_alert and True in self.alert_notification_validity and len(self.recipients) > 0:
                notification_result = notification.send(self.subscription, self.recipients, self.camera_name, "Alert",
                                                        self.main_dir, str(
                        self.im_name), self.config["SAS_URL"], self.folder_id, self.alert_notification_validity, self.alert_results, self.alert_description,
                                                        self.whats_app_service, self.telegram_service)
                self.logger.info(
                    msg=f"Alert notification_result: {notification_result}")
            prev_spotlight = True
            
            
        elif self.check == "auto_alert":
            cv2.imwrite(
                f'{self.alert_path}/{str(self.im_name)}_autoalert.jpg', self.result_img)
            self.logger.info(
                msg=f"Current autoalert image stored in alert folder with name {str(self.im_name)}_autoalert.jpg!")
            cv2.imwrite(
                f'{self.frame_path}/{str(self.im_name)}.jpg', self.frame)
            if self.autoalert_display:
                cv2.imwrite(
                    f'{self.live_path}/workday.jpg', self.result_img)
                cv2.imwrite(
                    f'{self.live_path}/holiday.jpg', self.result_img)
                self.logger.info(
                    msg=f"Current image stored in live folder (autoalert_display ON): {str(self.im_name)}")
            else:
                cv2.imwrite(
                    f'{self.live_path}/workday.jpg', self.frame)
                cv2.imwrite(
                    f'{self.live_path}/holiday.jpg', self.frame)
                self.logger.info(
                    msg=f"Current image(raw frame) stored in live folder (autoalert_display OFF): {str(self.im_name)}")
            cv2.imwrite(
                f'{self.spotlight_path}/workday.jpg', self.result_img)
            cv2.imwrite(
                f'{self.spotlight_path}/holiday.jpg', self.result_img)
            self.logger.info(
                msg=f"Current spotlight images for workday and holiday are stored in spotlight folder")
            if self.email_autoalert and self.camera_configuration["Email_Auto_Alert"] and len(
                    self.recipients) > 0 and ((object_anomaly_validity and self.object_anomaly_status) or (
                    frame_anomaly_validity and self.frame_anomaly_status)):
                notification_result = notification.send(
                    self.subscription, self.recipients, self.camera_name, "AutoAlert", self.main_dir, str(self.im_name),self.config["SAS_URL"], self.folder_id,
                    self.whats_app_service, self.telegram_service)
                self.logger.info(
                    msg=f"Autoalert notification_result: {notification_result}")
            prev_spotlight = True

            
        else:
            if self.prev_spotlight:
                try:
                    if os.path.exists(f'{self.spotlight_path}/workday.jpg'):
                        os.remove(
                            f'{self.spotlight_path}/workday.jpg')
                except Exception as e:
                    self.logger.info(
                        msg=f"no file found {e}")
                try:
                    if os.path.exists(f'{self.spotlight_path}/holiday.jpg'):
                        os.remove(
                            f'{self.spotlight_path}/holiday.jpg')
                except Exception as e:
                    self.logger.info(
                        msg=f"no file found {e}")

                prev_spotlight = False
            else:
                prev_spotlight = False

            self.logger.info(
                msg=f"*****No spotlight detected for timestamp: {str(self.im_name)}, old spotlight removed form spotlight folder*****")
            cv2.imwrite(
                f'{self.live_path}/workday.jpg', self.result_img)
            cv2.imwrite(
                f'{self.live_path}/holiday.jpg', self.result_img)
            cv2.imwrite(
                f'{self.frame_path}/{str(self.im_name)}.jpg', self.frame)
            self.logger.info(
                    msg=f"*Current frame stored in frame folder*")
            self.logger.info(
                msg=f"Current workday and holiday image stored in live folder")

        return frame_anomaly_validity, object_anomaly_validity, alert_validity, no_object_validity, previous_alert_statuses, prev_spotlight
