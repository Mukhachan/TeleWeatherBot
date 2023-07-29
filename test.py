from time import sleep
import datetime

weather_cache = {}
weather_cache['last_update'] = datetime.datetime.now()
sleep(1)

print((datetime.datetime.now() - weather_cache['last_update']).total_seconds()/60)

if (datetime.datetime.now() - weather_cache['last_update']).total_seconds()/60 > 3*60:
    print('работает')