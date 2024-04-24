import json
import sys
import os
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import imgkit
import smtplib
from azure.storage.blob import BlobServiceClient, ContentSettings
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
        # print(base_path, "<<<<<<<<<< exe_base_path")
    except Exception as e:
        base_path = os.path.abspath(".")
        # print(base_path, "<<<<<<< base_path")
    return os.path.join(base_path, relative_path)

def az_upload(camera_dir, subscription, sas_url):
    service = BlobServiceClient(sas_url)
    bb = service.get_blob_client(container= subscription, blob=f"{camera_dir}/notification.jpg")
    image_content_setting = ContentSettings(content_type='image/jpeg')
    with open(f"notification.jpg", "rb") as data:
        bb.upload_blob(data,overwrite=True,content_settings=image_content_setting)
    return bb.url

def get_download_url(folder_id, notif_img):
    '''
        Here, we take the notification image and upload it on the drve of Akshainfo@algoanalytics.com and
        return a download url for that image. this was done for sending notifications through whatsapp.
    '''
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
    for file in file_list:
        file.Trash()
    gfile = drive.CreateFile({'parents': [{'id': folder_id}]})
    gfile.SetContentFile(notif_img)
    gfile.Upload()
    print('title: %s, id: %s' % (gfile['title'], gfile['id']))
    #print(gfile['alternateLink'])  # Display the sharable link.
    download_url  = f"https://drive.google.com/uc?id={gfile['id']}&export=download"

    return download_url

def send_to_telegram(image_file, chat_id, bot_token):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

        with open(image_file, 'rb') as image:
            files = {'photo': image}
            data = {'chat_id': chat_id, 'caption': 'Aksha Alert: This is an important image!'}

            response = requests.post(url, files=files, data=data)

        result = "Notification sent to Telegram chat successfully!"
    except Exception as e:
        result = f"Failed to send notification to Telegram chat with error: {e}"

    return result

def send_to_whatsapp(link, phone_number):
    try:
        url = f"https://graph.facebook.com/v13.0/107494948909422/messages"
        headers = {
            "Authorization": f"Bearer EAAMuz7x1mk0BAFu7oJIwNaVrvFZCFHIvwAasLLnsRMVldanEZCoQqrb1ZB1RaUrBYyr0nLBpIlfl6xEIR4MZB1w7V3QfKm4VpWQOQIZASxA4JmZA43IJqX0ZAlZAI1iZAlrH3pZBXikXInPnzdTlwrMeF6E6MUz9L9nEXle8PkcFQlzfxWV2wIVnN8",
            'Content-Type': 'application/json'
        }

        data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "image",
        "image": {
            "link" : link,
            "caption":"Aksha Alert"
        }
        }
        rr = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        result = "Notification sent on registered whats app number successfully!"
    except Exception as e:
        result = f"Failed to send notification on whats app with error: {e}"

    return result

