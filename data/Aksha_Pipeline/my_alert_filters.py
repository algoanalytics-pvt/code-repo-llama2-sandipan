from pymongo import MongoClient
import logging
from shapely.geometry import Polygon, Point
import cv2
import numpy as np
import datetime as dt
from PIL import Image, ImageDraw


def apply_filter(LIST_MYALERT_CONFIG, object_detection_results,crowd_threshold):
    """
            Input   :   Alert Name in args, LIST_ALERT_CONFIG having all configuration of the alerts mentioned in args.my_alerts and
                        a list named object_detection_results having co-ordinates of the objects detected in object detection  model
            Utility :   To check whether the objects detected by our object detection model intersects with the area defined by the user.
            Output  :   alert_results, alert_result_config, user_area
    """
    # Lists creation
    alert_results = []  # Consists of only applicable alert names
    alert_result_config = []  # Consists config of applicable alerts
    no_object = False

    for alert_config in LIST_MYALERT_CONFIG:
        filtered_objects = []
        no_object_status = False
        #print("24")
        print(f"for alert {alert_config['Alert_Name']} with start time {alert_config['Start_Time']} and end time {alert_config['End_Time']}")
        if str(dt.datetime.now().strftime("%A")) in alert_config["Days_Active"]:  # Check whether current day is mentioned for the particular alert or not
            #print("27")
            print(f"{dt.datetime.now().time()} '>' {dt.datetime.strptime(alert_config['Start_Time'], '%H:%M').time()} , {dt.datetime.now().time()} '<' {dt.datetime.strptime(alert_config['End_Time'], '%H:%M').time()}")
            print(dt.datetime.strptime(alert_config["Start_Time"], '%H:%M').time() < dt.datetime.now().time() < dt.datetime.strptime(alert_config["End_Time"], '%H:%M').time())
            if (dt.datetime.strptime(alert_config["Start_Time"], '%H:%M').time() < dt.datetime.now().time() < dt.datetime.strptime(alert_config["End_Time"], '%H:%M').time()):
                #print("28")
                if alert_config["No_Object_Status"]:
                    #print("31")
                    try:
                        if alert_config["Object_Area"]:  # Check whether user defined area is present or not
                            
                            # Loop for multiple objects detected by model
                            num_persons = 0
                            for i in object_detection_results:
                                if alert_config["Object_Class"] == i["label"]:
                                    list(alert_config["Object_Area"]).append(alert_config["Object_Area"][0])
                                    p1 = Polygon(list(alert_config["Object_Area"]))
                                    p2_centroid = Point(i["x"] + (i["w"] / 2), i["y"] + (i["h"] / 2))  # Centroid of the object detected by model
                                    if p2_centroid.within(p1):
                                        filtered_objects.append(i)
                                        
                                elif alert_config["Object_Class"] == "crowd" and i["label"] == "person":
                                    list(alert_config["Object_Area"]).append(alert_config["Object_Area"][0])
                                    p1 = Polygon(list(alert_config["Object_Area"]))
                                    p2_centroid = Point(i["x"] + (i["w"] / 2), i["y"] + (i["h"] / 2))
                                    if p2_centroid.within(p1):
                                        filtered_objects.append(i)
                                        num_persons += 1        
                                
                                else:
                                    continue
                                
                            if filtered_objects:
                                if alert_config["Object_Class"] == "crowd" and (num_persons >= crowd_threshold):
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"],
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"],
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": alert_config["Object_Area"],
                                        "Email_Activation": alert_config["Email_Activation"],
                                        "Alert_Description": alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object
                                    
                                    
                                
                                elif alert_config["Object_Class"] == "crowd" and (num_persons < crowd_threshold):
                                    pass

                                else:
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"],
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"],
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": alert_config["Object_Area"],
                                        "Email_Activation": alert_config["Email_Activation"],
                                        "Alert_Description": alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object
                                    
                        else:
                        
                            num_persons = 0
                            for i in object_detection_results:
                                if alert_config["Object_Class"] == i["label"]:
                                    filtered_objects.append(i)
                                elif alert_config["Object_Class"] == "crowd" and i["label"] == "person":
                                    filtered_objects.append(i)
                                    num_persons += 1
                                else:
                                    continue
                                
                            if filtered_objects:
                                if alert_config["Object_Class"] == "crowd" and (num_persons >= crowd_threshold):
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"], 
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"], 
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": None,
                                        "Email_Activation": alert_config["Email_Activation"],
                                        "Alert_Description": alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object
                                    
                                
                                elif alert_config["Object_Class"] == "crowd" and (num_persons < crowd_threshold):
                                    pass

                                    
                                else:
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"], 
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"], 
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": None,
                                        "Email_Activation": alert_config["Email_Activation"],
                                        "Alert_Description": alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object
                                    

                    except Exception as e:
                        return f"apply_filter() function failed with exception: {e}"
                else:
                    try:
                        #print(32)
                        if not alert_config["Object_Area"]:  # Check whether user defined area is present or not
                            raise Exception("Object area not defined!")
                        else:
                            no_object_status = True
                            # Loop for multiple objects detected by model
                            
                            num_persons = 0
                            for i in object_detection_results:
                                if alert_config["Object_Class"] == i["label"]:
                                    list(alert_config["Object_Area"]).append(alert_config["Object_Area"][0])
                                    p1 = Polygon(list(alert_config["Object_Area"]))
                                    p2_centroid = Point(i["x"] + (i["w"] / 2), i["y"] + (i["h"] / 2))  # Centroid of the object detected by model
                                    if p2_centroid.within(p1):
                                        no_object_status = False
                                        filtered_objects.append(i)
                                        
                                elif alert_config["Object_Class"] == "crowd" and i["label"] == "person":
                                    list(alert_config["Object_Area"]).append(alert_config["Object_Area"][0])
                                    p1 = Polygon(list(alert_config["Object_Area"]))
                                    p2_centroid = Point(i["x"] + (i["w"] / 2), i["y"] + (i["h"] / 2))
                                    if p2_centroid.within(p1):
                                        filtered_objects.append(i)
                                        num_persons +=1
                                        
                                else:
                                    continue
                                
                            if no_object_status: 
                                if alert_config["Object_Class"] == "crowd" and (num_persons >= crowd_threshold):
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"], 
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"], 
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": alert_config["Object_Area"],
                                        "Email_Activation":alert_config["Email_Activation"],
                                        "Alert_Description":alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object
                                   
                                elif alert_config["Object_Class"] == "crowd" and (num_persons < crowd_threshold):
                                    pass       

                                else:
                                    alert_filter_result = {
                                        "Alert_Name": alert_config["Alert_Name"], 
                                        "Display_Activation": alert_config["Display_Activation"],
                                        "Workday": alert_config["Workday_Status"], 
                                        "Holiday": alert_config["Holiday_Status"],
                                        "Filtered_Objects": filtered_objects,
                                        "Area_of_Interest": alert_config["Object_Area"],
                                        "Email_Activation":alert_config["Email_Activation"],
                                        "Alert_Description":alert_config["Alert_Description"]
                                    }
                                    alert_result_config.append(alert_filter_result)
                                    alert_results.append(alert_config["Alert_Name"])
                                    return alert_results, alert_result_config, no_object

                    except Exception as e:
                        return f"apply_filter() function failed (no object alert) with exception: {e}"
            else:
                continue
        else:
            continue
        no_object = no_object or no_object_status
        

    return alert_results, alert_result_config, no_object

