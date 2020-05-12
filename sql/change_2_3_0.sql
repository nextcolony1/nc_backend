ALTER TABLE `users` ADD `b_missioncontrol` DATETIME NULL DEFAULT NULL AFTER `r_missioncontrol`;

CREATE TABLE `buffs` ( `id` INT(11) NOT NULL AUTO_INCREMENT , `name` VARCHAR(256) NOT NULL , `price` BIGINT(20) NOT NULL , `buff_duration` INT(11) NOT NULL , PRIMARY KEY (`id`) USING BTREE) ENGINE = InnoDB;

INSERT INTO `buffs` (`id`, `name`, `price`, `buff_duration`) VALUES (NULL, 'missioncontrol', '1000000000000', '7');