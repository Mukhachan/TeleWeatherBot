from DataBase import DataBase
from config import db_connect_old

x = input('Какую функцию вызвать? ')
if x == '1':
    print(db_connect_old().check_user('596137700'))
elif x == '2':
    res = db_connect_old().search_user_in_times('596137700')
    print(res, len(res))