def make_top_right_arrow(image, triangle_percentage):
    print('inside function')
    width, height = image.size
    triangle_size = int(min(width, height) * triangle_percentage/2) 
    blue_arrow = Image.new("RGBA", (triangle_size, triangle_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(blue_arrow)
    points = [(triangle_size, 0), (triangle_size, triangle_size), (0, 0)]
    draw.polygon(points, fill=(10,87,235, 255))
    image.paste(blue_arrow, (width - triangle_size, 0), mask=blue_arrow)
    return image

def draw_filter(LIST_Alert_Config, result_img, check):
    """
            Input   :   Latest frame, LIST of applicable alert config from apply_filter() function, no_object/my_alert check. 
            Utility :   To draw all alerts that are defined by the user on latest frame.
            Output  :   An image with all the boxes and area drawn on it.
    """

    processed_frame = result_img.copy()
    workday_frame = result_img.copy()
    holiday_frame = result_img.copy()

    for i in LIST_Alert_Config:  
        try:
            try:
                # Draw "Area of Interest" if applicable 
                if i["Area_of_Interest"]:
                        pts = np.array(i["Area_of_Interest"], np.int32)
                        isClosed = True
                        color = (255, 0, 0)
                        thickness = 2
                        processed_frame = cv2.polylines(processed_frame, [pts], isClosed, color, thickness)
            except Exception as e:
                return f"draw_filter() function failed on cv2.polylines: {e}"
            try:

                # Draw "Area of Interest" if applicable 
                if i["Filtered_Objects"]:
                    for j in i["Filtered_Objects"]:
                        processed_frame = cv2.rectangle(processed_frame, (j["x"], j["y"]), ((j["x"] + j["w"]), (j["y"] + j["h"])),
                                                        (0, 255, 0), 2)
                        processed_frame = cv2.putText(processed_frame, j["label"], (j["x"], (j["y"] + j["h"])),
                                                    cv2.FONT_HERSHEY_SIMPLEX,
                                                    0.6, (0, 0, 255), 2, cv2.LINE_AA)
                font = cv2.FONT_HERSHEY_PLAIN
                if check == "no_object":
                    points=np.array([[650,0],[650,50],[600,0]])
                    processed_frame = cv2.fillPoly(processed_frame, pts=[points], color=(0,0,255))
                    
                    #processed_frame = make_top_right_arrow(processed_frame, triangle_percentage)
                else:
                    points=np.array([[650,0],[650,50],[600,0]])
                    processed_frame = cv2.fillPoly(workday_frame, pts=[points], color=(0,0,255))
                    #triangle_percentage=0.1
                    #processed_frame = make_top_right_arrow(processed_frame, triangle_percentage)
                # cv2.imwrite("/home/algo39/Aksha/test/processed_frame.jpg", processed_frame)
            except Exception as e:
                return f"draw_filter() cv2.rectangle or cv2 putext: {e}"

                 
        except Exception as e:
            return f"draw_filter() function failed with exception: {e}"


        # Applied Alert Display Activation  
        if i["Display_Activation"]:

            # Alert Applicable only on Workday 
            if i["Workday"]:
        
                try:
                    # Draw "Area of Interest" if applicable 
                    if i["Area_of_Interest"]:
                            pts = np.array(i["Area_of_Interest"], np.int32)
                            isClosed = True
                            color = (255, 0, 0)
                            thickness = 2
                            workday_frame = cv2.polylines(workday_frame, [pts], isClosed, color, thickness)

                    # Draw "Area of Interest" if applicable    
                    if i["Filtered_Objects"]:   
                        for j in i["Filtered_Objects"]:
                            workday_frame = cv2.rectangle(workday_frame, (j["x"], j["y"]), ((j["x"] + j["w"]), (j["y"] + j["h"])),
                                                            (0, 255, 0), 2)
                            workday_frame = cv2.putText(workday_frame, j["label"], (j["x"], (j["y"] + j["h"])),
                                                        cv2.FONT_HERSHEY_SIMPLEX,
                                                        0.6, (0, 0, 255), 2, cv2.LINE_AA)
                            
                    font = cv2.FONT_HERSHEY_PLAIN
                    if check == "no_object":
                        points=np.array([[650,0],[650,50],[600,0]])
                        workday_frame = cv2.fillPoly(workday_frame, pts=[points], color=(0,0,255))
                        #triangle_percentage=0.1
                        #workday_frame = make_top_right_arrow(workday_frame, triangle_percentage)
                    else:
                        #workday_frame = cv2.putText(workday_frame, "My_Alert", (10, 25), font, 2, (0, 0, 255), 3)
                        points=np.array([[650,0],[650,50],[600,0]])
                        workday_frame = cv2.fillPoly(workday_frame, pts=[points], color=(0,0,255))
                        #triangle_percentage=0.1
                        #workday_frame = make_top_right_arrow(workday_frame, 0.1)
                    # cv2.imwrite("/home/algo39/Aksha/test/workday_frame.jpg", workday_frame)
                        
                except Exception as e:
                    return f"draw_filter() function failed with exception: {e}"
            
            # Alert Applicable only on Holiday 
            if i["Holiday"]:
                try:
                    # Draw "Area of Interest" if applicable 
                    if i["Area_of_Interest"]:
                            pts = np.array(i["Area_of_Interest"], np.int32)
                            isClosed = True
                            color = (255, 0, 0)
                            thickness = 2
                            holiday_frame = cv2.polylines(holiday_frame, [pts], isClosed, color, thickness)

                    # Draw "Area of Interest" if applicable     
                    if i["Filtered_Objects"]:  
                        for j in i["Filtered_Objects"]:
                            holiday_frame = cv2.rectangle(holiday_frame, (j["x"], j["y"]), ((j["x"] + j["w"]), (j["y"] + j["h"])),
                                                            (0, 255, 0), 2)
                            holiday_frame = cv2.putText(holiday_frame, j["label"], (j["x"], (j["y"] + j["h"])),
                                                        cv2.FONT_HERSHEY_SIMPLEX,
                                                        0.6, (0, 0, 255), 2, cv2.LINE_AA)
                            
                    font = cv2.FONT_HERSHEY_PLAIN
                    if check == "no_object":
                        points=np.array([[650,0],[650,50],[600,0]])
                        holiday_frame = cv2.fillPoly(holiday_frame, pts=[points], color=(0,0,255))
                    else:
                        points=np.array([[650,0],[650,50],[600,0]])
                        holiday_frame = cv2.fillPoly(holiday_frame, pts=[points], color=(0,0,255))
                        # triangle_percentage=0.1
                        # holiday_frame = make_top_right_arrow(holiday_frame, triangle_percentage)
                            
                except Exception as e:
                  return f"draw_filter() function failed with exception: {e}"   


    
    return processed_frame, workday_frame, holiday_frame