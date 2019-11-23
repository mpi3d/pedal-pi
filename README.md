# Pedal Pi

Pedal effects for guitar who use Raspberry Pi 0, the [Pedal-Pi](https://www.electrosmash.com/pedal-pi) and programmed in C

[![Pedal Pi](/Pedal_Pi.jpg)](https://www.electrosmash.com/pedal-pi)

## Shop

+ [Pedal Pi](https://shop.electrosmash.com/product/pedal-pi-kit/)

## Pedals Effects

+ [Pedals Effects](/Pedals_Effects)

## Installation

Install BCM2835

```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.50.tar.gz
tar xvfz bcm2835-1.50.tar.gz
cd bcm2835-1.50
./configure
make
sudo make install
```

## Running

Compile

`gcc -o {Output name} -l rt {Program}.c -l bcm2835`

Running

`sudo ./{Output name}`
