## Example `alarmbot.ini`

```
[config]
to_channel=#security
my_name=Alarm Bot NG
motd=I might still be buggy so please annoy @srw if I go a little crazy. There is a known issue whereby the PIR sensor is sending false positives after being enabled, this appears to be a hardware fault and @srw is looking into that.
slack_api=<slack web api key>
```

## Systemd service file

```
[Unit]
Description=alarmbot

[Service]
WorkingDirectory=/path/to/alarm
ExecStart=/path/to/alarm/alarmbot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
