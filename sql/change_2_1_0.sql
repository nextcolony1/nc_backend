CREATE TABLE `asks` (
  `id` varchar(50) NOT NULL,
  `category` varchar(50) NOT NULL,
  `subcategory` varchar(50) NOT NULL,
  `type` varchar(50) NOT NULL,
  `uid` varchar(50) NOT NULL,
  `price` bigint(20) NOT NULL,
  `fee_burn` bigint(20) NOT NULL,
  `market` varchar(16) DEFAULT NULL,
  `fee_market` bigint(20) NOT NULL,
  `date` datetime NOT NULL,
  `user` varchar(16) NOT NULL,
  `cancel_trx` varchar(50) DEFAULT NULL,
  `buy_trx` varchar(50) DEFAULT NULL,
  `sold` datetime DEFAULT NULL,
  `failed` datetime DEFAULT NULL,
  `cords_hor` int(11) DEFAULT NULL,
  `cords_ver` int(11) DEFAULT NULL
); 

ALTER TABLE `asks`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `cords` (`cords_hor`,`cords_ver`) USING BTREE,
  ADD KEY `active` (`cancel_trx`,`buy_trx`,`sold`,`failed`) USING BTREE,
  ADD KEY `user` (`user`) USING BTREE,
  ADD KEY `user_active` (`user`,`cancel_trx`,`buy_trx`,`sold`,`failed`) USING BTREE,
  ADD KEY `type_active` (`type`,`cancel_trx`,`buy_trx`,`sold`,`failed`) USING BTREE,
  ADD KEY `uid` (`uid`) USING BTREE;


ALTER TABLE `items` ADD `for_sale` TINYINT(1) NOT NULL DEFAULT '0' AFTER `last_owner`;
ALTER TABLE `ships` ADD `for_sale` TINYINT(1) NOT NULL DEFAULT '0' AFTER `home_planet_id`;
ALTER TABLE `planets` ADD `for_sale` TINYINT(1) NOT NULL DEFAULT '0' AFTER `abandoned`;

DROP TABLE `market`;

ALTER TABLE `shipstats` ADD `blueprint` TINYINT(1) NOT NULL DEFAULT '1' AFTER `shipyard_level`;

UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'scout';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'patrol';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'cutter';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'corvette';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'frigate';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'destroyer';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'cruiser';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'battlecruiser';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'carrier';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'dreadnought';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'transportship';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'explorership';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'transporter';
UPDATE `shipstats` SET `blueprint` = '0' WHERE `name` = 'explorer';