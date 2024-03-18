# YandexGPT Bot

You can use this code to create a base for your telegram bot for ChatGPT or other AI model that answers with MarkDown formatting.
This bot is working inside [Yandex Cloud](https://cloud.yandex.ru/en/) infrastructure and using YandexGPT API, but you can replace yandex-dependent code to yours. 

## What this bot can do
* Ofc, make requests to yandex models
* Change and save model parameters for every chat
* Formatting output from model to telegram supported HTML format (working in 99%)
* **Small feature:** bot showing "typing..." while doing long requests

## Yandex dependent code that you should replace
Yandex dependent code i call code that uses Yandex Cloud inner API to work properly.
Yandex dependent code placed in:
1. main() in [GPTBot.py](https://github.com/SlamperBOOM/Telegram-Bots/blob/master/YandexGPTBot/GPTBot.py#L27) when retrieveng bot token
2. _send_msg_to_model() in [YandexGPTAPI.py](https://github.com/SlamperBOOM/Telegram-Bots/blob/master/YandexGPTBot/YandexGPTAPI.py#L38) when making request to model API
3. retrieve_iam_token() on [YandexTokenUtil.py](https://github.com/SlamperBOOM/YandexGPT-Bot/blob/master/YandexGPTBot/YandexTokenUtil.py#L10) when retrieve IAM-token that used in all other requests inside Yandex Cloud
4. Params for model in [ModelParamsManager.py](https://github.com/SlamperBOOM/YandexGPT-Bot/blob/master/YandexGPTBot/ModelParamsManager.py). All functions related to change parameters

If you want to use this repo in your own bot, cha
## Set up telegram bot on remote server
To run this bot at system startup on your server, do the following steps:
1. Copy files from [YandexGPTBot](YandexGPTBot) to some folder on your server (for example, /home/\*username\*/)
Your folder should look like this:

![image](https://github.com/SlamperBOOM/YandexGPT-Bot/assets/25345740/25b39aaf-ab76-400a-97eb-156ba1b4c63b)

3. Change paths in [bot.service](https://github.com/SlamperBOOM/Telegram-Bots/blob/master/YandexGPTBot/bot.service#L7) to `/absolute/path/to/home/folder/start_bot.sh` and [start_bot.sh](https://github.com/SlamperBOOM/Telegram-Bots/blob/master/YandexGPTBot/start_bot.sh#L2) to `/absolute/path/to/home/folder`
4. Copy bot.service file at `/etc/systemd/system/` folder. Then run this commands:
```shell
sudo systemctl daemon-reload
sudo systemctl enable bot.service
sudo systemctl start bot.service
```
4. Use bot :)
