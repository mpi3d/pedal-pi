#!/bin/bash
clear
dir=`pwd`
cd $dir
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
