from datetime import timedelta
import datetime
import frame_based_anomaly
import object_based_anomaly
import insight_report as ir
import pymongo
import logging 
import time

import argparse
import os
import cv2
import numpy as np
import timeit
import json

parser = argparse.ArgumentParser()
parser.add_argument('--time_delta', help="Please enter deletion data retention period in days.", type=int, default=10)
args = parser.parse_args()

def get_camera_list():
    try:
        camera_names=db.config.distinct("Camera_Name")
        print(camera_names)
        logger.info(msg=f"Inside get_camera_list: Fetched camera list successfully, camera list: {camera_names}")
        return(camera_names)
    except Exception as e:
        logger.info(msg=f"Inside get_camera_list: following error occured: {e}")
    

def init_gen_insight_report(aksha_path, db, logger):
    try:
        cameras= get_camera_list()
        alert_list= db.Alerts.distinct("Alert_Name")
        # cameras=[]
        if len(cameras) != 0 and len(alert_list) != 0:
            ir.generate_insight_report(aksha_path, cameras, db, logger)
            logger.info(msg=f"Inside init_gen_insight_report: Report generated succesfully")
        else:
            pass 
        
    except Exception as e:
        logger.info(msg=f"Inside init_gen_insight_report: following error occured: {e}")
    
def anomaly_models_training(aksha_path, start_hour, db, time_delta):

    try: 
        camera_names=get_camera_list()
        # print(camera_names)
        logger.info(msg=f"Mongo DB established connection")
        #calling training function for each camera
        for camera_name in camera_names:
            
            logger.info(msg=f'Anomaly model for : {camera_name}')
            print("training for", camera_name)
            print("for frame based")
            try:
                frame_anomaly_model_status = frame_based_anomaly.train_IF_model(aksha_path, camera_name, anomaly_percent, start_hour)
                logger.info(msg=str(frame_anomaly_model_status))
            except Exception as e:
                 print(f"Error in building frame based anomaly model {e}")
                 logger.info(msg=f'frame based anomaly model : {e}')
            print("for object based")
            try:
                object_anomaly_model_status =object_based_anomaly.train_IF_object_based_model(aksha_path, camera_name, anomaly_percent, start_hour,db)
                logger.info(msg=str(object_anomaly_model_status))
            except Exception as e:
                 print(f"Error in building object based anomaly model {e}")
                 logger.info(msg=f'object based anomaly model : {e}')
            
    except Exception as e:
        logger.info(msg=f'anomaly model trainer failed: {e}')




if __name__=="__main__":
       
    
    while True:
        # aksha_path = "/home/aapl19/Aksha/AkshaV2-Alpha-UIUX/backend/Aksha"
        aksha_path = "Aksha"
        isexist = os.path.exists(aksha_path)
        print(isexist)
        if not isexist:
            os.makedirs(aksha_path)
            print(f"{aksha_path} created")
        else:
            print(f"{aksha_path} allready exist")
        logging.basicConfig(filename=f"{aksha_path}/anomaly-model-training.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)
        logger = logging.getLogger()
        try:
            # conn = pymongo.MongoClient("mongodb://172.18.0.2:27017/") # Uncomment this line for testing on development system
            # conn = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/Aksha?authSource=admin&tls=false", directConnection=True)
            conn = pymongo.MongoClient("mongodb://mongo:mongo@mongodb:27017/Aksha?authSource=admin&tls=false", directConnection=True) # Uncomment this line for running in production/docker network
            #Defining DB name 
            print(conn)
            db = conn["Aksha"]
            db.create_collection("Resource")

            logger.info(msg=f'Database connected successfully')
        except Exception as e:
            logger.info(msg=f'Database connection failed: {e}')

        #anomaly_percentage_value (contamination in IF model)
        anomaly_percent = 0.005

        # model training function
        while True:
            current_time = datetime.datetime.now()
            model_training_time = current_time-timedelta(hours=1)
            if current_time.minute == 00:

                try:
                    if current_time.hour == 00:
                        frame_based_anomaly.gen_weekly_bgImage(aksha_path, db, logger)
                        ir.del_insight_report(aksha_path, args.time_delta)
                        
                    init_gen_insight_report(aksha_path, db, logger)
                    anomaly_models_training(aksha_path, model_training_time.hour, db, args.time_delta)
                    logger.info(msg=f"Model for {model_training_time.hour} th hour for date {datetime.datetime.now()+timedelta(days=1)}  has trained and saved successfully")
                    new_time = datetime.datetime.now()
                    model_training_schedule = 60 - new_time.minute
                    print(model_training_schedule)
                    time.sleep(model_training_schedule*60)
                except Exception as e:
                    logger.info(msg=f" Unexpected exception has occurred: {e}")
                    print(e)
            else:
                continue
            
