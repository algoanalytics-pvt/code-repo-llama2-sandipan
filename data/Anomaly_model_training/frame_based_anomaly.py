
#external imports
from datetime import date
from datetime import timedelta
import datetime
from sklearn.ensemble import IsolationForest
import pickle
import os
import glob
import cv2
import numpy as np
import random

#Directory stucture for foreground frames - ../output/{camera_name}/foreground/{date}/{hour}/"%Y-%m-%d %H:%M:%S.jpg"

# Get training frames for the given start_hour,end_hour and camera_name
def get_training_frames(aksha_path, start_hour, n_days, camera_name):
    print("gettin frames")
    # SAVING_FOLDER = "Aksha" 
    SAVING_FOLDER = aksha_path 
    frames_list = list() #output list for training frames
    current_date = date.today()-timedelta(days=1) #current date
    
    for diff in range(0, n_days + 1):
        target_date = current_date - timedelta(diff)
        search_path = "{}/{}/foreground/{}/{}/*.jpg".format(
            SAVING_FOLDER, camera_name, str(target_date),str(start_hour)
        )
        search_result = list(glob.glob(search_path, recursive=True))
        if len(search_result) >= 90:
            search_result = random.sample(search_result, 90)
        
        frames_list = frames_list + search_result #adding search_results to output frames_list
  
    return frames_list

# Train and dump frame based anomaly with updated dataset
def train_IF_model(aksha_path, camera_name, anomaly_percent, start_hour):
    print("training")
    # Get frames for training
    training_frames = get_training_frames(aksha_path, start_hour, 7, camera_name)

    # If no traninig_frames are returned
    if len(training_frames) == 0:
        return f'No frame detected for training'

    # Generate array
    image_array = None
    f = 0

    for image_filename in training_frames:
 
        # print("read")
        image = cv2.imread(image_filename) #reading training frames

        # Checking if image is of type np.ndarray
        if isinstance(image, np.ndarray):
            image = image.flatten() #flattening the array
            image = np.expand_dims(image, axis=0)
            f = 1
            if image_array is None:
                image_array = image
            else:
                image_array = np.append(image_array, image, axis=0)

    
    if image_array is not None:
        clf = IsolationForest(contamination=anomaly_percent) 
        clf.fit(image_array) # Training the classifier
        
        # Dumping classifier
        
        dir_path = f"{aksha_path}/{str(camera_name)}/anomaly_models/framebase" #dir path for saving frame based anomaly models
        
        # Checking if the directory exists
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_name = '{}.pkl'.format(str(start_hour))
        try:
            pickle.dump(clf, open(os.path.join(dir_path,file_name), 'wb'))
            return f"Framebased anomaly model for {str(camera_name)} for {str(start_hour)} hour stored successfully!!!"
        except Exception as e:
 
            return f"Framebased anomaly model for {str(camera_name)} for {str(start_hour)} hour failed to store with exception {e} !!!"



def gen_weekly_bgImage(aksha_path, db, logger):
    """
    to generate weekly background image (at "00:00:00")

    """        

    try:
        # logging.basicConfig(filename=f"{aksha_path}/anomaly-model-training.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)
        # logger = logging.getLogger()
        camera_names=db.config.distinct("Camera_Name")
        # camera_names=["camera1", "camera2"]     
        logger.info(msg= f"{camera_names}")
        logger.info(msg=f"Mongo DB established connection")
        # calling training function for each camera
        for camera_name in camera_names:
            background_path = f'{aksha_path}/{camera_name}/background'
            #self.logger.info(f">>>>>>>>>>>>{[len(self.frames_background_gen[str(hour)]) for hour in range(24)]}")
            for hour in range(24):
                video = cv2.VideoCapture(f'{background_path}/background_data_{hour}.mp4')
                frames = []
                while(video.isOpened()):
                    ret, frame = video.read()
                    if ret == False:
                        break
                    frames.append(frame)
                if frames:
                    cv2.imwrite(background_path + f'/weekly_background_hour_{hour}.jpg', np.median(frames, axis=0).astype(dtype=np.uint8) )
                    logger.info(msg= f"weekly_bg_image saved for {camera_name}")
                video.release()

    except Exception as e:
        logger.info(
            msg=f"Weekly background generation failed with exception: {e} ")

