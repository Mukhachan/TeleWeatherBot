import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.utils.exceptions import BotBlocked

import requests

from datetime import datetime

from config import TG_KEY, headers, db_connect_old

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
        mess = 'Твой аккаунт разморожен!)\nЧто бы посмотреть свои настройки просто введи команду /settings'
        await bot.send_message(chat_id=chat_id, text=mess)
        await bot.send_message(chat_id=chat_id, text='Добро пожаловать!')
        conn.change_sending(chat_id, 'True')
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
    latitude = str(message.location.latitude)[:6]
    longitude = str(message.location.longitude)[:6]
    print(latitude, longitude)
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'limit': 1
    }
    try: 
        r = requests.get('https://api.gismeteo.net/v2/search/cities/', params=params, headers=headers)
        print(r.url)
        response = r.json()['response'][0]
        city = response['id']
        city_name = response['district']['nameP']
    except Exception:
        print('Отправь геолокацию на самый близжайший от тебя город')
        await message.reply('Отправь геолокацию на самый близжайший от тебя город')

    # Добавляем город в таблицу с chat_id 
    conn.add_city_by_chatId(city, message.chat.id)

    # Отправляем поздравительное сообщение
    reply_markup = types.ReplyKeyboardRemove()
    await message.reply(f"Теперь ваш город: "+ response['district']['name'], reply_markup=reply_markup)
    
    time_search = conn.search_user_in_times(chat_id=chat_id)
    # Проверяем количество времён в БД. 
    print(time_search, type(time_search))
    if str(time_search).count('datetime.timedelta') == 0:
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

    del conn, r

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

     
     # Входной текст от 5 до 7 симвов #  В тексте содержится :  #  Последний символ '0'
    elif 5 <= len(message.text) <= 7 and ':' in message.text or '🕛 None' in message.text:
        print('Получил время')
        if message.text[-2] not in ('0', '3', 'n') and '🕛' not in message.text:
            await bot.send_message(chat_id=chat_id, text='Ты можешь указать время только с шагом в 30 минут\nК примеру: 12:00, 12:30, 13:00 и т.д.')
            return
        
        print('[INFO] Обрабатываем время')
        if '🕛' in message.text: # Надо изм\\енить уже существующее время #
            print('Зашли в условие')
            time = message.text.replace('🕛', '').strip()
            print('[INFO] Ищем время и город:', time)
            await conn.search_by_ChatId_and_time(chat_id=chat_id, time=time)
            await add_time(message, chat_id, 'Прошу выбрать новое время:')
            return

        result = conn.search_user_in_times(chat_id=chat_id)
        if result.count(':') >= 2: # Срабатывает если в БД уже есть 2 записи со временем
            er_mess = f"Ты не можешь получать погоду больше 2х раз\nНа данный момент ты получаешь погоду в {result[0]['time']} и в {result[1]['time']}"
            await message.reply(text=er_mess)

        else:
            db_connect_old().change_log(f"Изменено время для пользователя {chat_id}")
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
    elif message.text == 'chat_id':
        await message.reply(f"ID этого чата: {chat_id}")
    elif message.text == 'Отмена':
        # await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await message.reply('Хорошо. Клавиатуру я вряд ли спрячу, но допекать не буду')
        # await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id)
        current_time = '12:00'
        return
    elif message.text == 'Давай добавим время!':
        message.reply('Хорошо')
        await add_time(message, chat_id)
        return
    elif message.text == 'Расписание 📅': 
        print('[INFO] Принтуем расписание')
        mess = 'Вот твоё расписание\nНажми на время которое хочешь поменять'
        await add_time(message=message, chat_id=chat_id, mess=mess, pref=True)
    elif 'спасибо' in message.text.lower():
        await bot.send_message(chat_id=chat_id, text='Обращайся!)')

    if prev_time != current_time:
        # Отправляем обновленную клавиатуру
        mess = last_message
        await add_time(message, chat_id, mess)


