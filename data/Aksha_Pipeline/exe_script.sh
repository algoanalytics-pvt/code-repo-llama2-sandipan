#!/bin/bash

echo Creating Virtual Environment !!

sudo  apt install python3.8-venv
python3.8 -m venv ./aksha-venv
source aksha-venv/bin/activate
pip3 install -r requirements.txt
pip3 install https://github.com/pyinstaller/pyinstaller/tarball/develop

echo Virtual enironment created with all the requirements!!
echo Creating the executable using pyinstaller

python3.8 -m PyInstaller \
   --add-data="./coco.names:." \
   --add-data="./LOADING_IMG.png:." \
   --add-data="./RTSP_ISSUE_IMG.png:." \
   --add-data="./logo.png:." \
   --add-data="./logo2.png:." \
   --add-binary="./yolov7.onnx:." \
   --hidden-import="sklearn" \
   --hidden-import="sklearn.ensemble._iforest" \
   ./main.py --debug=all --onefile --clean

cp ./dist/main ./

echo Creating the dockerimage using the executable
sudo docker pull ubuntu:20.04
sudo docker build -t surveillance:latest .
sudo docker tag surveillance:latest dockerhubalgo/surveillance:latest
rm main
rm -rf aksha-venv
