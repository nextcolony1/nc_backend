ALTER TABLE `asks` ADD `img_id` INT(11) NULL DEFAULT NULL AFTER `cords_ver`;

UPDATE `asks` a, `planets` p
SET a.img_id = p.img_id
WHERE a.category = "planet" AND a.img_id is null AND a.uid = p.id;