import json
import os
import argparse
import surveillance

# Command line arguments for main function

parser = argparse.ArgumentParser()
parser.add_argument('--env',
                    help="Please enter environment", default=os.environ.get("ENVIRONMENT"))
parser.add_argument('--camera_name',
                    help="Please enter camera name", default=os.environ.get("CAMERA_NAME"))
parser.add_argument('--update_camera_name',
                    help="Please enter new camera name", default=os.environ.get("UPDATE_CAMERA_NAME"))
parser.add_argument('--rtsp_id',
                    help="Please enter rtsp unique id", default=os.environ.get("RTSP_ID"))
parser.add_argument('--video_path',
                    help="Path of video file: rtsp link", type=str, default=os.environ.get("RTSP_LINK"))
parser.add_argument('--output_size',
                    help='Optional. The first image size used for CTPN model reshaping. '
                    'Default: 160, 90. Note that submitted images should have the same resolution, '
                    'otherwise predictions might be incorrect.', type=int, default=(640, 360), nargs=2,)
parser.add_argument('--object_detection',
                    help="Optional. Don't show output.", type=bool, default=os.environ.get("OBJECT_DETECTION"))
parser.add_argument('--anomaly_detetion',
                    help="Optional. Don't show output.", type=bool, default=os.environ.get("ANOMALY_DETECTION"))
parser.add_argument('--skip_fps_sec',
                    help="Please enter inferance interval in sec.", type=float, default=os.environ.get("SKIP_INTERVAL"))
parser.add_argument('--prefilter_threshold',
                    help="Define prefilter threshold", type=float, default=0.95)
parser.add_argument('--my_alerts',
                    help="Define customized Alerts list eg:- --my_alerts 'Alert1 Alert2 Alert3'",  type=str, default=os.environ.get("MY_ALERTS"))
parser.add_argument('--autoalert_notification_email_service',
                   help="Enable email notification service for Autoalerts",  type=bool, default=os.environ.get("AUTOALERT_EMAIL_NOTIFICATION_SERVICE"))
parser.add_argument('--whats_app_service',
                    help="Enable whats app service", type=str, default=os.environ.get("WHATS_APP_SERVICE"))
parser.add_argument('--telegram_service',
                    help="Enable telegram service", type=str, default=os.environ.get("TELEGRAM_SERVICE"))
parser.add_argument('--crowd_threshold',
                    help="Enable crowd_threshold", type=int, default=6)
parser.add_argument('--time_delta',
                    help="Please enter deletion data retention period in days.", type=int, default=10)
parser.add_argument('--autoalert_display',
                   help="Enable Autoalerts display on monitor screen",  type=bool, default=os.environ.get("AUTOALERT_DISPLAY"))
parser.add_argument('--email_alert',
                   help="Enable email notification service for Alerts",  type=bool, default=os.environ.get("EMAIL_ALERT"))
parser.add_argument('--alert_display',
                   help="Enable Alerts display on monitor screen",  type=bool, default=os.environ.get("ALERT_DISPLAY"))
args = parser.parse_args()

whats_app_service = args.whats_app_service.lower() == "true" if args.whats_app_service is not None else None
telegram_service = args.telegram_service.lower() == "true" if args.telegram_service is not None else None


    #return whats_app_service
# Load Environment
with open(args.env, 'r') as f:
    config = json.load(f)    


if __name__ == '__main__':

    surveillance.Run(config, args.camera_name, args.update_camera_name, args.rtsp_id, args.my_alerts, 
                     args.whats_app_service, args.telegram_service, args.video_path, args.skip_fps_sec, 
                     args.output_size, args.object_detection, args.prefilter_threshold, 
                     args.autoalert_notification_email_service, args.crowd_threshold, args.time_delta, 
                     args.autoalert_display, args.email_alert, args.alert_display)