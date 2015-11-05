#!/usr/bin/env python

import select, socket, urllib2, ConfigParser, logging, time
from slacker import Slacker

config = ConfigParser.RawConfigParser()
config.read('alarmbot.ini')

to_channel = config.get('config', 'to_channel')
my_name = config.get('config', 'my_name')
port = config.getint('config', 'port')
squelch = config.getint('config', 'squelch')
testing = config.getboolean('config', 'testing')
slack = Slacker(config.get('config', 'slack_api'))

bufferSize = 1024
lights_on = False
next_motion_alert_allowed = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

if not testing:
  slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':tada:',
    attachments='[ { "color": "#00ff00", "fallback": "I\'m Online and monitoring", "title": "I\'m Online and monitoring", "text": "%s" } ]' % config.get('config', 'motd'))
else:
  logging.warning("running in test mode")

while True:
  result = select.select([s],[],[])
  msg = result[0][0].recv(bufferSize)
  logging.info("recv:%s" % msg)
  [etime, data] = msg.split(' ', 1)
  [channel, argument] = data.split('=')

  if not testing:
    if channel == "ballarathackerspace.org.au/status":
      slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
        attachments='[ { "color": "#ffaa00", "fallback": "Alarm status", "title": "Alarm Status", "text": "%s" } ]' % (argument))

    if channel == "ballarathackerspace.org.au/motion":
      warmCache = urllib2.urlopen("https://ballarathackerspace.org.au/webcam%s.jpg" % etime).read()
      if time.time() > next_motion_alert_allowed:
        logging.info("sending motion alert to slack")
        slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
          attachments='[ { "color": "#ff0000", "fallback": "Motion detected", "title": "Motion Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "PIR sensor has been tripped %s time(s)." } ]' % (etime, argument))
      next_motion_alert_allowed = time.time() + squelch

    if channel == "ballarathackerspace.org.au/light":
      argument = int(argument)
      warmCache = urllib2.urlopen("https://ballarathackerspace.org.au/webcam%s.jpg" % etime).read()
      if argument > 1500:
        if not lights_on:
          lights_on = True
          logging.info("sending lights detected alert to slack")
          slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
            attachments='[ { "color": "#00ff00", "fallback": "Lights detected", "title": "Lights Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "LDR sensor has detected bright light (%s)." } ]' % (etime, argument))
      if argument < 1000:
        if lights_on:
          lights_on = False
