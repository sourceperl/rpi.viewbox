#!/usr/bin/env python3

import time
import json
import threading
import schedule
import paho.mqtt.client as mqtt
import RPi_I2C_LCD

# global vars
vig_level = {
    1: 'V',
    2: 'J',
    3: 'O',
    4: 'R',
}
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


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('pub/meteo_vig/dep/59')
    client.subscribe('pub/meteo_vig/dep/62')
    client.subscribe('pub/house/garden/pressure_sea_level')
    client.subscribe('pub/house/garden/temperature')
    client.subscribe('pub/mail/loic.celine/unread')


def on_disconnect(client, userdata, rc):
    print('MQTT disconnect')


def on_message(client, userdata, msg):
    # global vars
    global vig_59, vig_59_up
    global vig_62, vig_62_up
    global p_atmo, p_atmo_up
    global t_atmo, t_atmo_up
    global nb_mail, nb_mail_up
    # process topic
    if msg.topic == 'pub/meteo_vig/dep/59':
        try:
            index = int(json.loads(msg.payload.decode())['value'])
            vig_59 = vig_level[index]
            vig_59_up = int(time.time())
        except:
            pass
    elif msg.topic == 'pub/meteo_vig/dep/62':
        try:
            index = int(json.loads(msg.payload.decode())['value'])
            vig_62 = vig_level[index]
            vig_62_up = int(time.time())
        except:
            pass
    elif msg.topic == 'pub/house/garden/pressure_sea_level':
        try:
            p_atmo = float(json.loads(msg.payload.decode())['value'])
            p_atmo_up = int(time.time())
        except:
            pass
    elif msg.topic == 'pub/house/garden/temperature':
        try:
            t_atmo = float(json.loads(msg.payload.decode())['value'])
            t_atmo_up = int(time.time())
        except:
            pass
    elif msg.topic == 'pub/mail/loic.celine/unread':
        try:
            nb_mail = int(json.loads(msg.payload.decode())['value'])
            nb_mail_up = int(time.time())
        except:
            pass


def lcd_job():
    # global vars
    global vig_59, vig_59_up
    global vig_62, vig_62_up
    global p_atmo, p_atmo_up
    global t_atmo, t_atmo_up
    global nb_mail, nb_mail_up
    # format and display
    now = int(time.time())
    # l1
    p_atmo_str = '%7.2f hPa' % p_atmo if (now - p_atmo_up < 360) else '      ? hPa'
    vig_59 = vig_59 if (now - vig_59_up < 3600) else str('?')
    line1 = str('%s     59:%c' % (p_atmo_str, vig_59)).ljust(20)[:20]
    # l2
    t_atmo_str = '%7.2f C' % t_atmo if (now - t_atmo_up < 360) else '      ? C'
    vig_62 = vig_62 if (now - vig_62_up < 3600) else str('?')
    line2 = str('%s       62:%c' % (t_atmo_str, vig_62)).ljust(20)[:20]
    # l3
    str_mail = str(nb_mail) if (now - nb_mail_up < 900) else '?'
    line3 = '%7s %s' % (str_mail, 'e-mails' if (nb_mail > 1) else 'e-mail')
    line3 = line3.ljust(20)[:20]
    # l4
    datetime = time.strftime('%d/%m/%Y  %H:%M:%S', time.localtime())
    line4 = (datetime).ljust(20)[:20]
    # send result to LCD
    lcd.set_cursor(row=0)
    lcd.message(line1)
    lcd.set_cursor(row=1)
    lcd.message(line2)
    lcd.set_cursor(row=2)
    lcd.message(line3)
    lcd.set_cursor(row=3)
    lcd.message(line4)

if __name__ == '__main__':
    # init LCD screen
    lcd = RPi_I2C_LCD.LCD()
    lcd.set_backlight(True)
    lcd.home()
    lcd.message('connect MQTT server')
    # init MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect('192.168.1.60', port=1883, keepalive=30)
    client.loop_start()
    # schedule conf.
    schedule.every(.5).seconds.do(lcd_job)
    # main loop
    while True:
        schedule.run_pending()
        time.sleep(.1)

