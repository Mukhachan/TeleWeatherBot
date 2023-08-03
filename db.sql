CREATE TABLE IF NOT EXISTS `ArtemsWeatherBot`.`users` (
    id int NOT NULL AUTO_INCREMENT,
    username text NOT NULL,
    chat_id bigint NOT NULL,
    city text NULL,
    reg_date datetime NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS `ArtemsWeatherBot`.`times`(
    id int NOT NULL AUTO_INCREMENT,
    user_id bigint NOT NULL,
    time time NULL,
    city text NOT NULL,
    sending text NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS `ArtemsWeatherBot`.`change_log`(
    id int NOT NULL AUTO_INCREMENT,
    change_text text NOT NULL,
    change_time datetime NOT NULL,
    PRIMARY KEY (id)
)