import datetime


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
                    f'INSERT INTO `ArtemsWeatherBot`.`times` VALUES(NULL, {chat_id}, NULL, NULL, "True")'
                )
                self.__cur.execute(sql)
                self.__connection.commit()
        except Exception as e:
            print('[WARNING] При сохранении времени возникла ошибка', e)
            return False
        
        self.change_log(f'Регистрация нового пользователя {username}')

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

    async def add_time_by_chatId(self, chat_id: int, time: str) -> bool:
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
                self.change_log(f'Смена времени у пользовател {chat_id}')
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
        # sql = (
        #     f"SELECT * FROM `ArtemsWeatherBot`.`times` WHERE `city`='{city}' and `time` BETWEEN '{start_time}' AND '{end_time}' "
        # )
        sql = (
            f"SELECT * FROM `ArtemsWeatherBot`.`times` WHERE `city`='{city}' and `time`='{current_time}' and `sending`='True'"
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

    async def search_by_ChatId_and_time(self, chat_id: int, time: str) -> tuple:
        """
            Ищет запись по chat_id и time и заменяет time на newtime
        """
        time = f'"{time}:00"' if ':' in time else 'NULL'
        sql = (
            f'UPDATE `ArtemsWeatherBot`.`times` SET time=NULL WHERE chat_id={chat_id} AND `time`={time} '
        )
        print(time, sql)
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
            print("Затронуто строк:", self.__cur.rowcount)
            if self.__cur.rowcount == 0:
                return False
            else:
                return True
        except Exception as e:
            print('[WARNING] Ошибка при добавлении нового времени для пользователя', e)
            return False

    def change_log(self, change_text: str) -> bool:
        """
            Это просто функция для логгирования всяких важных событий
        """
        change_time = datetime.datetime.now()

        sql = (
            f'INSERT INTO `ArtemsWeatherBot`.`change_log` VALUES(NULL, "{change_text}", "{change_time}")'
        )
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            print('[WARNING] При создании лога возникла ошибка', e)
            return False
    
    def change_sending(self, chat_id: int, text: str) -> bool:
        """
            Меняет значение в столбце sending
        """
        sql = f'UPDATE `ArtemsWeatherBot`.`times` SET sending = "{text}" WHERE chat_id={chat_id}'
        try:
            self.__cur.execute(sql)
            self.__connection.commit()
            return True
        except Exception as e:
            print('[WARNING] Произошла ошибка при изменении отправки:', e)
            return False
        