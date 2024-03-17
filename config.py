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
