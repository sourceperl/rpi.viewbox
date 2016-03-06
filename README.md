Raspberry Pi ViewBox
====================

A Raspberry Pi with an 20 chars x 4 lines I2C LCD screen (with PCF8574 chip).

The viewbox display temperature, pressure from a garden weather station, it
display also the level of "vigilance meteo" (weather alert french system). All
this informations are available on a local MQTT broker.

A script check regulary the number of unread mail on an IMAP server. The result
is also display on the panel.

Setup
-----

## Python

### PyPi lib

    sudo pip3 install -r requirements.txt

### Github lib (LCD driver)

    git clone https://github.com/sourceperl/rpi.lcd-i2c.git
    cd rpi.lcd-i2c
    sudo python3 setup.py install

## Bin

    sudo cp usr/local/bin/* /usr/local/bin

## Supervisor

    sudo apt-get install supervisor
    sudo cp etc/supervisor/conf.d/* /etc/supervisor/conf.d/
    sudo supervisorctl update

