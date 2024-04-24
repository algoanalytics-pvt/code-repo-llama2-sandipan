import os
import shutil
from datetime import date, timedelta
import datetime as dt
import logging
# import pymongo

def execute(DATABASE, camera_name, data_dir, time_delta:int, logger):


    try:
        COLLECTION_Meta = DATABASE[f"meta_{camera_name}"]
    except Exception as e:
       return f"Database connection is facing issue {e}"
    
    logger.info(msg=f"Thread for deletion started with time_delta as {time_delta}")
    camera_dir_path = f"{data_dir}{camera_name}"
    from_date = dt.datetime.now()-timedelta(days=time_delta)
    print(from_date)
    isexist = os.path.exists(camera_dir_path)
    foregroundisexist = os.path.exists(f'{camera_dir_path}/foreground/')
    frameisexist = os.path.exists(f'{camera_dir_path}/frame')
    alertsisexist = os.path.exists(f'{camera_dir_path}/alerts')

    try:
        data = COLLECTION_Meta.find({"Timestamp":{"$lte":from_date}})
        records = list(data)
        COLLECTION_Meta.delete_many({"Timestamp":{"$lte":from_date}})
        logger.info(msg= f"Records to be removed : {len(records)}")
        frame_date_list = [i["Timestamp"].date() for i in records]
        set_frame_date_list = set(frame_date_list)
        logger.info(msg= f"frame_date_list : {set_frame_date_list}")

        if isexist:
            if foregroundisexist:
                for j in set_frame_date_list:
                    try:
                        logger.info(msg=f"{camera_dir_path}/foreground/{j}")
                        shutil.rmtree(f"{camera_dir_path}/foreground/{j}", ignore_errors=True)
                        logger.info(msg= f"Record found for foreground images and successfully removed for date {j}!")
                    except Exception as e:
                       logger.info(msg= f"Exception occured for foreground images for {j} date : {e}")
            
            if frameisexist or alertsisexist:
                for k in records:
                    # print(k, len(k["Alerts"]))
                    if len(k["Alerts"])>0: 
                        try:
                            # logger.info(msg=f'{k["Timestamp"]}_alert.jpg')
                            os.remove(f'{camera_dir_path}/alerts/{k["Timestamp"]}_alert.jpg')
                            os.remove(f'{camera_dir_path}/frame/{k["Timestamp"]}.jpg')
                            # logger.info(msg= f"Record found, alert and frame data removed for timestamp {k['Timestamp']}!")
                        except Exception as e:
                            logger.info(msg= f"Exception occured when removing frame for timestamp {k['Timestamp']} with exception: {e}!")

                    elif k["Frame_Anomaly"] or k["Object_Anomaly"]:
                        try:
                            # logger.info(msg=f'{k["Timestamp"]}_autoalert.jpg')
                            os.remove(f'{camera_dir_path}/alerts/{k["Timestamp"]}_autoalert.jpg')
                            os.remove(f'{camera_dir_path}/frame/{k["Timestamp"]}.jpg')
                            # logger.info(msg= f"Record found, autoalert and frame data removed for timestamp {k['Timestamp']}!")
                        except Exception as e:
                            logger.info(msg= f"Exception occured when removing frame for timestamp {k['Timestamp']} with exception: {e}!")  

                    else:
                        try:
                            # logger.info(msg=f'{k["Timestamp"]}.jpg')
                            os.remove(f'{camera_dir_path}/frame/{k["Timestamp"]}.jpg')
                            # logger.info(msg= f"Record found, frame data removed for timestamp {k['Timestamp']}!")
                        except Exception as e:
                           logger.info(msg= f"Exception occured when removing frame for timestamp {k['Timestamp']} with exception {e}!")
                logger.info(msg=f"Data older than date: {from_date.date()} for {camera_name} has been removed from the storage")
   
    except Exception as e:
       return f"Data deletion failed with exception: {e}"
    
# if __name__=="__main__":
#     conn = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/Aksha?authSource=admin&tls=false", directConnection=True)
#     database= conn["Aksha"]
#     camera_name = "algocam"
#     data_dir= "/home/algo39/kartikz/Aksha-Version-2/Aksha/"
#     time_delta= 24
    
#     # logging.basicConfig(filename=f"{data_dir}{camera_name}/deletion.log", format='%(asctime)s %(message)s', filemode='a+',
#     #                 level=logging.DEBUG)

#     execute(database, camera_name, data_dir, time_delta)
