from pyowm import OWM
from pyowm.utils.config import get_default_config

import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from geopy.geocoders import Nominatim

from datetime import datetime

from config import OWM_KEY, TG_KEY, db_connect_old

config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = OWM(api_key=OWM_KEY)
mgr = owm.weather_manager() # Получаем свежую погоду

bot = Bot(token=TG_KEY) # Подключаемся к боту
dp = Dispatcher(bot)

current_time = '12:00'
last_message = ''

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    mess = 'Привет!\nЯ бот Артёма который оправляет погоду'
    username = message.from_user.username
    chat_id = message.chat.id
    print(chat_id)

    conn = db_connect_old()
    await bot.send_message(chat_id=chat_id, text=mess)
    
    if conn.check_user(chat_id):
        mess = 'Ты уже имеешь здесь аккаунт!\nЧто бы посмотреть свои настройки просто введи команду /settings'
        await bot.send_message(chat_id=chat_id, text=mess)
    else:
        mess = 'Как я вижу, раньше ты не пользовался мной.\nДавай начнём с того где ты живёшь.\nОтправь свой город'
        conn.add_user(username=username, chat_id=chat_id)
        del conn
        await add_city(message, chat_id, mess)

@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    chat_id = message.chat.id
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.row(KeyboardButton("Город 🏙️", request_location=True), KeyboardButton("Расписание 📅"))
    await bot.send_message(text='Вот настройки:', chat_id=chat_id, reply_markup=reply_markup)

@dp.message_handler(content_types=ContentType.LOCATION)
async def handle_location(message: types.Message):
    global last_message
    conn = db_connect_old()
    chat_id = message.chat.id

    # Получаем широту и долготу
    latitude = message.location.latitude
    longitude = message.location.longitude
    # Получаем город
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    city = location.raw['address']['city']
    # Добавляем город в таблицу с chat_id 
    conn.add_city_by_chatId(city, message.chat.id)

    # Отправляем поздравительное сообщение
    reply_markup = types.ReplyKeyboardRemove()
    await message.reply(f"Город успешно изменён на: "+ city, reply_markup=reply_markup)
    
    time_search = conn.search_user_in_times(chat_id=chat_id)
    # Проверяем количество времён в БД. 
    print(time_search, type(time_search))
    if time_search.count(':') == 0:
        # В базе данных все записи со временем пустые
        mess = 'Давай заполним в какое время отправлять тебе погоду?\nНа данный момент я могу отправлять погоду два раза в сутки с шагом в 30 минут'
        await add_time(message, chat_id, mess)
        
    elif time_search.count(':') == 1:
        # В базе данных только 1 запись со временем
        mess = 'Кстати.\n На данный момент отправляю тебе погоду, только раз в сутки.\nНе хочешь ли добавить ещё одно время?'
        markup_request = ReplyKeyboardMarkup(resize_keyboard=True)
        markup_request.row(KeyboardButton('Нет, спасибо'), KeyboardButton('Давай добавим время!'))
        await bot.send_message(chat_id=chat_id, text=mess, reply_markup=markup_request)
    elif time_search.count(':') >= 2:
        print(f'Расписание для {chat_id} уже забито')

    del conn

@dp.message_handler()
async def process_message(message: types.Message):
    global current_time
    global last_message
    last_message = message.text
    chat_id = message.chat.id
    prev_time = current_time

    conn = db_connect_old() # Соединяем с БД #

    if message.text == "⬅️":
        # await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        current_time = change_time(current_time, '-')
    elif message.text == "➡️":
        # await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        current_time = change_time(current_time, '+')

    elif len(message.text) == 5 and ':' in message.text and '0' in message.text:
        if '🕛 ' in message.text: # Надо изменить уже существующее время #
            time = message.text.replace('🕛', '').strip()
            print('Ищем время и город:', time)
            

        result = conn.search_user_in_times(chat_id=chat_id)
        if result.count(':') >= 2: # Срабатывает если в БД уже есть 2 записи со временем
            er_mess = f"Ты не можешь получать погоду больше 2х раз\nНа данный момент ты получаешь погоду в {result[0]['time']} и в {result[1]['time']}"
            await message.reply(text=er_mess)

        else:
            # await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            add_time_res = await conn.add_time_by_chatId(chat_id, message.text)
            result = conn.search_user_in_times(chat_id=chat_id)
            if add_time_res:
                print('Смена времени')
                current_time = '12:00'
                print('Длина', result, len(result))
                if 'None' not in str(result):
                    print('Убираем клавиатуру')
                    reply_markup = types.ReplyKeyboardRemove()
                else:
                    print('Выводим клавиатуру')
                    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
                    reply_markup.row(KeyboardButton("⬅️"), KeyboardButton(current_time), KeyboardButton("➡️"))
                
                await bot.send_message(chat_id, 'Время успешно добавлено!', reply_markup=reply_markup)  
                return
            else:
                await bot.send_message(chat_id, 'Произошла, какая-то беда\nНапиши Артёму (@Mukhachan_dev)')

    elif message.text == 'Отмена':
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id)
        current_time = '12:00'
        return
    elif message.text == 'Давай добавим время!':
        message.reply('Хорошо')
        await add_time(message, chat_id)
        return

    elif message.text == 'Расписание 📅': 
        mess = 'Вот твоё расписание\nНажми на время которое хочешь поменять'
        add_time(message=message, chat_id=chat_id, mess=mess, pref=True)

    if prev_time != current_time:
        # Отправляем обновленную клавиатуру
        mess = last_message
        await add_time(message, chat_id, mess)

        # last_message = await bot.send_message(chat_id, mess, reply_markup=keyboard)
        # await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id-1)


