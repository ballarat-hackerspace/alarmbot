#!/usr/bin/env python

import select, socket, urllib2, ConfigParser
from slacker import Slacker

config = ConfigParser.RawConfigParser()
config.read('alarmbot.ini')

to_channel = config.get('config', 'to_channel')
my_name = config.get('config', 'my_name')
port = 25276
bufferSize = 1024
slack = Slacker(config.get('config', 'slack_api'))

lights_on = False

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)

slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':tada:',
  attachments='[ { "color": "#00ff00", "fallback": "I\'m Online and monitoring", "title": "I\'m Online and monitoring", "text": "%s" } ]' % config.get('config', 'motd'))

while True:
  result = select.select([s],[],[])
  msg = result[0][0].recv(bufferSize) 
  print msg
  [time, data] = msg.split(' ', 1)
  [channel, argument] = data.split('=')

  if channel == "ballarathackerspace.org.au/status":
    slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
      attachments='[ { "color": "#ffaa00", "fallback": "Alarm status", "title": "Alarm Status", "text": "%s" } ]' % (argument))

  if channel == "ballarathackerspace.org.au/motion":
    slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
      attachments='[ { "color": "#ff0000", "fallback": "Motion detected", "title": "Motion Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "PIR sensor has been tripped %s time(s)." } ]' % (time, argument))
    warmCache = urllib2.urlopen("https://ballarathackerspace.org.au/webcam%s.jpg" % time).read()

  if channel == "ballarathackerspace.org.au/light":
    argument = int(argument)
    if argument > 1500:
      if not lights_on:
        lights_on = True
        slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
          attachments='[ { "color": "#00ff00", "fallback": "Lights detected", "title": "Lights Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "LDR sensor has detected bright light (%s)." } ]' % (time, argument))
    if argument < 1000:
      if lights_on:
        lights_on = False
