import sqlite3, pytz, datetime, bs4, asyncio, aiohttp

from async_bot import logging
from aiogram import types
from aiogram.dispatcher import FSMContext

from marks import mark, menus, cancel, remove, sett, times
import config, messages, cstatic


connection = sqlite3.connect("botter.db", check_same_thread=False,
                             detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

text = None

zeroid = []
cidis = {}
for i in range(len(cstatic.cities)):
    zeroid.append((i) * 3)
    cidis.update({cstatic.cities[i]: i})


async def userlogging(message: types.Message):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users")  # sql
    users = cursor.fetchall()  # get all ids from db
    ids = []
    for user in users:
        ids.append(user[0])
    if message.chat.id not in ids:  # add user to db if it is new
        logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " New user {0}({1}) logged in".format(message.chat.username,
                                                                                               message.chat.id))
        data_tuple = (str(message.chat.id), message.chat.username, 0, 9, 30)
        cursor.execute("INSERT INTO 'users'('id', 'username', 'status', 'hour', 'minute') VALUES(?, ?, ?, ?, ?);",
                       data_tuple)
        connection.commit()


async def stater(message: types.Message):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    cursor = connection.cursor()
    cursor.execute("SELECT city FROM users WHERE id = {}".format(message.chat.id))
    city = cursor.fetchall()[0][0]
    logging.info(
        now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) required statics for {2}".format(message.chat.username,
                                                                                             message.chat.id, city))
    b = bs4.BeautifulSoup(text.decode('utf-8'), 'html.parser')
    i = cidis[city]
    rus = b.select(cstatic.RUSER)[cstatic.RUSID].text
    ill = b.select(cstatic.FINDER)[zeroid[i]].text
    nills = b.select(cstatic.FINDER)[zeroid[i] + 1].text
    died = b.select(cstatic.FINDER)[zeroid[i] + 2].text
    ret = round(int(died) / int(ill) * 100, 2)
    await message.answer(messages.STATICS.format(cstatic.cities[i], ill, died, nills, ret, rus), parse_mode='html')


async def cityset(message: types.Message):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET city = '{0}' WHERE id = '{1}';".format(message.text, message.chat.id))
    connection.commit()
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) changed to '{2}'".format(message.chat.username,
                                                                                              message.chat.id,
                                                                                              message.text))


async def timeset(message: types.Message, state: FSMContext):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    try:
        hour = None
        minute = None
        if not message.text == "Назад":
            timea = message.text.split(':')
            hour = int(timea[0])
            minute = int(timea[1])
            if hour > 23 or hour < 0 or minute > 59 or minute < 0:
                raise ValueError
    except ValueError:
        await message.answer("Неправильный формат")
        logging.warning(
            now.strftime("%Y-%m-%d %H:%M:%S") + " {0}({1}) send invalid date format".format(message.chat.username,
                                                                                            message.chat.id))
        hour = None
    if hour is not None:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET hour = '{0}' WHERE id = '{1}';".format(hour, message.chat.id))
        cursor.execute("UPDATE users SET minute = '{0}' WHERE id = '{1}';".format(minute, message.chat.id))
        connection.commit()
        await state.finish()
        if minute == 0:
            minute = "00"
        logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) changed everyday msg time to {2}:{3}".format(
            message.chat.username, message.chat.id, hour, minute))
    return hour, minute


async def systemsg(message, bot):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    cursor = connection.cursor()
    logging.warning(now.strftime("%Y-%m-%d %H:%M:%S") + " -- -System messages starting -- -")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " Sent System msg for user {0}({1})".format(user[0], user[2]))
        await bot.send_message(user[0], messages.SYSTEM_MSG, parse_mode='html')
    logging.warning(now.strftime("%Y-%m-%d %H:%M:%S") + "! -- -System messages stoped -- -!")
    await message.answer("Ok")
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + "Admin {0}({1}) sent System message".format(message.chat.username,
                                                                                                 message.chat.id))


async def generator():
    """Get data from cite every 30 seconds"""
    while True:
        global text
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(cstatic.URL) as resp:
                text = await resp.read()
        await asyncio.sleep(30)


async def everyday(bot):
    """Sending everyday messages"""
    while True:
        now = datetime.datetime.now()
        timezone = pytz.timezone("Europe/Moscow")
        now = timezone.localize(now)
        cursor = connection.cursor()
        await asyncio.sleep(5)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user in users:
            if user[1] == None:
                continue
            else:
                if user[4] == now.hour and user[5] == now.minute and user[3] == 0:
                    logging.info(
                        now.strftime("%Y-%m-%d %H:%M:%S") + " Sent statics about {1} for user {0}({2})".format(user[0],
                                                                                                               user[1],
                                                                                                               user[2]))
                    b = bs4.BeautifulSoup(text.decode('utf-8'), 'html.parser')
                    i = cidis[user[1]]
                    rus = b.select(cstatic.RUSER)[cstatic.RUSID].text
                    ill = b.select(cstatic.FINDER)[zeroid[i]].text
                    nills = b.select(cstatic.FINDER)[zeroid[i] + 1].text
                    died = b.select(cstatic.FINDER)[zeroid[i] + 2].text
                    ret = round(int(died) / int(ill) * 100, 2)
                    await bot.send_message(user[0],
                                           messages.STATICS.format(cstatic.cities[i], ill, died, nills, ret, rus),
                                           parse_mode='html')
                    cursor.execute("UPDATE users SET status = '{0}' WHERE id = {1};".format(1, user[0]))
                if (user[4] != now.hour or user[5] > now.minute) and user[3] == 1:
                    cursor.execute("UPDATE users SET status = '{0}' WHERE id = {1};".format(0, user[0]))
