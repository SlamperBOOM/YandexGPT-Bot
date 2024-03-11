#!/bin/bash
cd /home/slamper/
mkdir yandexgptbot
cd yandexgptbot/
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
python3 -m pip install aiogram
python3 -m pip install requests
python3 -m pip install jsonpickle
cp ../*.py .
python3 GPTBot.py
