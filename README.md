# Covid Rus Bot
## Installation
:warning: *You need python 3.7 or higher*
### Mac os/Linux
```
python3 -m venv venv
source venv/bin/activate
pip3 install aiogram bs4 aiohttp-proxy

```
### Windows
```
python -m venv venv
source venv/bin/activate
pip install aiogram bs4 aiohttp-proxy
```
## Starting
Please, paste your bot token and your telegram id(you can find it with @userinfobot) in config.py.
### Linux
#### Simple
```
python3 async_bot.py
```
#### Using as service
Copy file from [gist](https://gist.github.com/xsestech/d48b67ad69faa4d730f242080ac7e950) to /lib/systemd/system/covbot.service. Replace <user> with your linux username and <bot loctation> with your bot path.

Now you can start your bot with `sudo service covbot start`
### Windows
```
python async_bot.py
```
