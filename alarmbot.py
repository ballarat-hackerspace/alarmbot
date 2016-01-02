#!/usr/bin/env python

import select, socket, urllib2, ConfigParser, logging, time
from slacker import Slacker
from slacker_log_handler import SlackerLogHandler
from threading import Timer

def checkAlive():
  if last_watchdog != 0:
    if (time.time() - last_watchdog) > 600:
      logger.panic("no watchdog msg seen for %2.2f minutes!" % ((time.time() - last_watchdog)/60))
  th = Timer(150.0, checkAlive)
  th.daemon = True
  th.start()

config = ConfigParser.RawConfigParser()
config.read('alarmbot.ini')

to_channel = config.get('config', 'to_channel')
log_channel = config.get('config', 'log_channel')
my_name = config.get('config', 'my_name')
port = config.getint('config', 'port')
squelch = config.getint('config', 'squelch')
testing = config.getboolean('config', 'testing')
slack = Slacker(config.get('config', 'slack_api'))

bufferSize = 1024
lights_on = False
next_motion_alert_allowed = 0
last_watchdog = 0
cur_timer = None

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

slack_handler = SlackerLogHandler(config.get('config', 'slack_api'), log_channel, username="alarmbot")
logger.addHandler(slack_handler)

th = Timer(150.0, checkAlive)
th.daemon = True
th.start()

if not testing:
  try:
    slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':tada:',
      attachments='[ { "color": "#00ff00", "fallback": "I\'m Online and monitoring", "title": "I\'m Online and monitoring", "text": "%s" } ]' % config.get('config', 'motd'))
  except Exception as e:
    logger.warn("slack.chat.post_message() failed: %s" % e)
else:
  logger.warning("running in test mode")

while True:
  result = select.select([s],[],[])
  msg = result[0][0].recv(bufferSize)
  logger.debug("recv:%s" % msg)
  try:
    [etime, data] = msg.split(' ', 1)
    [channel, argument] = data.split('=')
  except:
    logger.warn("unknown message format")
    channel = None

  if not testing:
    if channel == "ballarathackerspace.org.au/status":
      try:
        slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
          attachments='[ { "color": "#ffaa00", "fallback": "Alarm status", "title": "Alarm Status", "text": "%s" } ]' % (argument))
      except Exception as e:
        logger.warn("slack.chat.post_message() failed: %s" % e)

    elif channel == "ballarathackerspace.org.au/motion":
      try:
        warmCache = urllib2.urlopen("https://ballarathackerspace.org.au/webcam%s.jpg" % etime).read()
      except:
        logger.warn("warmcache failed")
      if time.time() > next_motion_alert_allowed:
        logger.info("sending motion alert to slack")
        try:
          slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
            attachments='[ { "color": "#ff0000", "fallback": "Motion detected", "title": "Motion Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "PIR sensor has been tripped %s time(s)." } ]' % (etime, argument))
        except Exception as e:
          logger.warn("slack.chat.post_message() failed: %s" % e)
      else:
          logger.info("squelched a motion alert")
      next_motion_alert_allowed = time.time() + squelch

    elif channel == "ballarathackerspace.org.au/light":
      argument = int(argument)
      try:
        warmCache = urllib2.urlopen("https://ballarathackerspace.org.au/webcam%s.jpg" % etime).read()
      except:
        logger.warn("warmcache failed")
      if argument > 1500:
        if not lights_on:
          lights_on = True
          logger.info("sending lights detected alert to slack")
          try:
            slack.chat.post_message(to_channel, '', username=my_name, icon_emoji=':rotating_light:',
              attachments='[ { "color": "#00ff00", "fallback": "Lights detected", "title": "Lights Detected", "title_link": "http://axis205.ballarathackerspace.org.au", "image_url": "https://ballarathackerspace.org.au/webcam%s.jpg", "text": "LDR sensor has detected bright light (%s)." } ]' % (etime, argument))
          except Exception as e:
            logger.warn("slack.chat.post_message() failed: %s" % e)
      if argument < 1000:
        if lights_on:
          lights_on = False

    elif channel == "ballarathackerspace.org.au/watchdog":
      last_watchdog = time.time()

    elif channel == "ballarathackerspace.org.au/wifi":
      pass

    else:
      logger.warn("unknown channel: %s (%s)" % (channel, argument))
