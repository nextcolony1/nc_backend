ALTER TABLE `users` ADD `b_battlespeed` DATETIME NULL DEFAULT NULL AFTER `r_Yamato_busy`;

ALTER TABLE `shipstats` ADD `battlespeed` FLOAT NOT NULL AFTER `blueprint`;

UPDATE `shipstats` SET battlespeed = speed;

UPDATE `shipstats` SET battlespeed=5 where variant = 0;
UPDATE `shipstats` SET battlespeed=6 where variant = 2;
UPDATE `shipstats` SET battlespeed=7 where variant = 1;

UPDATE `shipstats` SET battlespeed=2 where variant = 0 and name="scout";
UPDATE `shipstats` SET battlespeed=2 where variant = 0 and name="patrol";
UPDATE `shipstats` SET battlespeed=3 where variant = 0 and name="cutter";
UPDATE `shipstats` SET battlespeed=6 where variant = 0 and name="dreadnought";

UPDATE `shipstats` SET battlespeed=3 where variant = 2 and name="scout2";
UPDATE `shipstats` SET battlespeed=3 where variant = 2 and name="patrol2";
UPDATE `shipstats` SET battlespeed=4 where variant = 2 and name="cutter2";
UPDATE `shipstats` SET battlespeed=7 where variant = 2 and name="dreadnought2";
UPDATE `shipstats` SET battlespeed=7 where variant = 2 and name="carrier2";

UPDATE `shipstats` SET battlespeed=4 where variant = 1 and name="scout1";
UPDATE `shipstats` SET battlespeed=4 where variant = 1 and name="patrol1";
UPDATE `shipstats` SET battlespeed=5 where variant = 1 and name="cutter1";
UPDATE `shipstats` SET battlespeed=8 where variant = 1 and name="dreadnought1";
UPDATE `shipstats` SET battlespeed=8 where variant = 1 and name="carrier1";
UPDATE `shipstats` SET battlespeed=8 where variant = 1 and name="battlecruiser1";

ALTER TABLE `shipstats` ADD `order` INT(11) NOT NULL DEFAULT '0' AFTER `battlespeed`;

UPDATE `shipstats` SET `order` = 100 WHERE `shipstats`.`name` = 'transporter';
UPDATE `shipstats` SET `order` = 101 WHERE `shipstats`.`name` = 'transportship';
UPDATE `shipstats` SET `order` = 110 WHERE `shipstats`.`name` = 'transportship1';
UPDATE `shipstats` SET `order` = 120 WHERE `shipstats`.`name` = 'transportship2';

UPDATE `shipstats` SET `order` = 201 WHERE `shipstats`.`name` = 'explorer';
UPDATE `shipstats` SET `order` = 202 WHERE `shipstats`.`name` = 'explorership';
UPDATE `shipstats` SET `order` = 210 WHERE `shipstats`.`name` = 'explorership1';

