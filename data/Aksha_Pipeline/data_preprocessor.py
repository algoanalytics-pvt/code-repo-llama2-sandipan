import pandas as pd 

# get count of each obj in frame 
def get_count(lst,obj):

    return len([x for x in lst if x['label'] == obj])

# object anoamly model input data preprocessing
def data_preprocess_object_based_anomaly(object_classes, date_time, results):
    temp_df = pd.DataFrame()
    temp_date = date_time.date()
    temp_time = date_time.time()
    temp_df['date'] = [temp_date.day]
    temp_df['month'] = [temp_date.month]
    temp_df['hour'] = [temp_time.hour]
    temp_df['minutes'] = [temp_time.minute]
    temp_df['Results'] = [results]
    for obj in object_classes:
        temp_df[obj] = temp_df['Results'].apply(get_count, obj = obj)
    
    temp_df.drop(["Results"],axis = 1, inplace = True )
    return temp_df.values