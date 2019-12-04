#!/bin/bash
clear
dir=`pwd`
cd $dir
sudo apt-get install mosquitto
sudo pip3 install pexpect paho-mqtt
sudo mosquitto_passwd -b /etc/mosquitto/passwd pedal-pi effect
sudo bash -c 'echo "password_file /etc/mosquitto/passwd
allow_anonymous false" >> /etc/mosquitto/mosquitto.conf
listener 1883
listener 1884
protocol websockets'
sudo service mosquitto restart
wget https://raw.githubusercontent.com/eclipse/paho.mqtt.javascript/master/src/paho-mqtt.js
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
tar xvfz bcm2835-1.50.tar.gz
cd bcm2835-1.50
./configure
make
sudo make install
cd $dir
for path in $dir/Pedals/*
do
    gcc -o `echo "$path" | cut -d'.' -f1` -l rt $path -l bcm2835
done
