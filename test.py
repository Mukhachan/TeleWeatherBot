import requests

PARAMS = {
    "apikey":"92b10480-ab04-458b-88b0-2533a3e60440",
    "format":"json",
    "lang":"ru_RU",
    "kind":"house",
    "geocode": f"55.647914,37.958664"
}

#отправляем запрос по адресу геокодера.
try:
    r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
    #получаем данные
    json_data = r.json()
    #вытаскиваем из всего пришедшего json строку с городом.
    # ["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"][2]["name"]
    city = json_data
    print(city)
    
except:
    pass