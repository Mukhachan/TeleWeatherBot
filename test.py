from datetime import datetime
import requests
from pprint import pprint
headers = {
    'X-Gismeteo-Token' : '64ad4247b7f419.73289992'
}


def get_city():
    params = {
    # 'latitude': '55.748',
    # 'longitude':'37.815',
    'query': 'екатеринбург',
    'limit': 1
    }
    r = requests.get(f'https://api.gismeteo.net/v2/search/cities/', params=params, headers=headers)
    pprint(r.json()['response']['items'][0]['id'])

def get_weather():
    weather_cache = {}
    city = '4368'
    # r = requests.get(f'https://api.gismeteo.net/v2/weather/current/{city}/', headers=headers)
    # weather_cache[city] = r.json()['response']
    # pprint(weather_cache[city])

    # humidity = weather_cache[city]['humidity']['percent']
    # description = weather_cache[city]['description']['full']
    # temperature = weather_cache[city]['temperature']['air']['C']
    # cloudiness = weather_cache[city]['cloudiness']['percent']
    # precipitation = weather_cache[city]['precipitation']
    
    humidity = 1342
    description = 2314
    temperature = 1234
    cloudiness = 345
    precipitation = 5462
    text = f"{datetime.now().strftime('%H:%M %d/%m/%Y')}\nСейчас температура в твоём городе: {temperature}°\n",\
    f"Влажность: {humidity}%\n",\
    f"Описание: {description}\n",\
    f"Облачность: {cloudiness}%\n",\
    f"Осадки:\n",\
    f"    Тип: {precipitation}/3\n",\
    f"    Количество: {precipitation}мм\n",\
    f"    Интенсивность: {precipitation}/3\n"
    text = "".join(text)
    print(text)
    # response = r.json()['response'][0]
    # city_name = response['district']['nameP']
    # city_id = response['id']

get_weather()
# get_weather()