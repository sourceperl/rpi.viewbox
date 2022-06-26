#!/usr/bin/env python3

import time
import json
from typing import Any
import schedule
import paho.mqtt.client as mqtt
import RPi_I2C_LCD


# some const
VIG_LVL = {1: 'V', 2: 'J', 3: 'O', 4: 'R'}


# some class
class ValueUpd:
    """A value with an up-to-date flag."""

    def __init__(self, value: Any = None, ttl: int = 3600) -> None:
        # public
        self.ttl = ttl
        # private
        self._value = None
        self._update_t = 0
        # properties
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self._value = value
            self._update_t = time.monotonic()

    @property
    def up(self) -> bool:
        return self._update_t + self.ttl > time.monotonic()


# global vars
vig_59 = ValueUpd('I', ttl=3600)
vig_62 = ValueUpd('I', ttl=3600)
p_atmo = ValueUpd(0.0, ttl=3600)
t_atmo = ValueUpd(0.0, ttl=3600)
nb_mail = ValueUpd(0, ttl=900)


class CustomMQTT(mqtt.Client):
    def on_connect(self, client, userdata, flags, rc):
        # subscribe to topics here for redo after disconnect
        client.subscribe('pub/meteo_vig/dep/59')
        client.subscribe('pub/meteo_vig/dep/62')
        client.subscribe('pub/metars/lesquin')
        client.subscribe('pub/mail/loic.celine/unread')

    def on_message(self, client, userdata, msg):
        # global vars
        global vig_59, vig_62, p_atmo, t_atmo, nb_mail
        # try to update values
        try:
            # process payload (json -> dict)
            msg_pld_d = json.loads(msg.payload.decode())
            # process topics
            if msg.topic == 'pub/meteo_vig/dep/59':
                vig_59.value = VIG_LVL.get(msg_pld_d['value'], None)
            elif msg.topic == 'pub/meteo_vig/dep/62':
                vig_62.value = VIG_LVL.get(msg_pld_d['value'], None)
            elif msg.topic == 'pub/metars/lesquin':
                t_atmo.value = float(msg_pld_d['temp'])
                p_atmo.value = float(msg_pld_d['press'])
            elif msg.topic == 'pub/mail/loic.celine/unread':
                nb_mail.value = int(msg_pld_d['value'])
        except:
            pass


def lcd_job():
    # global vars
    global vig_59, vig_62, p_atmo, t_atmo, nb_mail
    # format vars for display
    now = int(time.time())
    p_atmo_lcd = f'{p_atmo.value:7.2f}' if p_atmo.up else '?'
    t_atmo_lcd = f'{t_atmo.value:7.2f}' if t_atmo.up else '?'
    vig_59_lcd = vig_59.value if vig_59.up else '?'
    vig_62_lcd = vig_62.value if vig_62.up else '?'
    mail_nb_lcd = f'{nb_mail.value}' if nb_mail.up else '?'
    mail_lbl_lcd = 'e-mails' if nb_mail.value > 1 else 'e-mail'
    # send result to LCD
    lcd.set_cursor(row=0)
    lcd.message(f'{p_atmo_lcd:>7} hPa     59:{vig_59_lcd}')
    lcd.set_cursor(row=1)
    lcd.message(f'{t_atmo_lcd:>7} C       62:{vig_62_lcd}')
    lcd.set_cursor(row=2)
    lcd.message(f'{mail_nb_lcd:>7} {mail_lbl_lcd}')
    lcd.set_cursor(row=3)
    lcd.message(time.strftime('%d/%m/%Y  %H:%M:%S', time.localtime()))


if __name__ == '__main__':
    # init LCD screen
    lcd = RPi_I2C_LCD.LCD()
    lcd.set_backlight(True)
    lcd.home()
    lcd.message('connect MQTT server')
    # init MQTT client
    client = CustomMQTT()
    # connect try loop
    while True:
        try:
            client.connect('192.168.1.60', port=1883, keepalive=30)
            break
        except OSError:
            time.sleep(5.0)
    # start MQTT I/O thread
    client.loop_start()
    # int scheduler
    schedule.every(.5).seconds.do(lcd_job)
    # main loop
    while True:
        schedule.run_pending()
        time.sleep(.1)