# Отображает отправку времени #
async def add_time(message: types.Message, chat_id: int, mess: str = 'Выбери время:', pref: bool = False, change: bool = False):
    """
        Вызывается при нажатии на любую кнопку, которая подразумевает выбор ВРЕМЕНИ
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if pref:
        res = db_connect_old().search_user_in_times(message.chat.id)
        first_time = res[0]['time']
        second_button = res[1]['time']
        keyboard.row(KeyboardButton('🕛 '+ first_time), KeyboardButton(second_button + ' 🕛'))

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(KeyboardButton("⬅️"), KeyboardButton(current_time), KeyboardButton("➡️"))

    keyboard.row(KeyboardButton("Отмена"))

    last_message = await bot.send_message(chat_id, mess, reply_markup=keyboard)
    await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id-1)

# Отображает отправку города #
async def add_city(message: types.Message, chat_id: int, mess: str = 'Выбери город:'):
    """
        Вызывается при нажатии на любую кнопку, которая подразумевает выбор ГОРОДА
    """
    markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add( KeyboardButton('Отправить свою локацию 🗺️', request_location=True))
    await bot.send_message(chat_id=chat_id, text=mess, reply_markup=markup_request)

def change_time(time_str, side: str):
    hours, minutes = map(int, time_str.split(":"))
    total_minutes = hours * 60 + minutes    
    if side == '+':
        new_time = (total_minutes + 30) % (24 * 60)
    elif side == '-':
        new_time = (total_minutes - 30) % (24 * 60)
    return "{:02d}:{:02d}".format(new_time // 60, new_time % 60)


# async def shedule_handler():
#     while True:
#         now = datetime.now().strftime("%H:%M")
#         print(f'\r{now}', end='')
#         await asyncio.sleep(60)

#         if now in TIMES:                
#             try:
#                 observation = mgr.weather_at_place('Москва,RU')
#                 w = observation.weather

#                 text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в Москве: {int(w.temperature('celsius')['temp'])}°\nОщущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}"
#                 print('\nОТПРАВЛЕНО СООБЩЕНИЕ:')
#                 print(text, '\n')

#                 sent_message = await bot.send_message(chat_id=ARTEMS_CHAT, text=text)
#                 await bot.delete_message(chat_id=ARTEMS_CHAT, message_id=sent_message.message_id - 1)
#                 with open('log.txt', 'w') as f:
#                     f.write(now + ' - sent')    

#             except Exception as e:
#                 text = 'При отправке возникла ошибка: '+ e
#                 print(text)
#                 sent_message = await bot.send_message(chat_id=ARTEMS_CHAT, text=text)
#                 await bot.delete_message(chat_id=ARTEMS_CHAT, message_id=sent_message.message_id - 1)


def get_weather_cache():
    # Кэш для хранения данных о погоде для каждого города
    weather_cache = {}
    cities = []
    for i in db_connect_old().get_cities(): # Получаем список всех городов в БД
        cities.append(i['city'])
    cities = set(cities)

    for city in cities: # Получаем погоду по всем городам
        observation = mgr.weather_at_place(city)
        w = observation.weather
        weather_cache[city] = w
    
    return cities, weather_cache

async def shedule_handler():
    cache_response = get_weather_cache()
    cities = cache_response[0]
    weather_cache = cache_response[1]
    while True:
        now = datetime.now().strftime("%H:%M")
        print(f'\r{now}', end='')      
        await asyncio.sleep(120) # Ждём 2 минуты
        for city in cities: # Перебираем города
            people_list = db_connect_old().search_by_city_and_nowtime(city) # Получаем список пользователей которым нужно отправить погоду
            for person in people_list: # Перебираем список пользователей #
                if person['city'] not in weather_cache: # Если в кэше нет нужного города, то обновляем его и едем дальше
                    cache_response = get_weather_cache()
                    cities = cache_response[0]
                    weather_cache = cache_response[1]

                w = weather_cache[person['city']]
                chat_id = people_list['chat_id']

                text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в Москве: {int(w.temperature('celsius')['temp'])}°\nОщущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}"
                print('\nОТПРАВЛЕНО СООБЩЕНИЕ:')
                print(text, '\n')

                sent_message = await bot.send_message(chat_id=chat_id, text=text)
                await bot.delete_message(chat_id=chat_id, message_id=sent_message.message_id - 1)

if __name__ == '__main__':
    print('Бот запущен\n')

    loop = asyncio.get_event_loop()
    loop.create_task(shedule_handler())
    loop.create_task(executor.start_polling(dp, skip_updates=True))