def email(subscription:str, recipients:list, camera:str, Type:str, DataPath:str,Timestamp:str,alert_notification_validity:list=None, alert:list=None, description:list=None):

    try:
        # Define these once; use them twice!
        strFrom = f'cctv.alerts+{subscription}@algoanalytics.com'

        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = f'CCTV {Type} Notification'
        msgRoot['From'] = strFrom
        msgRoot['To'] = ", ".join(recipients) 
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('This is the alternative plain text message.')
        msgAlternative.attach(msgText)
        # This example assumes the image is in the current directory
        fp = open(resource_path('logo.png'), 'rb')
        msgImage = MIMEImage(fp.read())
        fp = open(resource_path('logo2.png'), 'rb')
        msgImage2 = MIMEImage(fp.read())
        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msgImage2.add_header('Content-ID', '<image2>')

        Email_Format = ""
        if Type =="Alert" or Type == "No Object Alert":
            Alert_Details = []
            for alert_name, alert_details, validity in zip(alert, description, alert_notification_validity):
                if validity:
                    Alert_Details.append(f'<span style="line-height:30px;"><strong>Alert Name :</strong> {alert_name}</span><br> <span style="line-height:30px;"><strong>Alert description : </strong>{alert_details}</span><br>')
            #Email body for Alert format
            Email_Format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>My alert email</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            
                            <div 
                            style="font-family:sans-serif;background:#dddd;width:100%;padding:49px 20px">
                                <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src="cid:image1" style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src="cid:image2" style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha User, <br><br>
                                    Please check with alert details. <br><br>
                                    <p style="margin-bottom: 9px;">My Alert</p>
                                
                                    <span style="line-height:30px;"><strong>Camera :</strong> {camera}</span><br>
                                    {" ".join(Alert_Details)}
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                    <table>
                                    <tr>
                                        <td>
                                            <img src="cid:image5" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </p>
                                </div>
                            </div>

                        </body>
                    </html>
                    """   
            fp = open(f'{DataPath}/alerts/{Timestamp}_alert.jpg', 'rb')
            msgImage5 = MIMEImage(fp.read())
            fp.close()  
            msgImage5.add_header('Content-ID', '<image5>')
            msgRoot.attach(msgImage)
            msgRoot.attach(msgImage2)
            msgRoot.attach(msgImage5)

        else:
            #Email body for Anomaly format
            Email_Format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Anomaly email Template</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            <div 
                            style="font-family:sans-serif;background:#dddd;width:100%;padding:49px 20px">
                                <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src="cid:image1" style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src="cid:image2" style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha User, <br><br>
                                    Aksha has come across this unusual situation for {camera}, please check with Image <br><br>
                                </p>
                                <p>
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                </p>
                                <table>
                                    <tr>
                                        <td>
                                            <img src="cid:image3" alt="my alert" style="max-width:100%;">
                                        </td>
                                        
                                    </tr>
                                    <tr>
                                        <td>
                                            <img src="cid:image4" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </div>
                            </div>

                        </body>
                        </html>
                        """
            fp = open(f'{DataPath}/frame/{Timestamp}.jpg', 'rb')
            msgImage3 = MIMEImage(fp.read())
            fp = open(f'{DataPath}/alerts/{Timestamp}_autoalert.jpg', 'rb')
            msgImage4 = MIMEImage(fp.read())
            fp.close()
            # fp = open(f'{DataPath}/alerts/{Timestamp}_alert.jpg', 'rb')
            # msgImage5 = MIMEImage(fp.read())
            fp.close()       
            # We reference the image in the IMG SRC attribute by the ID we give it below
            msgImage3.add_header('Content-ID', '<image3>')
            msgImage4.add_header('Content-ID', '<image4>')
            # msgImage5.add_header('Content-ID', '<image5>')
            msgRoot.attach(msgImage)
            msgRoot.attach(msgImage2)
            msgRoot.attach(msgImage3)
            msgRoot.attach(msgImage4)
            # msgRoot.attach(msgImage5)
            # msgAlternative.attach(msgText)
        msgText = MIMEText(Email_Format, 'html')
        msgAlternative.attach(msgText)
 
        # Send the email (this example assumes SMTP authentication is required)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.set_debuglevel(1)
        smtp.starttls() #enable security
        smtp.login("cctv.alerts@algoanalytics.com", "Algo123$")
        smtp.sendmail(strFrom, recipients, msgRoot.as_string())
        smtp.quit()

    except Exception as e:
        return f"Error encountered while sending mail to Camera : {camera}, with following exception {e}"

def whatsapp(subscription: str, camera:str, Type:str, DataPath:str, Timestamp:str, sas_url:str, folder_id:str, alert_notification_validity:list=None, alert:list=None, description:list=None, whats_app_service:dict={"service_status": False, "contact_number": None}):


    try:
        Whatsapp_Format = ""
        if Type =="Alert" or Type == "No Object Alert":
            Alert_Details = []
            for alert_name, alert_details, validity in zip(alert, description, alert_notification_validity):
                if validity:
                    Alert_Details.append(f'<span style="line-height:30px;"><strong>Alert Name :</strong> {alert_name}</span><br> <span style="line-height:30px;"><strong>Alert description : </strong>{alert_details}</span><br>')
            Whatsapp_Format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
			            <meta name="imgkit-format" content="png"/>
			            <meta name="imgkit-orientation" content="Portrait"/>
                        <title>My alert email</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            
                            
                                <div style="max-width:554px;margin:0 auto;padding: 35px; background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src={resource_path('logo.png')} style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src={resource_path('logo2.png')} style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha User, <br><br>
                                    Please check with alert details. <br><br>
                                    <p style="margin-bottom: 9px;">My Alert</p>
                                
                                    <span style="line-height:30px;"><strong>Camera :</strong> test2</span><br>
                                    <span style="line-height:30px;"><strong>Alert Name :</strong> nope</span><br> <span style="line-height:30px;"><strong>Alert description : </strong>please</span><br>
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                    <table>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/alerts/{Timestamp}_alert.jpg" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </p>
                                </div>
                            

                        </body>
                    </html>
                    """    
        else:
            Whatsapp_Format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="imgkit-format" content="png"/>
                        <meta name="imgkit-orientation" content="Portrait"/>
                        <title>My alert email</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            
                            
                                <div style="max-width:554px;margin:0 auto;padding: 35px; background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src={resource_path('logo.png')} style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src={resource_path('logo2.png')} style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha User, <br><br>
                                    Aksha has come across this unusual situation for {camera}, please check with Image <br><br>
                                </p>
                                <p>
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                </p>
                                <table>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/frame/{Timestamp}.jpg" alt="my alert" style="max-width:100%;">
                                        </td>
                                        
                                    </tr>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/alerts/{Timestamp}_autoalert.jpg" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </div>
                            

                        </body>
                    </html>
                    """
        try:
            
            if whats_app_service["service_status"]:
                whats_app_body = open("notification_whatsapp.html","w")
                whats_app_body.write(Whatsapp_Format)
                whats_app_body.close()
                options = {'enable-local-file-access': None}
                imgkit.from_file('notification_whatsapp.html', 'notification_whatsapp.jpg', options = options)
                notification_image_url = get_download_url(folder_id, "notification_whatsapp.jpg")
                wap_response = send_to_whatsapp(notification_image_url, whats_app_service["contact_number"], sas_url)
            else:
                print('Whatsapp service not activated')
        except Exception as e:
            wap_response = f"whats app service failed with exception : {e}"

    except Exception as e:
        return f"Error encountered while sending whatsapp alert to Camera : {camera}, with following exception {e}"