UPDATE `shipstats` SET `order` = 300 WHERE `shipstats`.`name` = 'scout';
UPDATE `shipstats` SET `order` = 301 WHERE `shipstats`.`name` = 'scout2';
UPDATE `shipstats` SET `order` = 302 WHERE `shipstats`.`name` = 'scout1';
UPDATE `shipstats` SET `order` = 310 WHERE `shipstats`.`name` = 'patrol';
UPDATE `shipstats` SET `order` = 311 WHERE `shipstats`.`name` = 'patrol2';
UPDATE `shipstats` SET `order` = 312 WHERE `shipstats`.`name` = 'patrol1';
UPDATE `shipstats` SET `order` = 320 WHERE `shipstats`.`name` = 'cutter';
UPDATE `shipstats` SET `order` = 321 WHERE `shipstats`.`name` = 'cutter2';
UPDATE `shipstats` SET `order` = 322 WHERE `shipstats`.`name` = 'cutter1';
UPDATE `shipstats` SET `order` = 330 WHERE `shipstats`.`name` = 'corvette';
UPDATE `shipstats` SET `order` = 331 WHERE `shipstats`.`name` = 'corvette2';
UPDATE `shipstats` SET `order` = 332 WHERE `shipstats`.`name` = 'corvette1';
UPDATE `shipstats` SET `order` = 340 WHERE `shipstats`.`name` = 'frigate';
UPDATE `shipstats` SET `order` = 341 WHERE `shipstats`.`name` = 'frigate2';
UPDATE `shipstats` SET `order` = 342 WHERE `shipstats`.`name` = 'frigate1';
UPDATE `shipstats` SET `order` = 350 WHERE `shipstats`.`name` = 'destroyer';
UPDATE `shipstats` SET `order` = 351 WHERE `shipstats`.`name` = 'destroyer2';
UPDATE `shipstats` SET `order` = 352 WHERE `shipstats`.`name` = 'destroyer1';
UPDATE `shipstats` SET `order` = 360 WHERE `shipstats`.`name` = 'cruiser';
UPDATE `shipstats` SET `order` = 361 WHERE `shipstats`.`name` = 'cruiser2';
UPDATE `shipstats` SET `order` = 362 WHERE `shipstats`.`name` = 'cruiser1';
UPDATE `shipstats` SET `order` = 370 WHERE `shipstats`.`name` = 'battlecruiser';
UPDATE `shipstats` SET `order` = 371 WHERE `shipstats`.`name` = 'battlecruiser2';
UPDATE `shipstats` SET `order` = 372 WHERE `shipstats`.`name` = 'battlecruiser1';
UPDATE `shipstats` SET `order` = 380 WHERE `shipstats`.`name` = 'carrier';
UPDATE `shipstats` SET `order` = 381 WHERE `shipstats`.`name` = 'carrier2';
UPDATE `shipstats` SET `order` = 382 WHERE `shipstats`.`name` = 'carrier1';
UPDATE `shipstats` SET `order` = 390 WHERE `shipstats`.`name` = 'dreadnought';
UPDATE `shipstats` SET `order` = 391 WHERE `shipstats`.`name` = 'dreadnought2';
UPDATE `shipstats` SET `order` = 392 WHERE `shipstats`.`name` = 'dreadnought1';

UPDATE `shipstats` SET `order` = 400 WHERE `shipstats`.`name` = 'yamato';
UPDATE `shipstats` SET `order` = 401 WHERE `shipstats`.`name` = 'yamato1';
UPDATE `shipstats` SET `order` = 402 WHERE `shipstats`.`name` = 'yamato2';
UPDATE `shipstats` SET `order` = 403 WHERE `shipstats`.`name` = 'yamato3';
UPDATE `shipstats` SET `order` = 404 WHERE `shipstats`.`name` = 'yamato4';
UPDATE `shipstats` SET `order` = 405 WHERE `shipstats`.`name` = 'yamato5';
UPDATE `shipstats` SET `order` = 406 WHERE `shipstats`.`name` = 'yamato6';
UPDATE `shipstats` SET `order` = 407 WHERE `shipstats`.`name` = 'yamato7';
UPDATE `shipstats` SET `order` = 408 WHERE `shipstats`.`name` = 'yamato8';
UPDATE `shipstats` SET `order` = 409 WHERE `shipstats`.`name` = 'yamato9';
UPDATE `shipstats` SET `order` = 410 WHERE `shipstats`.`name` = 'yamato10';
UPDATE `shipstats` SET `order` = 411 WHERE `shipstats`.`name` = 'yamato11';
UPDATE `shipstats` SET `order` = 412 WHERE `shipstats`.`name` = 'yamato12';
UPDATE `shipstats` SET `order` = 413 WHERE `shipstats`.`name` = 'yamato13';
UPDATE `shipstats` SET `order` = 414 WHERE `shipstats`.`name` = 'yamato14';
UPDATE `shipstats` SET `order` = 415 WHERE `shipstats`.`name` = 'yamato15';
UPDATE `shipstats` SET `order` = 416 WHERE `shipstats`.`name` = 'yamato16';
UPDATE `shipstats` SET `order` = 417 WHERE `shipstats`.`name` = 'yamato17';
UPDATE `shipstats` SET `order` = 418 WHERE `shipstats`.`name` = 'yamato18';
UPDATE `shipstats` SET `order` = 419 WHERE `shipstats`.`name` = 'yamato19';
UPDATE `shipstats` SET `order` = 420 WHERE `shipstats`.`name` = 'yamato20';

INSERT INTO `buffs` (`id`, `name`, `price`, `buff_duration`) VALUES (NULL, 'battlespeed', '500000000000', '7');