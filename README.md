Raspberry Pi ViewBox
====================

A Raspberry Pi with an 20 chars x 4 lines I2C LCD screen (with PCF8574 chip).

The viewbox display temperature, pressure from a garden weather station, it
display also the level of "vigilance meteo" (weather alert french system). All
this informations are available on a local MQTT broker.

A script check regulary the number of unread mail on an IMAP server. The result
is also display on the panel.

Requirements
------------

## Python

### PyPi lib

    sudo pip install -r requirements.txt

### Github lib

    git clone https://github.com/sourceperl/rpi.lcd-i2c.git
    cd rpi.lcd-i2c
    sudo python setup.py install


