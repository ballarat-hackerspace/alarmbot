import json
import traceback
import logging

from slacker import Slacker

ERROR_COLOR = 'danger'  # color name is built in to Slack API
WARNING_COLOR = 'warning'  # color name is built in to Slack API
INFO_COLOR = '#439FE0'

COLORS = {
    logging.CRITICAL: ERROR_COLOR,
    logging.ERROR: ERROR_COLOR,
    logging.WARNING: WARNING_COLOR
}

EMOJIS = {
    logging.NOTSET: ':loudspeaker:',
    logging.DEBUG: ':speaker:',
    logging.INFO: ':information_source:',
    logging.WARNING: ':warning:',
    logging.ERROR: ':exclamation:',
    logging.CRITICAL: ':boom:'
}


class SlackerLogHandler(logging.Handler):
    def __init__(self, api_key, channel, stack_trace=False, username='Python logger', icon_url=None):
        logging.Handler.__init__(self)
        self.slack_chat = Slacker(api_key)
        self.channel = channel
        self.stack_trace = stack_trace
        self.username = username
        self.icon_url = icon_url
        self.emojis = EMOJIS

        if not self.channel.startswith('#'):
            self.channel = '#' + self.channel

    def emit(self, record):
        message = str(record.getMessage())
        trace = {
            'fallback': message,
            'color': COLORS.get(self.level, INFO_COLOR)
        }
        if record.exc_info:
            trace['text'] = '\n'.join(traceback.format_exception(*record.exc_info))
        attachments = [trace]
        self.slack_chat.chat.post_message(
            text=message,
            channel=self.channel,
            username=self.username,
            icon_url=self.icon_url,
            icon_emoji=self.emojis[record.levelno],
            attachments=json.dumps(attachments)
        )
