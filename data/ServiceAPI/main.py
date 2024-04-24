# uvicorn fastAPI:app --reload (Command to run the file)
from multiprocessing import allow_connection_pickling
from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import json
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import insight
import store_reference_img
import logging

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
work_dir = "./Aksha"
# work_dir = "/home/algo39/kartikz/Aksha-Version-2/Aksha"
store_reference_img.main(work_dir)

logging.basicConfig(filename=f"{work_dir}/insight.log", format='%(asctime)s %(message)s', filemode='w',
            level=logging.DEBUG)
logger = logging.getLogger()


# A Pydantic model
class Subscription(BaseModel):
    # id: int
    subscriptionKey: str
    # joined: date 


class Surveillance(BaseModel):
    type:str
    camera_list: list 
    
class Insight(BaseModel):
    camera_name: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    
    #REQUEST BODY FOR INSIGHT
        # {"Start_Date": 2022-09-01, "Start_Time": 21:00:00, "End_Date": 2022-09-10, 
        # "End_Time": 01:00:00, "Camer_Name": "${Camera_Name}"}

@app.post("/Subscription")
async def main(item:Subscription ):

    if item.subscriptionKey == "hi":
        return {"Status":"Running", "RemainingDays":10}
    else:
        return {"Status":"Expired", "RemainingDays":0}

@app.post("/Insight")
def Insight(item:Insight):
    camera_name = item.camera_name
    start_date = item.start_date
    start_time = item.start_time
    end_date = item.end_date
    end_time = item.end_time
    try:
        insight.create_heatmap(Start_date=start_date, Start_time=start_time, End_date=end_date, End_time=end_time,Camera_name=camera_name, work_dir= work_dir, logger = logger)  
    except Exception as e:
        return(f"Create_heatmap() function facing issue, {e}")

    
    return f"Result precessed for Insight(Heatmap)"

@app.get("/rtsplinks.json")
async def get_rtsp_links():
    file_name = "rtsplinks.json"
    file_path = f"{work_dir}/{file_name}"
    return FileResponse(file_path)
    
def command_func(i):
    print(len(i["alerts"]), i["alerts"])
    alert = " ".join(i["alerts"])
    rtsp = f'{i["rtsp_link"]}'
    email_auto_alert = i['email_auto_alert'] if "email_auto_alert" in i.keys() else True
    display_auto_alert = i['display_auto_alert'] if "display_auto_alert" in i.keys() else True
    email_alert = i['email_alert'] if "email_alert" in i.keys() else True
    display_alert = i['display_alert'] if "display_alert" in i.keys() else True
 
    if len(i["alerts"]) == 0:
        # command = f'docker run -d --name {str(i["camera_name"])} --volumes-from aksha_service_api_1 --network aksha-net surveillance:latest /bin/bash -c "python3 main.py --camera_name {str(i["camera_name"])} --video_path "{rtsp}" --object_detection --skip_fps_sec {str(i["skip_interval"])} --prefilter_threshold {i["skip_interval"]}"'
        command = f'docker run -d --restart unless-stopped --env ENVIRONMENT="prod.json" --env CAMERA_NAME={str(i["camera_name"])} --env UPDATE_CAMERA_NAME={str(i["update_camera_name"])} --env RTSP_ID={str(i["rtsp_id"])} --env RTSP_LINK="{rtsp}" --env OBJECT_DETECTION="True" --env ANOMALY_DETECTION="True" --env SKIP_INTERVAL={str(i["skip_interval"])} --env MY_ALERTS=" " --env AUTOALERT_EMAIL_NOTIFICATION_SERVICE="{email_auto_alert}" --env AUTOALERT_DISPLAY="{display_auto_alert}" --env EMAIL_ALERT="{email_alert}" --env ALERT_DISPLAY="{display_alert}" --env TELEGRAM_SERVICE="True" --env WHATS_APP_SERVICE="False" --env crowd_threshold=6 --env time_delta=10  --name {str(i["update_camera_name"])} --volumes-from API_SERVICE --network aksha-net dockerhubalgo/surveillance:latest'

    else:
        # command = f'docker run -d --name {str(i["camera_name"])} --volumes-from aksha_service_api_1 --network aksha-net surveillance:latest /bin/bash -c "python3 main.py --camera_name {str(i["camera_name"])} --video_path "{rtsp}"  --object_detection --skip_fps_sec {str(i["skip_interval"])} --prefilter_threshold {i["skip_interval"]} --my_alerts {" ".join(i["alerts"])}"'
        command = f'docker run -d --restart unless-stopped --env ENVIRONMENT="prod.json" --env CAMERA_NAME={str(i["camera_name"])} --env UPDATE_CAMERA_NAME={str(i["update_camera_name"])} --env RTSP_ID={str(i["rtsp_id"])} --env RTSP_LINK="{rtsp}" --env OBJECT_DETECTION="True" --env ANOMALY_DETECTION="True" --env SKIP_INTERVAL={str(i["skip_interval"])} --env MY_ALERTS="{alert}" --env AUTOALERT_EMAIL_NOTIFICATION_SERVICE="{email_auto_alert}" --env AUTOALERT_DISPLAY="{display_auto_alert}" --env EMAIL_ALERT="{email_alert}" --env ALERT_DISPLAY="{display_alert}" --env TELEGRAM_SERVICE="True" --env WHATS_APP_SERVICE="False" --env crowd_threshold=6 --env time_delta=10 --name {str(i["update_camera_name"])} --volumes-from API_SERVICE --network aksha-net dockerhubalgo/surveillance:latest'

    print(command)
    return command

