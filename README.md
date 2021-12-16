# nmonit.py

#### Simple Nano Node Monitoring Tool with optional slack and discord webhook notifications
---
### Requirements:
* python3 
* requests `pip3 install requests`
---

### Usage:
```bash
nmonit.py [-h] [--connection_string CONNECTION_STRING] [--slack_webhook SLACK] [--discord_webhook DISCORD] --nickname NICKNAME
```
#### optional arguments:
|Flag|Description|Default
|-|-|-|
|-h, --help| show this help message and exit
|--connection_string| RPC connection to node| localhost:7075
|--slack_webhook| Slack Websocket url to send to|unset
|--discord_webhook|Discord Webhook to send to|unset
|--nickname|endpoint nickname|

### [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks):
1) Server Settings
2) Integrations
3) Create Webhook
### [Slack Webhook](https://api.slack.com/messaging/webhooks):
1) Create Slack App
2) Enable Incoming Webhooks
3) Create Webhook

### Creating cronjob:
1) `crontab -e`
2) add the following to the crontab `*/5 * * * * /path/to/python3 /path/to/nmonit.py --connection_string=\<endpoint:port\> --slack_webhook=\<slack webhook url\> --discord_webhook=\<discord webhook url\> --nickname=\<connection nickname>` adjusting [*/5 * * * *](https://crontab.guru/#*/5_*_*_*_*) as required
