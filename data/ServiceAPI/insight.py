import numpy as np
import cv2
import glob
from datetime import datetime, timedelta
import os
import logging
import create_input_video as ci
import output_video as ov
import ffmpeg

start = datetime.now()

work_dir = "./Aksha"


# logfile_path = f"/home/algo5/Aksha_latest_developer/Aksha-Version-2/Aksha/insight.log"
# logfile_isexist = os.path.exists(logfile_path)
# if not logfile_isexist:
#     os.makedirs(logfile_path)
#     logging.basicConfig(filename= logfile_path,
#                         format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)
#     logger = logging.getLogger()
#     logger.info(msg=f"{logfile_path} created")
# else:
#     logging.basicConfig(filename= logfile_path,
#                         format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)
#     logger = logging.getLogger()
#     logger.info(msg=f"{logfile_path} already exist")

# logging.basicConfig(filename=f"{work_dir}/insight.log", format='%(asctime)s %(message)s', filemode='w',
#                     level=logging.DEBUG)
# logger = logging.getLogger()



def get_diff_files (Start_date: str,End_date: str,Start_time: str,End_time: str,Camera_name: str, logger):        
    
    startD = datetime.strptime(Start_date, '%Y-%m-%d').date()
    
    endD = datetime.strptime(End_date, '%Y-%m-%d').date()
    startT = datetime.strptime(Start_time, '%H:%M:%S').time().hour
    endT = datetime.strptime(End_time, '%H:%M:%S').time().hour
    startm = datetime.strptime(Start_time, '%H:%M:%S').time().minute
    endm = datetime.strptime(End_time, '%H:%M:%S').time().minute

    frame_path= f"{work_dir}/{Camera_name}/frame/*.jpg"
    diff_files = []

    # PROCESS
    for filename in glob.glob(frame_path):
        image_timestamp_date= datetime.strptime(filename.split("/")[-1].split(" ")[0], "%Y-%m-%d").date()
        image_timestamp_hour= datetime.strptime(filename.split("/")[-1].split(" ")[-1].split(":")[0], '%H').time().hour
        
    #  image_timestamp_min= datetime.strptime(filename.split("/")[-1].split(" ")[-1].split(":")[1], '%M').time().minute
        if image_timestamp_date == startD == endD and endT >= image_timestamp_hour >= startT:
            diff_files.append(filename)
           
        elif startD != endD:
           
            if image_timestamp_date == startD and image_timestamp_hour >= startT:
                diff_files.append(filename)
            elif startD < image_timestamp_date < endD:
                diff_files.append(filename)
            elif image_timestamp_date == endD and image_timestamp_hour <= endT:
                diff_files.append(filename)
            else:
                continue
        else:
            
            continue
    startD = datetime.strptime(Start_date, '%Y-%m-%d').date()
    startT = datetime.strptime(Start_time, '%H:%M:%S').time().hour
    support_list = []
    for i in diff_files:
        print(i)
        if (datetime.strptime(i[-12:-4], '%H:%M:%S').time().minute < startm and datetime.strptime(i[-23:-4],
                                                                                            '%Y-%m-%d %H:%M:%S').date() == startD and datetime.strptime(
        i[-12:-4], '%H:%M:%S').time().hour == startT) or \
            datetime.strptime(i[-12:-4], '%H:%M:%S').time().minute > endm and datetime.strptime(i[-23:-4],
                                                                                                '%Y-%m-%d %H:%M:%S').date() == endD and datetime.strptime(
        i[-12:-4], '%H:%M:%S').time().hour == endT:
            support_list.append(i)

    for j in diff_files[:]:
 
        if j in support_list:
            diff_files.remove(j)

    return diff_files

                
                
                
def create_heatmap(Start_date: str,End_date: str,Start_time: str,End_time: str,Camera_name: str, work_dir,logger):
    
    """
    This function creates a heatmap for the specified time intervals by the user.

    Inputs:
        :Start_date: Start date for the filter
        :type Start_date: string
        :End_date: End date for the filter
        :type End_date: string
        :Start_time: Start time for the filter
        :type Start_time: string
        :End_time: End time for the filter
        :type End_time: string
        :Camera_name: Camera name for the filter
        :type Camera_name: string

    Returns:
        :: Heatmap generated for the specified filters.
    """
    
    # INITIALIZATION
    try:
        os.remove(f'{work_dir}/{Camera_name}/insight/heatmap_video_{Camera_name}.mp4')
        os.remove(f'{work_dir}/{Camera_name}/insight/converted_heatmap_video_{Camera_name}.mp4')
        os.remove(f'{work_dir}/{Camera_name}/insight/input_video_{Camera_name}.mp4')
    except:
        pass 

    diff_files = get_diff_files (Start_date, End_date, Start_time, End_time, Camera_name, logger)      

    try:
        input_video_path = ci.create_video_from_frames(diff_files, work_dir, Camera_name, logger)
        
        heatmap_vid_path = ov.heatmap_video(input_video_path, work_dir, Camera_name, logger)
        
        logger.info(msg= "Insight generated successfully!")


    except Exception as e:
        logger.info(msg= f'Following exception occured while trying to generate activity heatmap video: {e}')
            

end = datetime.now()
time_elapsed= (end - start).total_seconds() #* 10**3
print(f"Time elapsed for execution of this code: {time_elapsed} s")
