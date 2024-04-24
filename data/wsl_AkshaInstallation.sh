echo "Welcome to Aksha(AI Powered Surveillance) powered by AlgoAnalytics Pvt. Ltd"
echo "Initiating the installation process......."

mongod --shutdown

rm -r Aksha & mkdir Aksha || mkdir Aksha

docker kill $(sudo docker ps -q)
docker system prune -f

echo "Intiallation Started...."

cd Aksha

echo "Resource Loading ......"
# curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/avatar.png -O avatar.png
# curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/user.png -O user.png
curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/labels.txt -O labels.txt

curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/store_reference_img.py -O store_reference_img.py
curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/wsl_daemon_monitor.py -O daemon_monitor.py

# presigned URL comes here
# rtsp file URL
# app.config file URL

touch daemon_stat.log

curl https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/docker-compose.yml -O docker-compose.yml
docker login -u dockerhubalgo -p Aksha123#

docker pull dockerhubalgo/surveillance:latest

docker-compose up -d

rm docker-compose.yml

daemon_dir=$(pwd)

# Ubuntu specific, for windows OS we need to update Task Service
# (sudo crontab -l ; echo "*/15 * * * * /usr/bin/python3 $daemon_dir/daemon_monitor.py $daemon_dir/Aksha") | crontab -
# echo "cron tab added"

echo "Installation completed!"
    
docker ps

echo "AI surveillance network started successfully"

./Aksha

docker logout
