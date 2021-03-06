'''Send SMTP email alerts in case of sump pump failure.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import os
import time
import smtplib
from datetime import datetime
try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3
from collections import deque
import csv
from raspisump import log


config = configparser.RawConfigParser()

config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'email_to': config.get('email', 'email_to'),
           'email_from': config.get('email', 'email_from'),
           'smtp_authentication': config.getint(
               'email', 'smtp_authentication'),
           'smtp_tls': config.getint('email', 'smtp_tls'),
           'smtp_server': config.get('email', 'smtp_server'),
           'username': config.get('email', 'username'),
           'password': config.get('email', 'password'),
           'unit': config.get('pit', 'unit'),
           'pit_depth': config.get('pit', 'pit_depth')
           }

# If item in raspisump.conf add to configs dict above.  If not then provide
# a default value
try:
    configs['alert_interval'] = config.getint('email', 'alert_interval')
except configparser.NoOptionError:
    configs['alert_interval'] = 5

# same idea as above.
try:
    configs['alert_when'] = config.get('pit', 'alert_when')
except configparser.NoOptionError:
    configs['alert_when'] = 'high'


def unit_types():
    '''Determine  if inches or centimeters'''

    unit = configs['unit']

    if unit == 'imperial':
        return 'inches'
    if unit == 'metric':
        return 'centimeters'

def email_content(water_depth):
    '''Build the contents of email body which will be sent as an alert'''

    time_of_day = time.strftime('%I:%M%P %Z')
    unit_type = unit_types()
    pit_depth = int(configs['pit_depth'])
    water_gap = round((pit_depth-water_depth),1) # distance between the top of the pit and the water level
    email_contents = {'subject_high': 'Subject: Sump Pump Alert!',
                      'subject_low': 'Subject: Low Water Level Alert!',
                      'message_high': 'Critical! The sump pit water level is',
                      'message_low': 'Warning! The waterlevel is down to'
                      }

    if configs['alert_when'] == 'high':
        subject = email_contents['subject_high']
        message = email_contents['message_high']
    else:
        subject = email_contents['subject_low']
        message = email_contents['message_low']

    return "\r\n".join((
        "From: {}".format(configs['email_from']),
        "To: {}".format(configs['email_to']),
        "{}".format(subject),
        "",
        "{} - {} {} {}, {} {} from floor level.".format(time_of_day, message, str(water_depth), unit_type, str(water_gap), unit_type),
        "Sump pit depth is {} inches".format(configs['pit_depth']),
        "Next alert in {} minutes".format(configs['alert_interval']),
        )
        )



def smtp_alerts(water_depth):
    '''Send email alert if water level greater than critical distance.'''
    recipients = configs['email_to'].split(', ')
    email_body = email_content(water_depth)
    server = smtplib.SMTP(configs['smtp_server'])

    # Check if smtp server uses TLS
    if configs['smtp_tls'] == 1:
        server.starttls()
    else:
        pass
    # Check if smtp server uses authentication
    if configs['smtp_authentication'] == 1:
        username = configs['username']
        password = configs['password']
        server.login(username, password)
    else:
        pass

    server.sendmail(configs['email_from'], recipients, email_body)
    server.quit()


def determine_if_alert(water_depth):
    '''Determine if an alert is required.  Only send if last alert has been
    sent more than the amount of time identified in the raspisump.conf file.
    Entry in conf file is alert_interval under the [email] section.'''

    alert_interval = configs['alert_interval']

    alert_log = '/home/pi/raspi-sump/logs/alert_log'

    if not os.path.isfile(alert_log):
        smtp_alerts(water_depth)
        log.log_alerts('Email SMS Alert Sent')

    else:
        with open(alert_log, 'rt') as f:
            last_row = deque(csv.reader(f), 1)[0]
            last_alert_sent = last_row[0]
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            last_alert_time = datetime.strptime(
                last_alert_sent, '%Y-%m-%d %H:%M:%S'
            )
            time_now = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
            delta = (time_now - last_alert_time)
            minutes_passed = delta.seconds / 60
            
        if minutes_passed >= alert_interval:
            smtp_alerts(water_depth)
            log.log_alerts('Email SMS Alert Sent')

        else:
            pass
