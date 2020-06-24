# !/bin/bash
clear
dir=`pwd`
cd $dir
#sudo apt-get install mosquitto -y
#sudo pip3 install pexpect paho-mqtt
#sudo /etc/mosquitto/passwd
#sudo mosquitto_passwd -b /etc/mosquitto/passwd pedal_pi "effect[~~~~]"
#sudo bash -c 'echo "password_file /etc/mosquitto/passwd
#allow_anonymous false
#listener 1883
#listener 1884
#protocol websockets" >> /etc/mosquitto/mosquitto.conf'
#sudo service mosquitto restart
#wget https://raw.githubusercontent.com/eclipse/paho.mqtt.javascript/master/src/paho-mqtt.js
sudo apt-get install cmake -y
wget https://github.com/warmcat/libwebsockets/archive/master.zip http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
unzip master.zip
tar xvfz bcm2835-1.50.tar.gz
cd $dir/libwebsockets-master
cmake .
make
sudo make install
cd $dir/bcm2835-1.50
./configure
make
sudo make install
cd $dir
cp $dir/bcm2835-1.50/src/bcm2835.o $dir/bcm2835.o
rm -rf $dir/master.zip $dir/libwebsockets-master $dir/bcm2835-1.50.tar.gz $dir/bcm2835-1.50
for file in $dir/pedals/*
do
    gcc $file -o `echo "$file" | cut -d'.' -f1` -l bcm2835
done
