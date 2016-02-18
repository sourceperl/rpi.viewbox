#!/usr/bin/env python2.7

import imaplib
import json
import time
import schedule
import paho.mqtt.publish as publish

# Retrieve unseen mail number from IMAP server.

def mail_job():
    M = imaplib.IMAP4_SSL("imap.free.fr", 993)
    M.login(<username>, <password>)
    M.select()
    (retcode, messages) = M.search(None, "(UNSEEN)")
    if retcode == "OK":
        msg = {}
        msg['value'] = len(messages[0].split())
        msg['update'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        publish.single("pub/mail/loic.celine/unread", json.dumps(msg), 
                       hostname="192.168.1.60")
    M.close()

# schedule conf.
schedule.every(5).minutes.do(mail_job)

# main loop
while True:
    schedule.run_pending()
    time.sleep(1)
