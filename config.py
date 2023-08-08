OWM_KEY = "e8f63f748bfc269a3f4db8203af0c657"
TG_KEY = "5998963033:AAF_8rjDgMMLQcz95eI-B1WMVhYZvzdCq9o"
ARTEMS_CHAT = "596137700"
TIMES = ["12:00", "19:00"]

headers = {
    'X-Gismeteo-Token' : '64ad4247b7f419.73289992'
}
host = "45.9.41.88"
user = 'root'
password = 'dRi13iXz#k4pM{v2}b~~?2HYbnl8rJxz'
db_name = 'ArtemsWeatherBot'

import pymysql
from pymysql.cursors import DictCursor
from DataBase import DataBase

def db_connect_old() -> DataBase: # Подключение к БД #
    try:
        db = pymysql.connect(
            host = host,
            port = 3306,
            user = user,
            password = password,
            database = db_name,
            cursorclass = DictCursor,
        )
    except Exception as ex:
        print("[INFO] Ошибка при работе с MySQL: ", ex)
    
    return DataBase(db, db.cursor())
