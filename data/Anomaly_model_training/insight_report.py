
import pymongo
import datetime 
import json
import os
import logging

# client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/Aksha?authSource=admin&tls=false", directConnection=True)

# db = client["Aksha"]

# def get_camera_list():
#     camera_names=db.config.distinct("Camera_Name")
#     return camera_names

def generate_insight_report(aksha_path, cameras, db, logger):
    '''
    Create a JSON file report with insights data for each day's alerts
    Inputs: aksha_path: path of the working directory, cameras: list of cameras fetched from MongoDB
            db: database connection, date: date for which the report is to be generated,
    Output: cam_data: dictionary in which all the insights data is stored
    '''
    try: 
        date= str(datetime.datetime.now().date())
    except Exception as e:
        logger.info(msg=f"Inside generate_obj_report: the following error occured in the first try block: {e}")

    try:
        path=f"{aksha_path}/insight_report/"
        if not os.path.exists(path):
            os.makedirs(path)
        cam_data={}
        most_active_hour_data={}
        cam_alerts={}
        alert_col= db["Alerts"]

        for cam in cameras: 
            cam_alerts[cam]=[]
            # cam_alerts: contains a dictionary  of all alerts in db, camera wise
            for al in alert_col.find():
                if cam in al["Camera_Name"]:
                    al_dict={al["Alert_Name"]:al["Object_Class"]}
                    cam_alerts[cam].append(al_dict)
                    

            cam_col = db[f"meta_{cam}"]
            obj_dict = {}
            temp = {}
            all_alerts={}
        
            for x in cam_col.find():
                alert_timestamp = x["Timestamp"]
                alert_date = str(alert_timestamp.date())

                if str(alert_date) == str(date):
                    alert_time = alert_timestamp.time()
                    for i in x["Alerts"]:
                        for j in cam_alerts[cam]:

                            if i in j:
                                obj_class=next(item[i] for item in cam_alerts[cam] if i in item)
                                my_alert=i
                            # Calculating object_detection_alerts for each camera
                                obj_dict[obj_class] = obj_dict.get(obj_class, 0) + 1

                            # Calculating and storing most_active_hour_for_each_object for each camera
                                if obj_class not in temp:
                                    temp[obj_class] = {h: 0 for h in range(24)}  # Initialize hour count to 0 for each label

                                alert_hour = alert_time.hour
                                temp[obj_class][alert_hour] += 1  # Increment count for the respective hour

                                link= f"http://localhost:5000/{cam}/alerts/{alert_date}%20{alert_time}_alert.jpg"
                                all_alerts[f"{alert_time}"]={
                                    "object":obj_class,
                                    "link":link,
                                    "my_alert_name": [my_alert],
                                    "timestamp": str(alert_timestamp)
                                }
                    most_active_hour_data = {}
                    peak_hour = None
                    max_alerts = 0

                    for obj_class, hour_counts in temp.items():
                        
                        max_hour = max(hour_counts, key=hour_counts.get)  # Get max hour value
                        most_active_hour_data[obj_class] = max_hour  # Set the max hour as value for the label in hour_data


                        # Calculating and storing peak_alert_time for each camera
                        if hour_counts[max_hour] > max_alerts:
                         
                            peak_hour = max_hour
                            max_alerts = hour_counts[max_hour]

                    cam_data[cam] = {
                        "object_detection_alerts": obj_dict,
                        "total_alerts_generated": sum(obj_dict.values()),
                        "most_active_hour_for_each_object": most_active_hour_data,
                        "peak_alert_time_hour": peak_hour,
                        "alerts": all_alerts
                    }
        
        filename = str(date) + '.json'
        filepath= f"{path}{filename}"
 
        try:
            with open(filepath, 'r+') as file:
                try:
                    
                    existing_data = json.load(file)
                    existing_data.update(cam_data)
                    file.seek(0)
                    json.dump(existing_data, file, indent=4)
                    logger.info(msg=f"Inside generate_obj_report: Data overwritten successfully.")
                except json.JSONDecodeError:
                    json.dump(cam_data, file, indent=4)
                    logger.info(msg=f"Inside generate_obj_report: New data added successfully.")
        except FileNotFoundError:
            
            with open(filepath, 'w') as file:
             
                json.dump(cam_data, file, indent=4)
                logger.info(msg=f"Inside generate_obj_report: New file created and data added successfully.")
                
    except Exception as e:
        logger.info(msg=f"Inside generate_obj_report: Following exception occurred in the second try block: {e}")



def del_insight_report(data_dir, time_delta):
    
    try:
        
        insight_report_isexist= os.path.exists(f'{data_dir}/insight_report/')
        if insight_report_isexist:
            insight_report_path=f"{data_dir}/insight_report/"
            
            for i in os.listdir(insight_report_path):
                
                file_date=datetime.datetime.strptime(f"{i.split('.')[0]}", "%Y-%m-%d")
                if ((datetime.datetime.now() - file_date).days) >= time_delta:
                    try:
                        os.remove(f"{data_dir}/insight_report/{i}")
                        logger.info(msg= f"JSON file found for insight report and successfully removed for date {i}! ")
                    except Exception as e:
                        logger.info(msg= f"No Record found to remove insight report file for date {i} with exception {e}!")
                else:
                    continue
    except Exception as e:
       return f"Insight report deletion failed with exception: {e}"

# aksha_path="Aksha"
# cameras=get_camera_list()
# logging.basicConfig(filename=f"{aksha_path}/anomaly-model-training.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)
# logger = logging.getLogger()
# generate_insight_report(aksha_path, cameras, db, logger)