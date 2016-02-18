#!/usr/bin/python

# Python script for populate YUN datastore

# misc lib
import time
import json
import threading
# MQTT lib
import paho.mqtt.client as mqtt
# Access to YUN datastore lib (bridge interface ARM <->ATmega)
import sys
import RPi_I2C_LCD

lcd = RPi_I2C_LCD.LCD()
lcd.set_backlight(True)

# first banner
lcd.set_cursor(row=0)
lcd.message("LCD 4x20 chars I2C")
lcd.set_cursor(row=1)
lcd.message("line 2")
lcd.set_cursor(row=2)
lcd.message("12345678901234567890")
lcd.set_cursor(row=3)
lcd.message("line 4")

exit()

# global vars
vig_level = {
    1: 'V',
    2: 'J',
    3: 'O',
    4: 'R',
}

th_lock = threading.Lock()
store = bridgeclient()
vig_59 = 'I'
vig_59_up = 0
vig_62 = 'I'
vig_62_up = 0
p_atmo = 0.0
p_atmo_up = 0
t_atmo = 0.0
t_atmo_up = 0
nb_mail = 0
nb_mail_up = 0


def on_connect(client, userdata, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("pub/meteo_vig/dep/59")
    client.subscribe("pub/meteo_vig/dep/62")
    client.subscribe("pub/house/garden/pressure_sea_level")
    client.subscribe("pub/house/garden/temperature")
    client.subscribe("pub/mail/loic.celine/unread")


def on_disconnect(client, userdata, rc):
    print("MQTT disconnect")


def on_message(client, userdata, msg):
    # global vars
    global vig_59, vig_59_up
    global vig_62, vig_62_up
    global p_atmo, p_atmo_up
    global t_atmo, t_atmo_up
    global vig_level
    global nb_mail, nb_mail_up
    # thread lock
    th_lock.acquire()
    # process topic
    if msg.topic == "pub/meteo_vig/dep/59":
        try:
            index = int(json.loads(msg.payload)['value'])
            vig_59 = vig_level[index]
            vig_59_up = int(time.time())
        except:
            pass
    elif msg.topic == "pub/meteo_vig/dep/62":
        try:
            index = int(json.loads(msg.payload)['value'])
            vig_62 = vig_level[index]
            vig_62_up = int(time.time())
        except:
            pass
    elif msg.topic == "pub/house/garden/pressure_sea_level":
        try:
            p_atmo = float(json.loads(msg.payload)['value'])
            p_atmo_up = int(time.time())
        except:
            pass
    elif msg.topic == "pub/house/garden/temperature":
        try:
            t_atmo = float(json.loads(msg.payload)['value'])
            t_atmo_up = int(time.time())
        except:
            pass
    elif msg.topic == "pub/mail/loic.celine/unread":
        try:
            nb_mail = int(json.loads(msg.payload)['value'])
            nb_mail_up = int(time.time())
        except:
            pass
    # thread unlock
    th_lock.release()


def main():
    # global vars
    global vig_59, vig_59_up
    global vig_62, vig_62_up
    global p_atmo, p_atmo_up
    global t_atmo, t_atmo_up
    global vig_level
    global nb_mail, nb_mail_up
    # init MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect("192.168.1.60", port=1883, keepalive=30)
    client.loop_start();
    while True:
        # main loop run every 300 ms
        time.sleep(0.3)
        # thread lock
        th_lock.acquire()
        # main loop
        now = int(time.time())
        # l1
        p_atmo = p_atmo if (now - p_atmo_up < 240) else float('nan')
        vig_59 = vig_59 if (now - vig_59_up < 3600) else str(' ')
        line1 = str("%7.2f hPa     59:%c" % (p_atmo, vig_59)).ljust(20)[:20]
        # l2
        t_atmo = t_atmo if (now - t_atmo_up < 240) else float('nan')
        vig_62 = vig_62 if (now - vig_62_up < 3600) else str(' ')
        line2 = str("%7.2f C       62:%c" % (t_atmo, vig_62)).ljust(20)[:20]
        # l3
        str_mail = str(nb_mail) if (now - nb_mail_up < 900) else ''
        line3 = "%7s %s" % (str_mail, 'e-mails' if (nb_mail > 1) else 'e-mail')
        line3 = line3.ljust(20)[:20]
        # l4
        datetime = time.strftime("%d/%m/%Y  %H:%M:%S", time.localtime())
        line4 = (datetime).ljust(20)[:20]
        # thread unlock
        th_lock.release()
        # send result to datastore
        store.put("str_bloc", line1 + line2 + line3 + line4)


if __name__ == '__main__':
    main()
    sys.exit(0)
