CREATE TABLE IF NOT EXISTS `ArtemsWeatherBot`.`users` (
    id int NOT NULL AUTO_INCREMENT,
    username text NOT NULL,
    chat_id int NOT NULL,
    city text NULL,
    reg_date datetime NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS `ArtemsWeatherBot`.`times`(
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    time text NULL,
    city text NOT NULL,
    PRIMARY KEY (id)
)