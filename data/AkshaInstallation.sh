echo "Welcome to Aksha(AI Powered Surveillance) powered by AlgoAnalytics Pvt. Ltd" 

echo "Initiating the installation process......."
 
sudo service mongodb stop

sudo rm -r Aksha & sudo mkdir Aksha || sudo mkdir Aksha

sudo docker kill $(sudo docker ps -q) 

sudo docker system prune -f 

echo "Intiallation Started...."

cd Aksha


echo "Resource Loading ......"

# ubnutu specific
sudo wget https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/labels.txt
# sudo wget https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/avatar.png
# sudo wget https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/user.png

# executables files
# sudo wget https://aksha.blob.core.windows.net/aksha-resources/Aksha

sudo wget https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/store_reference_img.py
sudo wget https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/daemon_monitor.py

# presigned URL comes here
# rtsp file URL
# app.config file URL

pip install Pillow requests opencv-python
python store_reference_img.py

touch daemon_stat.log

cd ..

sudo https://aksha-storage.s3.ap-south-1.amazonaws.com/aksha-resources/docker-compose.yml
sudo docker login -u dockerhubalgo -p Aksha123#

sudo docker pull dockerhubalgo/surveillance:latest

sudo docker-compose up -d

sudo rm docker-compose.yml

daemon_dir=$(pwd)

sudo python store_reference_img.py
# Ubuntu specific, for windows OS we need to update Task Service
(sudo crontab -l ; echo "*/15 * * * * /usr/bin/python3 $daemon_dir/daemon_monitor.py $daemon_dir/Aksha") | crontab -
echo "cron tab added"

echo "Installation completed!"
    
sudo docker ps

echo "AI surveillance network started successfully"

./Aksha

sudo docker logout
