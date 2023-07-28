import datetime
import pymysql

class DataBase:
    """
        Класс созданный для взаимодействия с базой данных и так далее.
    """
    def __init__(self, connection = None, cursor = None): # Инициализация глобальных переменных # 
        self.__connection = connection
        self.__cur = cursor
 
    def check_user(self, chat_id: int) -> bool:
        """
            Проверяет есть ли в базе данных такой пользователь
        """
        sql = (
            f'SELECT * FROM `ArtemsWeatherBot`.`users` where chat_id = {chat_id}'
        )
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            return True if res else False
        except Exception as e:
            print('[WARNING] При поиске пользователя возникла ошибка:', e)
            return False

    def add_user(self, username: str, chat_id: int) -> bool:
        """
            Служит для добавления новых пользователей в базу данных
        """
        reg_date = datetime.datetime.now()
        try:
            sql = (
                f'INSERT INTO `ArtemsWeatherBot`.`users` VALUES (NULL, "{username}", {chat_id}, NULL, "{reg_date}")'
            )
            self.__cur.execute(sql)
            self.__connection.commit()
            
        except Exception as e:
            print('[WARNING] При сохранинии пользователя возникла ошибка', e)
            return False
        
        # Сохраняем время
        try:
            for i in range(2):
                sql = (
                    f'INSERT INTO `ArtemsWeatherBot`.`times` VALUES(NULL, {chat_id}, NULL, NULL)'
                )
                self.__cur.execute(sql)
                self.__connection.commit()
        except Exception as e:
            print('[WARNING] При сохранении времени возникла ошибка', e)
            return False

    def add_city_by_chatId(self, city: str, chat_id: int) -> bool:
        """
            Функция добавляет или меняет город в ячейке city для конкретного пользователя
        """
        
        # Меняем город в таблице users
        sql = f'UPDATE `ArtemsWeatherBot`.`users` SET city = "{city}" WHERE chat_id={chat_id}'
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
        except Exception as e:
            print('[WARNING] Ошибка при вставке города', e)
            return False
        
        # Меняем город в таблице times
        sql = f'UPDATE `ArtemsWeatherBot`.`times` SET city = "{city}" WHERE chat_id={chat_id}'
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
        except Exception as e:
            print('[WARNING] Ошибка при вставке города', e)
            return False
        
        return True

    def add_time_by_chatId(self, chat_id: int, time: str) -> bool:
        """
            Эта функция добавляет время в пустую ячейку
        """
        print('Меняем время на:', time)
        sql = (
            f'UPDATE `ArtemsWeatherBot`.`times` SET time="{time}:00" WHERE chat_id={chat_id} AND `time` IS NULL LIMIT 1;'
        )
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
            print('Самый конец функции БД')
            print("Затронуто строк:", self.__cur.rowcount)
            if self.__cur.rowcount == 0:
                return False
            else:
                return True
        except Exception as e:
            print('[WARNING] Ошибка при добавлении нового времени для пользователя', e)
            return False
        
    def get_cities(self) -> list:
        """
            Возвращает список городов
        """
        sql = (
            'SELECT city FROM `ArtemsWeatherBot`.`users`'
        )
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            print(res)
            return res if res else []
        
        except Exception as e:
            print('[WARNING] Ошибка при получении списка городов', e)
    
    def search_by_city_and_nowtime(self, city: str) -> tuple:
        """
            Получает список пользователей по городу и времени\n
            Возвращает [{'id': '', 'chat_id':'', 'time':'', 'city':''}, {'id': '', 'chat_id':'', 'time':'', 'city':''} ...]
        """
        # Получение текущего времени
        current_time = datetime.datetime.now().strftime('%H:%M')
        # Создание объекта временной погрешности
        time_difference = datetime.timedelta(minutes=1)

        # Расчет временных интервалов
        start_time = (datetime.datetime.strptime(current_time, '%H:%M') - time_difference).strftime('%H:%M')
        end_time = (datetime.datetime.strptime(current_time, '%H:%M') + time_difference).strftime('%H:%M')
        sql = (
            f"SELECT * FROM `ArtemsWeatherBot`.`times` WHERE `city`='{city}' and `time` BETWEEN '{start_time}' AND '{end_time}' "
        )
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            return res if res else []
        
        except Exception as e:
            print('[WARNING] Ошибка при получении списка пользователей по городу', e)

    def search_nowtime(self, time: str) -> tuple:
        """
            Получает список пользователей которым нужно отправить погоду в текущее время
        """
        sql = (
            f'SELECT * FROM `ArtemsWeatherBot`.`times` where time = {time}'
        )
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            return res if res else []
        
        except Exception as e:
            print('[WARNING] Ошибка при получении списка пользователей по времени', e)
    
    def search_user_in_times(self, chat_id: int) -> tuple:
        """
            проверяет указано ли время у конкретного пользователя в таблице times
        """
        sql = (
            f'SELECT time FROM `ArtemsWeatherBot`.`times` where chat_id={chat_id}'
        )
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            print(res)
            return res if res else []
        
        except Exception as e:
            print('[WARNING] Ошибка при получении времени конкретного пользователя в `times`', e)
            return False

    