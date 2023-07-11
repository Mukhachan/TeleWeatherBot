from pyowm import OWM
from pyowm.utils.config import get_default_config

import asyncio
from aiogram import Bot, Dispatcher, types, executor
from datetime import datetime

from config import OWM_KEY, TG_KEY, ARTEMS_CHAT, TIMES

owm = OWM(api_key=OWM_KEY)
mgr = owm.weather_manager()


observation = mgr.weather_at_place('Москва,RU')
w = observation.weather
config_dict = get_default_config()
config_dict['language'] = 'ru'

bot = Bot(token=TG_KEY)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print(message.chat.id)
    mess = 'Привет!\nЯ бот Артёма который оправляет ему погоду.\nЕсли ты не Артём, то Я тебе не рад)'
    await bot.send_message(chat_id=message.chat.id, text=mess)

async def shedule_handler():
    while True:
        now = datetime.now().strftime("%H:%M")
        print(f'\r{now}', end='')
        await asyncio.sleep(60)
        
        if now in TIMES:                
            text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в Москве: {int(w.temperature('celsius')['temp'])}°\nОщущается как {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}"
            print('\nОТПРАВЛЕНО СООБЩЕНИЕ:')
            print(text, '\n')

            try:
                sent_message = await bot.send_message(chat_id=ARTEMS_CHAT, text=text)
                await bot.delete_message(chat_id=ARTEMS_CHAT, message_id=sent_message.message_id - 1)

                with open('log.txt', 'w') as f:
                    f.write(now + ' - sent')    

            except Exception as e:
                print('При отправке возникла ошибка:', e)

if __name__ == '__main__':
    print('Бот запущен\n')

    loop = asyncio.get_event_loop()
    loop.create_task(shedule_handler())
    loop.create_task(executor.start_polling(dp, skip_updates=True))