def telegram(subscription: str, camera:str, Type:str, DataPath:str, Timestamp:str, alert_notification_validity:list=None, alert:list=None, description:list=None,telegram_service:dict={"service_status":False, "chat_ids": None, "bot_token":None}):


    try:
        telegram_format = ""
        if Type =="Alert" or Type == "No Object Alert":
            Alert_Details = []
            for alert_name, alert_details, validity in zip(alert, description, alert_notification_validity):

                if validity:
                    Alert_Details.append(f'<span style="line-height:30px;"><strong>Alert Name :</strong> {alert_name}</span><br> <span style="line-height:30px;"><strong>Alert description : </strong>{alert_details}</span><br>')
    
            telegram_format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>My alert email</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            
                            <div 
                            style="font-family:sans-serif;background:#dddd;padding:49px 20px">
                                <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src={resource_path('logo.png')} style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src={resource_path('logo2.png')} style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha user, <br><br>
                                    Please check with alert details. <br><br>
                                    <p style="margin-bottom: 9px;">My Alert</p>
                                
                                    <span style="line-height:30px;"><strong>Camera :</strong> {camera}</span><br>
                                    {" ".join(Alert_Details)}
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                    <table>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/alerts/{Timestamp}_alert.jpg" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </p>
                                </div>
                            </div>

                        </body>
                    </html>
                    """   
            
        else:

            telegram_format = f"""<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Anomaly email Template</title>
                        </head>
                        <body style="margin:0;padding:0;">
                            <div 
                            style="font-family:sans-serif;background:#dddd;padding:49px 20px">
                                <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                <table>
                                    <tr>
                                    <td> 
                                        <img src={resource_path('logo.png')} style="max-width:127px;position:relative;left:-7px;" alt="">
                                    </td>
                                    <td style="width:300px;"></td>
                                    <td> <img src={resource_path('logo2.png')} style="max-width:127px;" alt=""></td>
                                    </tr>
                                </table>
                                <p style="font-size:18px;padding-top:10px;">
                                    Dear Aksha User, <br><br>
                                    Aksha has come across this unusual situation for {camera}, please check with Image <br><br>
                                </p>
                                <p>
                                    <span style="line-height:30px;"><strong>Camera Images : </strong></span><br>
                                </p>
                                <table>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/frame/{Timestamp}.jpg" alt="my alert" style="max-width:100%;">
                                        </td>
                                        
                                    </tr>
                                    <tr>
                                        <td>
                                            <img src="{DataPath}/alerts/{Timestamp}_autoalert.jpg" alt="my alert" style="max-width:250px;">
                                        </td>
                                    </tr>
                                    </table>
                                </div>
                            </div>

                        </body>
                        </html>
                        """

        try:
            if telegram_service["service_status"]:
                telegram_body = open("notification_telegram.html","w")
                telegram_body.write(telegram_format)
                telegram_body.close()
                options = {'enable-local-file-access': None}
                imgkit.from_file('notification_telegram.html', 'notification_telegram.jpg',options)
                chat_ids = telegram_service["chat_ids"]
                bot_token = telegram_service["bot_token"]
                for ids in chat_ids:
                    tg_response = send_to_telegram("notification_telegram.jpg", ids, bot_token)
                    print(ids)
            else:
                print('Telegram service not activated')
        except Exception as e:
            tg_response = f"telegram service failed with exception : {e}"
        
        return f"Alert on telegram Sent successfully! {tg_response}"
    except Exception as e:
        return f"Error encountered while sending telegram alert to Camera : {camera}, with following exception {e}"

def send(subscription: str, recipients:list, camera:str, Type:str, DataPath:str, Timestamp:str, sas_url:str, folder_id:str, alert_notification_validity:list=None, alert:list=None, description:list=None, whats_app_service:dict={"service_status": False, "contact_number": None},telegram_service:dict={"service_status":False, "chat_ids": None}):
    DataPath = f'{DataPath}{camera}'
    result_email = email(subscription, recipients, camera, Type, DataPath,Timestamp,alert_notification_validity, alert, description)
    result_whatsapp = whatsapp(subscription, camera, Type, DataPath, Timestamp, sas_url, folder_id, alert_notification_validity, alert, description, whats_app_service)
    result_telegram = telegram(subscription, camera, Type, DataPath, Timestamp, alert_notification_validity, alert, description,telegram_service)

    return result_email, result_whatsapp, result_telegram

def error_notification(subscription:str, Type:str, recipients:list, camera:str, RTSP_Link:str, RTSP_Down:bool):
    try:
            # Define these once; use them twice!
            strFrom = f'cctv.alerts+{subscription}@algoanalytics.com'
            recipients.append("aksha@algoanalytics.com")

            # Create the root message and fill in the from, to, and subject headers
            msgRoot = MIMEMultipart('related')
            msgRoot['Subject'] = f'CCTV Notification - {Type}'
            msgRoot['From'] = strFrom
            msgRoot['To'] = ", ".join(recipients)
            msgRoot.preamble = 'This is a multi-part message in MIME format.'

            # Encapsulate the plain and HTML versions of the message body in an
            # 'alternative' part, so message agents can decide which they want to display.
            msgAlternative = MIMEMultipart('alternative')
            msgRoot.attach(msgAlternative)

            msgText = MIMEText('This is the alternative plain text message.')
            msgAlternative.attach(msgText)
            # This example assumes the image is in the current directory
            fp = open(resource_path('logo.png'), 'rb')
            msgImage = MIMEImage(fp.read())
            fp = open(resource_path('logo2.png'), 'rb')
            msgImage2 = MIMEImage(fp.read())
            # Define the image's ID as referenced above
            msgImage.add_header('Content-ID', '<image1>')
            msgImage2.add_header('Content-ID', '<image2>')
            msgRoot.attach(msgImage)
            msgRoot.attach(msgImage2)
            if not RTSP_Down:
                Email_Format = f"""<!DOCTYPE html>
                            <html lang="en">
                            <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>My alert email</title>
                            </head>
                            <body style="margin:0;padding:0;">
                                
                                <div 
                                style="font-family:sans-serif;background:#dddd;width:100%;padding:49px 20px">
                                    <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                    <table>
                                        <tr>
                                        <td> 
                                            <img src="cid:image1" style="max-width:127px;position:relative;left:-7px;" alt="">
                                        </td>
                                        <td style="width:300px;"></td>
                                        <td> <img src="cid:image2" style="max-width:127px;" alt=""></td>
                                        </tr>
                                    </table>
                                    <p style="font-size:18px;padding-top:10px;">
                                        Dear Aksha User, <br><br>
                                        <span style="line-height:30px;"><strong>Camera :</strong> {camera}</span><br>
                                        {f"RTSP link : '{RTSP_Link}'"}<br> is back in service. <br>

                                        CCTV is now under AI Surveillance! <br><br>
                                    </p>
                                    </div>
                                </div>

                            </body>
                        </html>
                        """   
            else:
                Email_Format = f"""<!DOCTYPE html>
                            <html lang="en">
                            <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>My alert email</title>
                            </head>
                            <body style="margin:0;padding:0;">
                                
                                <div 
                                style="font-family:sans-serif;background:#dddd;width:100%;padding:49px 20px">
                                    <div style="max-width:535px;margin:0 auto;padding:38px;background:#fff; box-shadow: 26px 56px 43px #ddd;border-radius: 10px;">
                                    <table>
                                        <tr>
                                        <td> 
                                            <img src="cid:image1" style="max-width:127px;position:relative;left:-7px;" alt="">
                                        </td>
                                        <td style="width:300px;"></td>
                                        <td> <img src="cid:image2" style="max-width:127px;" alt=""></td>
                                        </tr>
                                    </table>
                                    <p style="font-size:18px;padding-top:10px;">
                                        Dear Aksha User, <br><br>
                                        <span style="line-height:30px;"><strong>Camera :</strong> {camera}</span><br>
                                        {f"RTSP link : '{RTSP_Link}'"}<br> Facing connection error. <br>

                                        Please check RTSP links, make sure it is working! <br><br>
                                    </p>
                                    </div>
                                </div>

                            </body>
                        </html>
                        """   
        

            msgText = MIMEText(Email_Format, 'html')
            msgAlternative.attach(msgText)
    
            # Send the email (this example assumes SMTP authentication is required)

            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.set_debuglevel(1)
            smtp.starttls() #enable security
            smtp.login("cctv.alerts@algoanalytics.com", "Algo123$")
            smtp.sendmail(strFrom, recipients, msgRoot.as_string())
            smtp.quit()

    except Exception as e:
        print(f"Error encountered while sending mail to Camera : {camera}, with following exception {e}")
