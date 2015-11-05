# Alarmbot

This is a simple service to monitor UDP for broadcast messages coming from various sensors
and then use them to send alerts to slack. It still has some hardcoded bits for our hackerspace
but it shouldn't be hard to modify it.

We send data to this service from Particle boards using arduino code like the following:

```
unsigned int port = 6655;
const size_t packetSize = 256;
char packet[packetSize];
UDP udp;
IPAddress bcast(192, 168, 0, 255);

...
udp.begin();
...

...
sprintf(packet, "%d %s=%s", Time.now(), key, value);
udp.beginPacket(bcast, port);
udp.write(packet);
udp.endPacket();
...

```

Eventually we'll have some example code to do the same on an ESP8266 board.

## Example `alarmbot.ini`

```
[config]
to_channel=#security
my_name=Alarm Bot NG
motd=I will monitor local sensors and send alerts to this channel
slack_api=<slack web api key>
testing=no
squelch=120
port=6655
```

Most settings don't require explanation however `squelch` probably does, this is the amount of
time the sensors need to be quiet before another message is sent to slack. This is to reduce
the amount of alerts in the slack channel (especially if a sensor gets stuck in a loop).

## Systemd service file

```
[Unit]
Description=alarmbot

[Service]
WorkingDirectory=/path/to/alarmbot
ExecStart=/path/to/alarmbot/alarmbot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

