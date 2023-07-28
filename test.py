from datetime import datetime
from pyowm import OWM
from pyowm.utils.config import get_default_config

from config import OWM_KEY

city = '   Екатеринбург  '.strip().capitalize()

config_dict = get_default_config()
config_dict['language'] = 'ru'

owm = OWM(api_key=OWM_KEY)
mgr = owm.weather_manager()
observation = mgr.weather_at_place(city)
w = observation.weather
text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в городе "+ city +f": {int(w.temperature('celsius')['temp'])}°\nОщущается как: {int(w.temperature('celsius')['feels_like'])}°\nПогода: {w.detailed_status}"
print(text)            