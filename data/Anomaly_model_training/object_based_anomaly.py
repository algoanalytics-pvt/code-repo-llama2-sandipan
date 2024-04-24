from asyncio.log import logger
from datetime import date
from datetime import timedelta
import datetime
import pandas as pd
import pymongo
from sklearn.ensemble import IsolationForest
import pickle
import os

# Object classes from YOLO object detection
object_classes = ["person","supine person","helmet","no helmet","car","bicycle","truck","motorcycle","backpack","handbag", "gate open", "gate closed", "fork lift"]

# Get count of each obj in frame 
def get_count(lst,obj):
    return len([x for x in lst if x['label'] == obj])

# MongoDB api to get objects data for given camera_name, start_time and end_time. 
def get_objects_data(camera_name,start_time,end_time, database):
    posts = database["meta_"+str(camera_name)] #getting the camera_name collection
    objects = [] #output list of documents
    for post in posts.find({"Timestamp": {"$lt": end_time, "$gt": start_time}}):
        objects.append(post) #appending the query result in ouput list
    return objects

# Get training data and preprocess the data for given start_hour,end_hour,number of days and camera id
def get_training_data(start_hour, end_hour, n_days, camera_name, database):
    current_date = date.today()
    output_list = []
    filtered_df = pd.DataFrame()
    for diff in range(0, n_days + 1):
        target_date = current_date - timedelta(diff)

        # Generate starting and ending time for query
        start_time = datetime.datetime(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=start_hour,
            minute=0,
            second=0,
            microsecond=0,
        )
        
        if end_hour == 24:
            end_time = start_time.replace(hour=23, minute=59, second=59)
        else:
            end_time = start_time.replace(hour=end_hour)

        output_list = output_list + get_objects_data(camera_name, start_time, end_time, database)
    filtered_df = pd.DataFrame(output_list)

    if(len(filtered_df) == 0):
        return filtered_df

    filtered_df['date'] = filtered_df['Timestamp'].dt.day
    filtered_df['month'] = filtered_df['Timestamp'].dt.month
    filtered_df['hour'] = filtered_df['Timestamp'].dt.hour
    filtered_df['minutes'] = filtered_df['Timestamp'].dt.minute

    for obj in object_classes:
        filtered_df[obj] = filtered_df['Results'].apply(get_count,obj = obj)
    filtered_df.drop(["Timestamp","Frame_Anomaly","Object_Anomaly","Results","_id", "Alerts", "No_Object_Status"],axis = 1,inplace = True)
    return filtered_df


#Training and dumping the object based anomaly model with updated dataset
def train_IF_object_based_model(aksha_path, camera_name, anomaly_percent, start_hour, database):

    # Get data for training
    try:
        training_data = get_training_data(start_hour, start_hour + 1, 7, camera_name, database)
        print(f"got training data")
    except Exception as e:
        print(f"get training data issue {e}")

    if len(training_data) == 0:
        return None

    print(training_data)
    clf = IsolationForest(contamination=anomaly_percent)
    try:
        clf.fit(training_data.values)
    except Exception as e:
        print(f"clf error {e}")
    
    #Dumping classifier
    dir_path = f"{aksha_path}/{str(camera_name)}/anomaly_models/objectbase"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = '{}.pkl'.format(str(start_hour))
    try: 
        pickle.dump(clf, open(os.path.join(dir_path,file_name), 'wb'))
        return f"Objectbased anomaly model for {str(camera_name)} for {str(start_hour)} hour stored successfully!!!"
    except Exception as e:
        return f"Objectbased anomaly model for {str(camera_name)} for {str(start_hour)} hour failed to store with exception {e} !!!"
