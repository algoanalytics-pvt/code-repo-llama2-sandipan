#!/bin/bash

echo Creating Virtual Environment !!

sudo apt install python3.8-venv
python3.8 -m venv ./anomaly-env
source anomaly-env/bin/activate
pip3 install -r requirements.txt
pip3 install https://github.com/pyinstaller/pyinstaller/tarball/develop

echo Virtual enironment created with all the requirements!!
echo Creating the executable using pyinstaller

python3.8 -m PyInstaller \
   ./main.py --debug=all --onefile --clean

cp ./dist/main ./

echo Creating the dockerimage using the executable
sudo docker pull ubuntu:20.04
sudo docker build -t anomaly_trainer:latest .
sudo docker tag anomaly_trainer:latest dockerhubalgo/anomaly-trainer:latest
rm main
rm -rf anomaly-env
