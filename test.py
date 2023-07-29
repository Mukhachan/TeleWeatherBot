from datetime import datetime
from pyowm import OWM
from pyowm.utils.config import get_default_config

from config import OWM_KEY

city = '   Москва  '.strip().capitalize()

config_dict = get_default_config()
config_dict['language'] = 'ru'

owm = OWM(api_key=OWM_KEY)
mgr = owm.weather_manager()
observation = mgr.weather_at_place(city)
w = observation.weather

# text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\n", \
#         f"Сейчас температура в городе Москва: {int(w.temperature('celsius')['temp'])}°\n", \
#         f"Ощущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}\n", \
#         f"Облачность: {w.clouds}%"

text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в городе Москва: {int(w.temperature('celsius')['temp'])}°\nОщущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}\nОблачность: {w.clouds}%"



print('\nОТПРАВЛЕНО СООБЩЕНИЕ:')
print(text, '\n')
