"""Working with bot"""

# import aiogram modules
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# import all required libraries
import logging, datetime, importlib, pytz

# import our modules
import config, covid, config, marks, messages, cstatic
from config import PROXY_URL
import marks
from marks import mark, menus, cancel, remove, sett, times

# Form for next steps
class Form(StatesGroup):
    timer = State()
    starttimer = State()


# logging setup
logging.basicConfig(level=logging.INFO, filename='abot.log')

# * Uncomment this if you want to use your proxy and comment another bot
bot = Bot(token = config.TOKEN, proxy=PROXY_URL)

# bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    """Sending start message"""
    await covid.userlogging(message)
    await Form.starttimer.set()
    await message.answer("Привет, <b>{}</b> \n".format(message.chat.first_name) + messages.startmsg, parse_mode='html',
                         reply_markup=mark)


@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    """Sending statistics by command"""
    await covid.stater(message)


@dp.message_handler(commands=['menu'])
async def menur(message: types.Message):
    """Returning to menu by command"""
    await message.answer(messages.MENU, reply_markup=menus, parse_mode='html')


@dp.message_handler(commands=['changecity'])
async def changecity(message: types.Message):
    """Starting changing city by command"""
    await message.answer(messages.CIT, parse_mode='html', reply_markup=mark)


@dp.message_handler(commands=['changetime'])
async def timesetter(message: types.Message):
    """Starting changing sending time by command"""
    await Form.timer.set()
    await message.answer(messages.AFTER, parse_mode='html', reply_markup=times)


@dp.message_handler(commands=['info'])
async def infor(message: types.Message):
    """Sending info by command"""
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) required info".format(message.chat.username,
                                                                                           message.chat.id))
    await message.answer(messages.INFO, parse_mode='html', reply_markup=menus)


@dp.message_handler(commands=['reloadcfg'])
async def reloader(message: types.Message):
    """Reloading modules by admin command"""
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    if str(message.chat.id) in config.ADMINS:
        importlib.reload(config)
        importlib.reload(marks)
        importlib.reload(messages)
        importlib.reload(cstatic)
        await message.answer("Reloaded config")
        logging.warning(now.strftime("%Y-%m-%d %H:%M:%S") + " Admin {0}({1}) added reloaded config".format(message.chat.username, message.chat.id))
    else:
        logging.error(
            now.strftime("%Y-%m-%d %H:%M:%S") + " User with name {0} and id {1} tried to log in to admin ctr".format(message.chat.id, message.chat.username))


@dp.message_handler(commands=['sendmsgs'])
async def sender(message: types.Message):
    """Sending system messages"""
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    if str(message.chat.id) in config.ADMINS:
        covid.systemsg(message, bot)
    else:
        logging.error(
            now.strftime("%Y-%m-%d %H:%M:%S") + " User with name {0} and id {1} tried to log in to admin ctr".format(message.chat.id, message.chat.username))


@dp.message_handler(lambda message: message.text == "📊Статистика")
async def st(message: types.Message):
    """Sending statics by menu button"""
    await covid.stater(message)


@dp.message_handler(lambda message: message.text == "🏙️Изменить город")
async def rtr(message: types.Message):
    """Starting changing city by menu button"""
    await message.answer(messages.CIT, parse_mode='html', reply_markup=mark)


@dp.message_handler(lambda message: message.text == "⏱️Изменить время отправки")
async def rt(message: types.Message):
    """Starting changing sending time by menu button"""
    await Form.timer.set()
    await message.answer(messages.AFTER, parse_mode='html', reply_markup=times)


@dp.message_handler(lambda message: message.text == "ℹ️info")
async def info(message: types.Message):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) required info".format(message.chat.username,
                                                                                           message.chat.id))
    await message.answer(messages.INFO, parse_mode='html', reply_markup=menus)


@dp.message_handler(lambda message: message.text == "⚙️Настройки")
async def settin(message: types.Message):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) required settings".format(message.chat.username,
                                                                                               message.chat.id))
    await message.answer(messages.SET, parse_mode='html', reply_markup=sett)


@dp.message_handler(lambda message: message.text == "Назад", state='*')
async def can(message: types.Message, state: FSMContext):
    now = pytz.timezone("Europe/Moscow").localize(datetime.datetime.now())
    logging.info(now.strftime("%Y-%m-%d %H:%M:%S") + " User {0}({1}) pressed cancel".format(message.chat.username,
                                                                                            message.chat.id))
    await state.finish()
    await message.answer(messages.MENU, parse_mode='html', reply_markup=menus)


@dp.message_handler(lambda message: message.text in cstatic.cities, state=Form.starttimer)
async def setcitys(message: types.Message):
    """Setting sending city after /start"""
    await covid.cityset(message)
    await Form.timer.set()
    await message.answer(messages.AFTER, parse_mode='html', reply_markup=times)


@dp.message_handler(lambda message: message.text in cstatic.cities)
async def setcitys2(message: types.Message):
    """Setting city"""
    await covid.cityset(message)
    await message.answer(messages.CHANGED_CITY.format(message.text), parse_mode='html', reply_markup=cancel)
    await covid.stater(message)


@dp.message_handler(state=Form.timer)
async def settime(message: types.Message, state: FSMContext):
    """Setting sending time"""
    hour, minute = await covid.timeset(message, state)
    if hour is not None:
        await message.answer(messages.AFTER2.format(hour, minute), reply_markup=menus, parse_mode='html')


def main():
    dp.loop.create_task(covid.generator())
    dp.loop.create_task(covid.everyday(bot))
    executor.start_polling(dispatcher=dp)


if __name__ == '__main__':
    main()