@app.post("/Surveillance")
def SurveillanceAction(item:Surveillance):
    result = []
    if item.type == "start":
        for i in item.camera_list:
            print("Start",type(i['alerts']))           
            command = command_func(i)
            os.system(command)
            result.append(str(i["camera_name"]))
            with open(f"{work_dir}/rtsplinks.json", "r") as in_file:
                data = json.load(in_file)
            data[i["rtsp_link"]]["cam_name"] = i["camera_name"]
            data[i["rtsp_link"]]["running_status"] = True
            with open(f"{work_dir}/rtsplinks.json", "w") as write_file:
                json.dump(data, write_file, indent=4)

    elif item.type == "restart":
        for i in item.camera_list:
            print("Restart",(i['alerts']))
            with open(f"{work_dir}/rtsplinks.json", "r") as in_file:
                data = json.load(in_file)
            for link in data:
                if link == i["rtsp_link"]:
                    if data[link]["running_status"] == True:
                        if data[link]["cam_name"] != i["update_camera_name"]:
                            
                            #command = f"docker rename {data[link]['cam_name']} {i['camera_name']} "
                            command_2 = f"docker stop {data[link]['cam_name']} "
                            command_3 = f"docker system prune -f"
                            os.system(command_2)
                            os.system(command_3)
                            # i['camera_name'] = i["update_camera_name"]
                            command = command_func(i)

                            os.system(command)
                            data[link]["cam_name"] = i["update_camera_name"]
                            with open(f"{work_dir}/rtsplinks.json", "w") as write_file:
                                json.dump(data, write_file, indent=4)
                        else:
                            command = command_func(i)
                            command_2 = f"docker stop {i['camera_name']} "
                            command_3 = f"docker system prune -f"
                            os.system(command_2)
                            os.system(command_3)
                            os.system(command)
            result.append(str(i["camera_name"]))

    elif item.type == "stop":
        for i in item.camera_list:
            print(i)
            command_2 = f"docker stop {i['camera_name']} "
            command_3 = f"docker system prune -f"
            os.system(command_2)
            os.system(command_3)
            result.append(str(i["camera_name"]))
            with open(f"{work_dir}/rtsplinks.json", "r") as in_file:
                data = json.load(in_file)
            data[i["rtsp_link"]]["running_status"] = False
            with open(f"{work_dir}/rtsplinks.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
    else:
        return "type is not define! please define type: 'start', 'restart' or 'stop'"
    return f"Following camera's are started: {result}"