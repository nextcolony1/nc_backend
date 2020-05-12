ALTER TABLE `transactions` ADD INDEX( `user`, `tr_type`, `date`, `virtualop`, `error`);
ALTER TABLE `transactions` ADD INDEX(`tr_type`, `date`, `virtualop`, `error`);
ALTER TABLE `transactions` ADD INDEX( `user`, `date`, `virtualop`, `error`);
ALTER TABLE `transactions` ADD INDEX(  `date`, `virtualop`, `error`);
ALTER TABLE `missions` ADD INDEX( `user`, `busy_until`, `cords_hor`, `cords_ver`);
ALTER TABLE `missions` ADD INDEX( `user`, `busy_until`, `cords_hor_dest`, `cords_ver_dest`);
ALTER TABLE `missions` ADD INDEX( `user`, `mission_type`, `busy_until`, `busy_until_return`, `cords_hor`, `cords_ver`);
ALTER TABLE `missions` ADD INDEX( `user`, `mission_type`, `busy_until`, `busy_until_return`, `cords_hor_dest`, `cords_ver_dest`);
ALTER TABLE `ships` ADD INDEX( `user`, `cords_hor`, `cords_ver`, `busy_until`);
ALTER TABLE `missions` ADD INDEX( `user`, `mission_type`, `cancel_trx`, `cords_hor_dest`, `cords_ver_dest`);

ALTER TABLE `missions` ADD INDEX(`busy_until`, `cords_hor`, `cords_ver`);
ALTER TABLE `missions` ADD INDEX(`busy_until`, `cords_hor_dest`, `cords_ver_dest`);
ALTER TABLE `missions` ADD INDEX(`mission_type`, `busy_until`, `busy_until_return`, `cords_hor`, `cords_ver`);
ALTER TABLE `missions` ADD INDEX(`mission_type`, `busy_until`, `busy_until_return`, `cords_hor_dest`, `cords_ver_dest`);
ALTER TABLE `missions` ADD `destroyed` BOOLEAN NOT NULL DEFAULT FALSE AFTER `returning`;