# Отображает отправку времени #
async def add_time(message: types.Message, chat_id: int, mess: str = 'Выбери время:', pref: str = False, change: bool = False):
    """
        Вызывается при нажатии на любую кнопку, которая подразумевает выбор ВРЕМЕНИ
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if pref:
        res = db_connect_old().search_user_in_times(message.chat.id)
        first_time = str(res[0]['time'])[:-3] if res[0]['time'] != None else 'None'
        second_time = str(res[1]['time'])[:-3] if res[1]['time'] != None else 'None'
        print(f'[INFO] Выводим пользователю его время {first_time} и {second_time}')
        keyboard.row(KeyboardButton(f'🕛 {first_time}'), KeyboardButton(f'{second_time} 🕛'))

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row(KeyboardButton("⬅️"), KeyboardButton(current_time), KeyboardButton("➡️"))

    keyboard.row(KeyboardButton("Отмена"))

    last_message = await bot.send_message(chat_id, mess, reply_markup=keyboard)
    # await bot.delete_message(chat_id=chat_id, message_id=last_message.message_id-1)

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

def get_weather_cache():
    print('Обращаемся к GISMETEO за новыми данными')
    db_connect_old().change_log('Обращаемся к GISMETEO за новыми данными')
    weather_cache = {}
    cities = []

    for i in db_connect_old().get_cities(): # Получаем список всех городов в БД
        cities.append(i['city'])
    cities = set(cities)
    print (cities)
    for city in cities: # Получаем погоду по всем городам
        try:
            r = requests.get(f'https://api.gismeteo.net/v2/weather/current/{city}/', headers=headers)
            weather_cache[city] = r.json()['response']

        except Exception as e:
            print(f'С погодой для города {city} возникла ошибка: {e}')
            db_connect_old().change_log(f'Ошибка погоды для города {city}')
            weather_cache[city] = 'Город не найден'
    
    del r
    return cities, weather_cache

async def shedule_handler():
    cache_response = get_weather_cache()
    cities = cache_response[0]
    weather_cache = cache_response[1]
    weather_cache['last_update'] = datetime.now()
    
    while True:
        now = datetime.now().strftime("%H:%M")
        print(f'\r{now}', end='')      
        await asyncio.sleep(60) # Ждём минуту

        for city in cities: # Перебираем города
            people_list = db_connect_old().search_by_city_and_nowtime(city) # Получаем список пользователей которым нужно отправить погоду
            for person in people_list: # Перебираем список пользователей #
                print(person)
                if person['city'] not in weather_cache or (datetime.now() - weather_cache['last_update']).total_seconds()/60 > 6*60: # Если в кэше нет нужного города, то обновляем его и едем дальше
                    cache_response = get_weather_cache()
                    cities = cache_response[0]
                    weather_cache = cache_response[1]
                    weather_cache['last_update'] = datetime.now()

                w = weather_cache[person['city']]
                chat_id = person['chat_id']
                if w == 'Город не найден':
                    text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nЯ не могу отправить тебе погоду так как ты не указал близжайший от себя город\nОтправь мне геопозицую и в следующий раз я всё отправлю)"
                else:
                    humidity = w['humidity']['percent']
                    description = w['description']['full']
                    temperature = w['temperature']['air']['C']
                    cloudiness = w['cloudiness']['percent']
                    precipitation = w['precipitation']
                    
                    precipitation_emo = ['☀️ нет осадков', '🌧️ дождик', '🌨️снег', 'смешанные осадки']
                    intensity_emo = ['нет осадков', 'небольшой дождь или снег', 'дождь или снег', 'сильный дождь или снег']
                    x = cloudiness
                    smile = "🌤️" if x <= 20 else "⛅️" if x <= 50 else "🌥️" if x <= 75 else "☁️"

                    text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас 🌡️ температура в твоём городе: {temperature}°\n",\
                    f"💧Влажность: {humidity}%\n",\
                    f"Описание: {description}\n",\
                    f"Облачность: {cloudiness}% {smile}\n",\
                    f"Осадки:\n",\
                    f"    Тип: {precipitation['type']}/3 - {precipitation_emo[int(precipitation['type'])]}\n",\
                    f"    Количество: {precipitation['amount'] if not 'None' else '0'}мм\n",\
                    f"    Интенсивность: {precipitation['intensity']}/3 - {intensity_emo[int(precipitation['intensity'])]}\n"
                    text = "".join(text)
                    ### text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в городе {person['city']}: {int(w.temperature('celsius')['temp'])}°\nОщущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}\nОблачность: {w.clouds}%"

                print('ОТПРАВЛЕНО СООБЩЕНИЕ:')
                print(text, '\n')
                try:
                    sent_message = await bot.send_message(chat_id=chat_id, text=text)
                    # await bot.delete_message(chat_id=chat_id, message_id=sent_message.message_id - 1)
                except BotBlocked:
                    conn = db_connect_old()
                    print(f'Пользователь {chat_id} нас заблокировал')
                    conn.change_log(f'Пользователь {chat_id} нас заблокировал')
                    conn.change_sending(chat_id=chat_id, text='False')
                    del conn

if __name__ == '__main__':
    print('Бот запущен\n')

    loop = asyncio.get_event_loop()
    loop.create_task(shedule_handler())
    loop.create_task(executor.start_polling(dp, skip_updates=True))