
def email_status_check(frame_anomaly_status, object_anomaly_status, no_object_status, alert_results, previous_alert_statuses, skip_fps_sec, time_interval = 120):    
    '''
    Inputs : frame_anomaly_status, object_anomaly_status, no_object_status, alert_results, previous_alert_statuses, skip_fps_sec, time_interval(default = 120 seconds).
    Utility : This is a time based email filter logic. The counter gets triggered once an alert is detected, and until the counter reaches the specified interval of time, no new alert will be reported by email.
    Outputs : frame_anomaly_validity, object_anomaly_validity, alert_validity, no_object_validity, previous_alert_statuses.
    '''



    frame_check_count = int(time_interval/skip_fps_sec)
    frame_anomaly_validity = False
    object_anomaly_validity = False
    if not frame_anomaly_status:
        previous_alert_statuses["frame_alert"]["count"] = 0
    else:
        if previous_alert_statuses["frame_alert"]["count"]:
            previous_alert_statuses["frame_alert"]["count"] += 1
        if not previous_alert_statuses["frame_alert"]["count"]:
            frame_anomaly_validity = True
            previous_alert_statuses["frame_alert"]["count"] += 1
        if previous_alert_statuses["frame_alert"]["count"] == frame_check_count:
            previous_alert_statuses["frame_alert"]["count"] = 0
            
    if not object_anomaly_status:
        previous_alert_statuses["object_alert"]["count"] = 0
    else:
        if previous_alert_statuses["object_alert"]["count"]:
            previous_alert_statuses["object_alert"]["count"] += 1
        if not previous_alert_statuses["object_alert"]["count"]:
            object_anomaly_validity = True
            previous_alert_statuses["object_alert"]["count"] += 1
        if previous_alert_statuses["object_alert"]["count"] == frame_check_count:
            previous_alert_statuses["object_alert"]["count"] = 0
    previous_alert_statuses["frame_alert"]["status"] = frame_anomaly_status
    previous_alert_statuses["object_alert"]["status"] = object_anomaly_status


    alert_validity = [False]*len(previous_alert_statuses["detection_alert"])
    no_object_validity = [False]*len(previous_alert_statuses["no_object"])
    i = 0
    if no_object_status:
        detect_key = "no_object"
        el = "detection_alert"
    else:
        detect_key = "detection_alert"
        el = "no_object"
    for key in previous_alert_statuses[el]:
        previous_alert_statuses[el][key]["count"] = 0
        previous_alert_statuses[el][key]["status"] = False
    for key in previous_alert_statuses[detect_key]:
        if key not in alert_results:
            previous_alert_statuses[detect_key][key]["count"] = 0
        else:
            if previous_alert_statuses[detect_key][key]["count"]:
                previous_alert_statuses[detect_key][key]["count"] += 1
            if not previous_alert_statuses[detect_key][key]["count"]:
                if no_object_status:
                    no_object_validity[alert_results.index(key)] = True
                else:
                    alert_validity[alert_results.index(key)] = True
                previous_alert_statuses[detect_key][key]["count"] += 1
            if previous_alert_statuses[detect_key][key]["count"] == frame_check_count:
                previous_alert_statuses[detect_key][key]["count"] = 0
        previous_alert_statuses[detect_key][key]["status"]  = True if key in alert_results else False
    

    return frame_anomaly_validity, object_anomaly_validity, alert_validity, no_object_validity, previous_alert_statuses

    # #The below code was for frame based postfilter logic
    # frame_status_check = True if previous_alert_statuses["frame_alert"]["status"] == frame_anomaly_status and previous_alert_statuses["frame_alert"]["status"] else False
    # object_status_check = True if previous_alert_statuses["object_alert"]["status"] == object_anomaly_status and previous_alert_statuses["object_alert"]["status"] else False
    # object_anomaly_validity = False
    # frame_anomaly_validity = False
    # if not previous_alert_statuses["object_alert"]["status"] and object_anomaly_status:
    #     object_anomaly_validity = True
    # if not previous_alert_statuses["frame_alert"]["status"] and frame_anomaly_status:
    #     frame_anomaly_validity = True
    # if object_status_check:
    #     if not (previous_alert_statuses["object_alert"]["count"] + 1) % frame_check_count:
    #         object_anomaly_validity = True
    #         previous_alert_statuses["object_alert"]["count"] = 0
    #     else:
    #         previous_alert_statuses["object_alert"]["count"] += 1
    # else:
    #     object_anomaly_validity = True
    # if frame_status_check:
    #     if not (previous_alert_statuses["frame_alert"]["count"] + 1) % frame_check_count:
    #         frame_anomaly_validity = True
    #         previous_alert_statuses["frame_alert"]["count"] = 0
    #     else:
    #         previous_alert_statuses["frame_alert"]["count"] += 1
    # else:
    #     frame_anomaly_validity = True
    # previous_alert_statuses["frame_alert"]["status"] = frame_anomaly_status
    # previous_alert_statuses["object_alert"]["status"] = object_anomaly_status

    # alert_validity = [False]*len(previous_alert_statuses["detection_alert"])
    # i = 0
    # for key in previous_alert_statuses["detection_alert"]:
    #     if key in alert_results:
    #         if previous_alert_statuses["detection_alert"][key]["status"]:
    #             if not (previous_alert_statuses["detection_alert"][key]["count"] + 1) % frame_check_count:
    #                 alert_validity[i] = True
    #                 previous_alert_statuses["detection_alert"][key]["count"] = 0
    #             else:
    #                 previous_alert_statuses["detection_alert"][key]["count"] += 1
    #         else:
    #             alert_validity[i] = True
    #         previous_alert_statuses["detection_alert"][key]["status"] = True
    #     else:
    #         previous_alert_statuses["detection_alert"][key]["status"] = False
    #     i += 1
    

    