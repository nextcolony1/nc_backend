-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Erstellungszeit: 11. Mai 2019 um 16:05
-- Server-Version: 5.7.25-0ubuntu0.18.04.2
-- PHP-Version: 7.2.15-0ubuntu0.18.04.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Datenbank: `steembattle`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `activity`
--

CREATE TABLE `activity` (
  `id` int(11) NOT NULL,
  `mission_id` varchar(50) NOT NULL,
  `user` varchar(20) DEFAULT NULL,
  `type` varchar(256) NOT NULL,
  `cords_hor` int(11) NOT NULL,
  `cords_ver` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `result` varchar(256) DEFAULT NULL,
  `new_planet_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `auction`
--

CREATE TABLE `auction` (
  `trx_id` int(11) NOT NULL,
  `steem_trx` varchar(256) NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `bid` float NOT NULL,
  `planet_id` int(11) NOT NULL,
  `user` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `items`
--

CREATE TABLE `items` (
  `uid` varchar(255) NOT NULL,
  `owner` varchar(16) NOT NULL,
  `date` datetime NOT NULL,
  `trx_id` varchar(50) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `itemid` varchar(255) NOT NULL,
  `activated_trx` varchar(255) DEFAULT NULL,
  `activated_date` datetime DEFAULT NULL,
  `activated_to` varchar(255) DEFAULT NULL,
  `item_gifted_at` datetime DEFAULT NULL,
  `last_owner` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `missions`
--

CREATE TABLE `missions` (
  `mission_id` varchar(50) NOT NULL,
  `user` varchar(20) NOT NULL,
  `mission_type` varchar(256) NOT NULL,
  `date` datetime NOT NULL,
  `busy_until` datetime DEFAULT NULL,
  `busy_until_return` datetime DEFAULT NULL,
  `cancel_trx` varchar(50) DEFAULT NULL,
  `cords_hor` int(11) DEFAULT NULL,
  `cords_ver` int(11) DEFAULT NULL,
  `cords_hor_dest` int(11) DEFAULT NULL,
  `cords_ver_dest` int(11) DEFAULT NULL,
  `n_explorership` int(11) NOT NULL DEFAULT '0',
  `n_transportship` int(11) NOT NULL DEFAULT '0',
  `n_corvette` int(11) NOT NULL DEFAULT '0',
  `n_frigate` int(11) NOT NULL DEFAULT '0',
  `n_destroyer` int(11) NOT NULL DEFAULT '0',
  `n_cruiser` int(11) NOT NULL DEFAULT '0',
  `n_battlecruiser` int(11) NOT NULL DEFAULT '0',
  `n_carrier` int(11) NOT NULL DEFAULT '0',
  `n_dreadnought` int(11) NOT NULL DEFAULT '0',
  `qyt_coal` int(11) NOT NULL DEFAULT '0',
  `qyt_ore` int(11) NOT NULL DEFAULT '0',
  `qyt_copper` int(11) NOT NULL DEFAULT '0',
  `qyt_uranium` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `planetlevels`
--

CREATE TABLE `planetlevels` (
  `id` int(11) NOT NULL,
  `rarity` int(1) NOT NULL,
  `p_bonus_percentage` float NOT NULL,
  `name` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `planetlevels`
--

INSERT INTO `planetlevels` (`id`, `rarity`, `p_bonus_percentage`, `name`) VALUES
(1, 1, 0, 'common'),
(2, 2, 10, 'uncommon'),
(3, 3, 20, 'rare'),
(4, 4, 100, 'legendary'),
(5, 0, 0, 'undefined');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `planets`
--

CREATE TABLE `planets` (
  `id` varchar(50) NOT NULL,
  `img_id` int(11) DEFAULT NULL,
  `name` varchar(20) DEFAULT NULL,
  `bonus` int(11) DEFAULT NULL,
  `planet_type` int(2) DEFAULT NULL,
  `user` varchar(20) DEFAULT NULL,
  `qyt_uranium` float DEFAULT NULL,
  `qyt_ore` float DEFAULT NULL,
  `qyt_copper` float DEFAULT NULL,
  `qyt_coal` float DEFAULT NULL,
  `rate_coal` double NOT NULL DEFAULT '0',
  `rate_ore` double NOT NULL DEFAULT '0',
  `rate_copper` double NOT NULL DEFAULT '0',
  `rate_uranium` double NOT NULL DEFAULT '0',
  `depot_coal` double NOT NULL DEFAULT '0',
  `depot_ore` double NOT NULL DEFAULT '0',
  `depot_copper` double NOT NULL DEFAULT '0',
  `depot_uranium` double NOT NULL DEFAULT '0',
  `level_uranium` int(11) DEFAULT NULL,
  `level_ore` int(11) DEFAULT NULL,
  `level_copper` int(11) DEFAULT NULL,
  `level_coal` int(11) DEFAULT NULL,
  `level_ship` int(11) DEFAULT NULL,
  `ship_current` int(11) DEFAULT NULL,
  `level_base` int(11) DEFAULT NULL,
  `level_bunker` int(11) DEFAULT NULL,
  `level_shieldgenerator` int(11) DEFAULT NULL,
  `level_research` int(11) DEFAULT NULL,
  `level_coaldepot` int(11) DEFAULT NULL,
  `level_oredepot` int(11) DEFAULT NULL,
  `level_copperdepot` int(11) DEFAULT NULL,
  `level_uraniumdepot` int(11) DEFAULT NULL,
  `level_shipyard` int(11) DEFAULT NULL,
  `ore_busy` datetime DEFAULT NULL,
  `copper_busy` datetime DEFAULT NULL,
  `coal_busy` datetime DEFAULT NULL,
  `uranium_busy` datetime DEFAULT NULL,
  `research_busy` datetime DEFAULT NULL,
  `base_busy` datetime DEFAULT NULL,
  `bunker_busy` datetime DEFAULT NULL,
  `shieldgenerator_busy` datetime DEFAULT NULL,
  `shipyard_busy` datetime DEFAULT NULL,
  `oredepot_busy` datetime DEFAULT NULL,
  `coaldepot_busy` datetime DEFAULT NULL,
  `copperdepot_busy` datetime DEFAULT NULL,
  `uraniumdepot_busy` datetime DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `cords_hor` int(11) NOT NULL,
  `cords_ver` int(11) NOT NULL,
  `date_disc` datetime DEFAULT NULL,
  `trx_id` varchar(50) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `qyp_uranium` int(11) DEFAULT NULL,
  `boost_percentage` float DEFAULT NULL,
  `booster_activate_trx` varchar(50) DEFAULT NULL,
  `startplanet` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `planettypes`
--

CREATE TABLE `planettypes` (
  `id` int(11) NOT NULL,
  `type` varchar(256) NOT NULL,
  `type_id` int(11) NOT NULL,
  `uraniummine` int(1) NOT NULL,
  `coalmine` int(1) NOT NULL,
  `coppermine` int(1) NOT NULL,
  `oremine` int(1) NOT NULL,
  `base` int(1) NOT NULL,
  `researchcenter` int(1) NOT NULL,
  `shipyard` int(1) NOT NULL,
  `oredepot` int(1) NOT NULL,
  `coaldepot` int(1) NOT NULL,
  `copperdepot` int(1) NOT NULL,
  `uraniumdepot` int(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `planettypes`
--

INSERT INTO `planettypes` (`id`, `type`, `type_id`, `uraniummine`, `coalmine`, `coppermine`, `oremine`, `base`, `researchcenter`, `shipyard`, `oredepot`, `coaldepot`, `copperdepot`, `uraniumdepot`) VALUES
(1, 'earth', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
(2, 'coal', 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
(3, 'ore', 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
(4, 'copper', 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
(5, 'uranium', 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `productivity`
--

CREATE TABLE `productivity` (
  `id` int(11) NOT NULL,
  `name` varchar(256) NOT NULL,
  `level` int(11) NOT NULL,
  `coal` int(11) DEFAULT NULL,
  `ore` int(11) DEFAULT NULL,
  `copper` int(11) DEFAULT NULL,
  `uranium` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `productivity`
--

INSERT INTO `productivity` (`id`, `name`, `level`, `coal`, `ore`, `copper`, `uranium`) VALUES
(1, 'coalmine', 1, 80, 0, 0, 0),
(2, 'coalmine', 2, 160, 0, 0, 0),
(3, 'coalmine', 3, 240, 0, 0, 0),
(4, 'coalmine', 4, 320, 0, 0, 0),
(5, 'coalmine', 5, 400, 0, 0, 0),
(6, 'coalmine', 6, 480, 0, 0, 0),
(7, 'coalmine', 7, 560, 0, 0, 0),
(8, 'coalmine', 8, 640, 0, 0, 0),
(9, 'coalmine', 9, 720, 0, 0, 0),
(10, 'coalmine', 10, 800, 0, 0, 0),
(11, 'coalmine', 11, 880, 0, 0, 0),
(12, 'coalmine', 12, 960, 0, 0, 0),
(13, 'coalmine', 13, 1040, 0, 0, 0),
(14, 'coalmine', 14, 1120, 0, 0, 0),
(15, 'coalmine', 15, 1200, 0, 0, 0),
(16, 'coalmine', 16, 1280, 0, 0, 0),
(17, 'coalmine', 17, 1360, 0, 0, 0),
(18, 'coalmine', 18, 1440, 0, 0, 0),
(19, 'coalmine', 19, 1520, 0, 0, 0),
(20, 'coalmine', 20, 1600, 0, 0, 0),
(21, 'oremine', 1, 0, 40, 0, 0),
(22, 'oremine', 2, 0, 80, 0, 0),
(23, 'oremine', 3, 0, 120, 0, 0),
(24, 'oremine', 4, 0, 160, 0, 0),
(25, 'oremine', 5, 0, 200, 0, 0),
(26, 'oremine', 6, 0, 240, 0, 0),
(27, 'oremine', 7, 0, 280, 0, 0),
(28, 'oremine', 8, 0, 320, 0, 0),
(29, 'oremine', 9, 0, 360, 0, 0),
(30, 'oremine', 10, 0, 400, 0, 0),
(31, 'oremine', 11, 0, 440, 0, 0),
(32, 'oremine', 12, 0, 480, 0, 0),
(33, 'oremine', 13, 0, 520, 0, 0),
(34, 'oremine', 14, 0, 560, 0, 0),
(35, 'oremine', 15, 0, 600, 0, 0),
(36, 'oremine', 16, 0, 640, 0, 0),
(37, 'oremine', 17, 0, 680, 0, 0),
(38, 'oremine', 18, 0, 720, 0, 0),
(39, 'oremine', 19, 0, 760, 0, 0),
(40, 'oremine', 20, 0, 800, 0, 0),
(41, 'coppermine', 1, 0, 0, 20, 0),
(42, 'coppermine', 2, 0, 0, 40, 0),
(43, 'coppermine', 3, 0, 0, 60, 0),
(44, 'coppermine', 4, 0, 0, 80, 0),
(45, 'coppermine', 5, 0, 0, 100, 0),
(46, 'coppermine', 6, 0, 0, 120, 0),
(47, 'coppermine', 7, 0, 0, 140, 0),
(48, 'coppermine', 8, 0, 0, 160, 0),
(49, 'coppermine', 9, 0, 0, 180, 0),
(50, 'coppermine', 10, 0, 0, 200, 0),
(51, 'coppermine', 11, 0, 0, 220, 0),
(52, 'coppermine', 12, 0, 0, 240, 0),
(53, 'coppermine', 13, 0, 0, 260, 0),
(54, 'coppermine', 14, 0, 0, 280, 0),
(55, 'coppermine', 15, 0, 0, 300, 0),
(56, 'coppermine', 16, 0, 0, 320, 0),
(57, 'coppermine', 17, 0, 0, 340, 0),
(58, 'coppermine', 18, 0, 0, 360, 0),
(59, 'coppermine', 19, 0, 0, 380, 0),
(60, 'coppermine', 20, 0, 0, 400, 0),
(61, 'uraniummine', 1, 0, 0, 0, 10),
(62, 'uraniummine', 2, 0, 0, 0, 20),
(63, 'uraniummine', 3, 0, 0, 0, 30),
(64, 'uraniummine', 4, 0, 0, 0, 40),
(65, 'uraniummine', 5, 0, 0, 0, 50),
(66, 'uraniummine', 6, 0, 0, 0, 60),
(67, 'uraniummine', 7, 0, 0, 0, 70),
(68, 'uraniummine', 8, 0, 0, 0, 80),
(69, 'uraniummine', 9, 0, 0, 0, 90),
(70, 'uraniummine', 10, 0, 0, 0, 100),
(71, 'uraniummine', 11, 0, 0, 0, 110),
(72, 'uraniummine', 12, 0, 0, 0, 120),
(73, 'uraniummine', 13, 0, 0, 0, 130),
(74, 'uraniummine', 14, 0, 0, 0, 140),
(75, 'uraniummine', 15, 0, 0, 0, 150),
(76, 'uraniummine', 16, 0, 0, 0, 160),
(77, 'uraniummine', 17, 0, 0, 0, 170),
(78, 'uraniummine', 18, 0, 0, 0, 180),
(79, 'uraniummine', 19, 0, 0, 0, 190),
(80, 'uraniummine', 20, 0, 0, 0, 200),
(81, 'coaldepot', 1, 240, 0, 0, 0),
(82, 'coaldepot', 2, 480, 0, 0, 0),
(83, 'coaldepot', 3, 720, 0, 0, 0),
(84, 'coaldepot', 4, 960, 0, 0, 0),
(85, 'coaldepot', 5, 1200, 0, 0, 0),
(86, 'coaldepot', 6, 1440, 0, 0, 0),
(87, 'coaldepot', 7, 1680, 0, 0, 0),
(88, 'coaldepot', 8, 1920, 0, 0, 0),
(89, 'coaldepot', 9, 2160, 0, 0, 0),
(90, 'coaldepot', 10, 2400, 0, 0, 0),
(91, 'coaldepot', 11, 2640, 0, 0, 0),
(92, 'coaldepot', 12, 2880, 0, 0, 0),
(93, 'coaldepot', 13, 3120, 0, 0, 0),
(94, 'coaldepot', 14, 3360, 0, 0, 0),
(95, 'coaldepot', 15, 3600, 0, 0, 0),
(96, 'coaldepot', 16, 3840, 0, 0, 0),
(97, 'coaldepot', 17, 4080, 0, 0, 0),
(98, 'coaldepot', 18, 4320, 0, 0, 0),
(99, 'coaldepot', 19, 4560, 0, 0, 0),
(100, 'coaldepot', 20, 4800, 0, 0, 0),
(101, 'copperdepot', 1, 0, 0, 60, 0),
(102, 'copperdepot', 2, 0, 0, 120, 0),
(103, 'copperdepot', 3, 0, 0, 180, 0),
(104, 'copperdepot', 4, 0, 0, 240, 0),
(105, 'copperdepot', 5, 0, 0, 300, 0),
(106, 'copperdepot', 6, 0, 0, 360, 0),
(107, 'copperdepot', 7, 0, 0, 420, 0),
(108, 'copperdepot', 8, 0, 0, 480, 0),
(109, 'copperdepot', 9, 0, 0, 540, 0),
(110, 'copperdepot', 10, 0, 0, 600, 0),
(111, 'copperdepot', 11, 0, 0, 660, 0),
(112, 'copperdepot', 12, 0, 0, 720, 0),
(113, 'copperdepot', 13, 0, 0, 780, 0),
(114, 'copperdepot', 14, 0, 0, 840, 0),
(115, 'copperdepot', 15, 0, 0, 900, 0),
(116, 'copperdepot', 16, 0, 0, 960, 0),
(117, 'copperdepot', 17, 0, 0, 1020, 0),
(118, 'copperdepot', 18, 0, 0, 1080, 0),
(119, 'copperdepot', 19, 0, 0, 1140, 0),
(120, 'copperdepot', 20, 0, 0, 1200, 0),
(121, 'oredepot', 1, 0, 120, 0, 0),
(122, 'oredepot', 2, 0, 240, 0, 0),
(123, 'oredepot', 3, 0, 360, 0, 0),
(124, 'oredepot', 4, 0, 480, 0, 0),
(125, 'oredepot', 5, 0, 600, 0, 0),
(126, 'oredepot', 6, 0, 720, 0, 0),
(127, 'oredepot', 7, 0, 840, 0, 0),
(128, 'oredepot', 8, 0, 960, 0, 0),
(129, 'oredepot', 9, 0, 1080, 0, 0),
(130, 'oredepot', 10, 0, 1200, 0, 0),
(131, 'oredepot', 11, 0, 1320, 0, 0),
(132, 'oredepot', 12, 0, 1440, 0, 0),
(133, 'oredepot', 13, 0, 1560, 0, 0),
(134, 'oredepot', 14, 0, 1680, 0, 0),
(135, 'oredepot', 15, 0, 1800, 0, 0),
(136, 'oredepot', 16, 0, 1920, 0, 0),
(137, 'oredepot', 17, 0, 2040, 0, 0),
(138, 'oredepot', 18, 0, 2160, 0, 0),
(139, 'oredepot', 19, 0, 2280, 0, 0),
(140, 'oredepot', 20, 0, 2400, 0, 0),
(141, 'uraniumdepot', 1, 0, 0, 0, 30),
(142, 'uraniumdepot', 2, 0, 0, 0, 60),
(143, 'uraniumdepot', 3, 0, 0, 0, 90),
(144, 'uraniumdepot', 4, 0, 0, 0, 120),
(145, 'uraniumdepot', 5, 0, 0, 0, 150),
(146, 'uraniumdepot', 6, 0, 0, 0, 180),
(147, 'uraniumdepot', 7, 0, 0, 0, 210),
(148, 'uraniumdepot', 8, 0, 0, 0, 240),
(149, 'uraniumdepot', 9, 0, 0, 0, 270),
(150, 'uraniumdepot', 10, 0, 0, 0, 300),
(151, 'uraniumdepot', 11, 0, 0, 0, 330),
(152, 'uraniumdepot', 12, 0, 0, 0, 360),
(153, 'uraniumdepot', 13, 0, 0, 0, 390),
(154, 'uraniumdepot', 14, 0, 0, 0, 420),
(155, 'uraniumdepot', 15, 0, 0, 0, 450),
(156, 'uraniumdepot', 16, 0, 0, 0, 480),
(157, 'uraniumdepot', 17, 0, 0, 0, 510),
(158, 'uraniumdepot', 18, 0, 0, 0, 540),
(159, 'uraniumdepot', 19, 0, 0, 0, 570),
(160, 'uraniumdepot', 20, 0, 0, 0, 600),
(161, 'coalmine', 0, 40, 0, 0, 0),
(162, 'oremine', 0, 0, 20, 0, 0),
(163, 'coppermine', 0, 0, 0, 10, 0),
(164, 'uraniummine', 0, 0, 0, 0, 5),
(165, 'coaldepot', 0, 120, 0, 0, 0),
(166, 'oredepot', 0, 0, 60, 0, 0),
(167, 'copperdepot', 0, 0, 0, 30, 0),
(168, 'uraniumdepot', 0, 0, 0, 0, 15),
(169, 'bunker', 1, 13, 7, 3, 2),
(170, 'bunker', 2, 29, 14, 7, 4),
(171, 'bunker', 3, 47, 23, 12, 6),
(172, 'bunker', 4, 67, 34, 17, 8),
(173, 'bunker', 5, 90, 45, 22, 11),
(174, 'bunker', 6, 115, 58, 29, 14),
(175, 'bunker', 7, 143, 71, 36, 18),
(176, 'bunker', 8, 173, 86, 43, 22),
(177, 'bunker', 9, 205, 103, 51, 26),
(178, 'bunker', 10, 240, 120, 60, 30),
(179, 'bunker', 11, 277, 139, 69, 35),
(180, 'bunker', 12, 317, 158, 79, 40),
(181, 'bunker', 13, 359, 179, 90, 45),
(182, 'bunker', 14, 403, 202, 101, 50),
(183, 'bunker', 15, 450, 225, 112, 56),
(184, 'bunker', 16, 499, 250, 125, 62),
(185, 'bunker', 17, 551, 275, 138, 69),
(186, 'bunker', 18, 605, 302, 151, 76),
(187, 'bunker', 19, 661, 331, 165, 83),
(188, 'bunker', 20, 720, 360, 180, 90);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `ranking`
--

CREATE TABLE `ranking` (
  `user` varchar(20) NOT NULL,
  `last_update` datetime NOT NULL,
  `rate_coal` float NOT NULL DEFAULT '0',
  `rate_ore` float NOT NULL DEFAULT '0',
  `rate_copper` float DEFAULT '0',
  `rate_uranium` float NOT NULL DEFAULT '0',
  `meta_rate` float NOT NULL DEFAULT '0',
  `meta_skill` int(11) NOT NULL DEFAULT '0',
  `explorations` int(11) NOT NULL DEFAULT '0',
  `planets` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `ships`
--

CREATE TABLE `ships` (
  `id` varchar(50) NOT NULL,
  `type` varchar(256) NOT NULL,
  `level` int(11) NOT NULL,
  `user` varchar(20) NOT NULL,
  `cords_hor` int(11) NOT NULL,
  `cords_ver` int(11) NOT NULL,
  `qyt_copper` float NOT NULL,
  `qyt_uranium` float NOT NULL,
  `qyt_ore` float NOT NULL,
  `qyt_coal` float NOT NULL,
  `busy_until` datetime(6) NOT NULL,
  `mission_busy_until` datetime NOT NULL DEFAULT '2019-01-01 00:00:00',
  `last_update` datetime(6) NOT NULL,
  `created` datetime DEFAULT NULL,
  `trx_id` varchar(50) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `mission_id` varchar(50) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `home_planet_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `shipstats`
--

CREATE TABLE `shipstats` (
  `name` varchar(256) NOT NULL,
  `longname` varchar(256) DEFAULT NULL,
  `class` varchar(256) DEFAULT NULL,
  `variant` int(11) DEFAULT NULL,
  `variant_name` varchar(20) DEFAULT NULL,
  `level` int(11) NOT NULL,
  `speed` float NOT NULL,
  `consumption` float NOT NULL,
  `structure` int(11) NOT NULL,
  `armor` int(11) NOT NULL,
  `shield` int(11) NOT NULL,
  `rocket` int(11) DEFAULT NULL,
  `bullet` int(11) DEFAULT NULL,
  `laser` int(11) DEFAULT NULL,
  `capacity` int(11) NOT NULL,
  `shipyard_level` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `shipstats`
--

INSERT INTO `shipstats` (`name`, `longname`, `class`, `variant`, `variant_name`, `level`, `speed`, `consumption`, `structure`, `armor`, `shield`, `rocket`, `bullet`, `laser`, `capacity`, `shipyard_level`) VALUES
('battlecruiser', 'Battlecruiser Tiger', 'Battlecruiser', 0, 'rocket', 1, 4, 4, 40, 20, 36, 8, 0, 0, 0, 18),
('battlecruiser1', 'Battlecruiser Lion', 'Battlecruiser', 1, 'bullet', 1, 4, 4, 40, 20, 36, 0, 8, 0, 0, 18),
('battlecruiser2', 'Battlecruiser Leopard', 'Battlecruiser', 2, 'laser', 1, 4, 4, 40, 20, 36, 0, 0, 8, 0, 18),
('carrier', 'Carrier Argus', 'Carrier', 0, 'rocket', 1, 3, 4, 60, 100, 80, 20, 0, 0, 0, 19),
('carrier1', 'Carrier Unicorn', 'Carrier', 1, 'bullet', 1, 3, 4, 60, 100, 80, 0, 20, 0, 0, 19),
('carrier2', 'Carrier Centaur', 'Carrier', 2, 'laser', 1, 3, 4, 60, 100, 80, 0, 0, 20, 0, 19),
('corvette', 'Corvette Crocus', 'Corvette', 0, 'rocket', 1, 8, 1, 6, 8, 10, 2, 0, 0, 0, 14),
('corvette1', 'Corvette Petunia', 'Corvette', 1, 'bullet', 1, 8, 1, 6, 8, 10, 0, 2, 0, 0, 14),
('corvette2', 'Corvette Pimpernel', 'Corvette', 2, 'laser', 1, 8, 1, 6, 8, 10, 0, 0, 2, 0, 14),
('cruiser', 'Cruiser Kent', 'Cruiser', 0, 'rocket', 1, 5, 3, 15, 25, 20, 5, 0, 0, 0, 17),
('cruiser1', 'Cruiser Drake', 'Cruiser', 1, 'bullet', 1, 5, 3, 15, 25, 20, 0, 5, 0, 0, 17),
('cruiser2', 'Cruiser Hogue', 'Cruiser', 2, 'laser', 1, 5, 3, 15, 25, 20, 0, 0, 5, 0, 17),
('destroyer', 'Destroyer Rocket', 'Destroyer', 0, 'rocket', 1, 6, 2, 12, 14, 16, 4, 0, 0, 0, 16),
('destroyer1', 'Destroyer Janus', 'Destroyer', 1, 'bullet', 1, 6, 2, 12, 14, 16, 0, 4, 0, 0, 16),
('destroyer2', 'Destroyer Banshee', 'Destroyer', 2, 'laser', 1, 6, 2, 12, 14, 16, 0, 0, 4, 0, 16),
('dreadnought', 'Dreadnought Royal', 'Dreadnought', 0, 'rocket', 1, 2, 5, 200, 240, 160, 50, 0, 0, 0, 20),
('dreadnought1', 'Dreadnought Imperial', 'Dreadnought', 1, 'bullet', 1, 2, 5, 200, 240, 160, 0, 50, 0, 0, 20),
('dreadnought2', 'Dreadnought Galactic', 'Dreadnought', 2, 'laser', 1, 2, 5, 200, 240, 160, 0, 0, 50, 0, 20),
('explorership', 'Explorer', 'Explorer', 0, NULL, 1, 1, 0.002, 0, 1, 0, NULL, NULL, NULL, 0, 13),
('frigate', 'Frigate Quorn', 'Frigate', 0, 'rocket', 1, 7, 2, 12, 16, 8, 3, 0, 0, 0, 15),
('frigate1', 'Frigate Redmill', 'Frigate', 1, 'bullet', 1, 7, 2, 12, 16, 8, 0, 3, 0, 0, 15),
('frigate2', 'Frigate Lasalle', 'Frigate', 2, 'laser', 1, 7, 2, 12, 16, 8, 0, 0, 3, 0, 15),
('transportship', 'Transporter', 'Transporter', 0, NULL, 1, 2, 0.002, 0, 3, 0, NULL, NULL, NULL, 100, 12);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `shop`
--

CREATE TABLE `shop` (
  `id` int(11) NOT NULL DEFAULT '1',
  `name` varchar(255) NOT NULL,
  `itemid` varchar(255) NOT NULL,
  `prefix` varchar(8) NOT NULL,
  `tradeble` tinyint(1) NOT NULL,
  `activateable` tinyint(1) NOT NULL,
  `sales_per_day` int(11) NOT NULL,
  `max_supply` int(11) DEFAULT NULL,
  `apply_to` varchar(255) NOT NULL,
  `price` float DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `ore` int(11) DEFAULT NULL,
  `coal` int(11) DEFAULT NULL,
  `copper` int(11) DEFAULT NULL,
  `uranium` int(11) DEFAULT NULL,
  `boost_percentage` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `skillcosts`
--

CREATE TABLE `skillcosts` (
  `id` int(11) NOT NULL,
  `name` varchar(256) NOT NULL,
  `level` int(11) NOT NULL,
  `coal` int(11) NOT NULL,
  `ore` int(11) NOT NULL,
  `copper` int(11) NOT NULL,
  `uranium` int(11) NOT NULL,
  `research_time` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `skillcosts`
--

INSERT INTO `skillcosts` (`id`, `name`, `level`, `coal`, `ore`, `copper`, `uranium`, `research_time`) VALUES
(1, 'base', 1, 5, 3, 1, 0, 945),
(2, 'coaldepot', 1, 3, 2, 1, 0, 945),
(3, 'coalmine', 1, 2, 3, 1, 0, 945),
(4, 'copperdepot', 1, 4, 2, 1, 1, 945),
(5, 'coppermine', 1, 4, 1, 0, 1, 945),
(6, 'oredepot', 1, 5, 1, 1, 0, 945),
(7, 'oremine', 1, 6, 1, 1, 0, 945),
(8, 'researchcenter', 1, 4, 2, 1, 1, 945),
(9, 'shipyard', 1, 6, 2, 1, 1, 945),
(10, 'uraniumdepot', 1, 4, 2, 1, 0, 945),
(11, 'uraniummine', 1, 3, 2, 1, 0, 945),
(12, 'base', 2, 11, 5, 3, 1, 1991),
(13, 'coaldepot', 2, 5, 4, 2, 1, 1991),
(14, 'coalmine', 2, 4, 5, 2, 1, 1991),
(15, 'copperdepot', 2, 9, 3, 1, 1, 1991),
(16, 'coppermine', 2, 9, 3, 1, 1, 1991),
(17, 'oredepot', 2, 11, 2, 2, 1, 1991),
(18, 'oremine', 2, 12, 2, 1, 1, 1991),
(19, 'researchcenter', 2, 9, 4, 2, 1, 1991),
(20, 'shipyard', 2, 12, 4, 2, 1, 1991),
(21, 'uraniumdepot', 2, 8, 4, 2, 1, 1991),
(22, 'uraniummine', 2, 7, 4, 3, 0, 1991),
(23, 'base', 3, 16, 8, 4, 1, 3153),
(24, 'coaldepot', 3, 8, 7, 3, 1, 3153),
(25, 'coalmine', 3, 7, 8, 3, 1, 3153),
(26, 'copperdepot', 3, 14, 5, 2, 2, 3153),
(27, 'coppermine', 3, 14, 5, 1, 2, 3153),
(28, 'oredepot', 3, 16, 3, 3, 1, 3153),
(29, 'oremine', 3, 19, 3, 2, 1, 3153),
(30, 'researchcenter', 3, 14, 6, 3, 2, 3153),
(31, 'shipyard', 3, 19, 7, 3, 2, 3153),
(32, 'uraniumdepot', 3, 12, 6, 3, 1, 3153),
(33, 'uraniummine', 3, 11, 6, 4, 1, 3153),
(34, 'base', 4, 22, 11, 5, 2, 4454),
(35, 'coaldepot', 4, 11, 9, 4, 2, 4454),
(36, 'coalmine', 4, 9, 11, 4, 2, 4454),
(37, 'copperdepot', 4, 18, 7, 2, 2, 4454),
(38, 'coppermine', 4, 18, 6, 2, 3, 4454),
(39, 'oredepot', 4, 22, 5, 3, 2, 4454),
(40, 'oremine', 4, 26, 4, 3, 2, 4454),
(41, 'researchcenter', 4, 18, 8, 5, 2, 4454),
(42, 'shipyard', 4, 26, 9, 4, 2, 4454),
(43, 'uraniumdepot', 4, 17, 8, 5, 1, 4454),
(44, 'uraniummine', 4, 15, 8, 5, 1, 4454),
(45, 'base', 5, 28, 14, 7, 2, 5918),
(46, 'coaldepot', 5, 14, 12, 5, 2, 5918),
(47, 'coalmine', 5, 12, 14, 5, 2, 5918),
(48, 'copperdepot', 5, 24, 9, 3, 3, 5918),
(49, 'coppermine', 5, 24, 8, 2, 3, 5918),
(50, 'oredepot', 5, 28, 6, 4, 2, 5918),
(51, 'oremine', 5, 33, 5, 4, 2, 5918),
(52, 'researchcenter', 5, 24, 10, 6, 3, 5918),
(53, 'shipyard', 5, 33, 12, 5, 3, 5918),
(54, 'uraniumdepot', 5, 21, 10, 6, 1, 5918),
(55, 'uraniummine', 5, 19, 10, 7, 1, 5918),
(56, 'base', 6, 35, 17, 8, 3, 7579),
(57, 'coaldepot', 6, 17, 14, 6, 3, 7579),
(58, 'coalmine', 6, 14, 17, 6, 2, 7579),
(59, 'copperdepot', 6, 29, 11, 4, 4, 7579),
(60, 'coppermine', 6, 29, 10, 3, 4, 7579),
(61, 'oredepot', 6, 35, 7, 5, 3, 7579),
(62, 'oremine', 6, 40, 6, 5, 3, 7579),
(63, 'researchcenter', 6, 29, 12, 7, 4, 7579),
(64, 'shipyard', 6, 40, 14, 6, 4, 7579),
(65, 'uraniumdepot', 6, 26, 12, 7, 2, 7579),
(66, 'uraniummine', 6, 23, 12, 8, 2, 7579),
(67, 'base', 7, 42, 20, 10, 4, 9480),
(68, 'coaldepot', 7, 21, 17, 7, 3, 9480),
(69, 'coalmine', 7, 17, 20, 7, 3, 9480),
(70, 'copperdepot', 7, 35, 13, 4, 4, 9480),
(71, 'coppermine', 7, 35, 12, 4, 5, 9480),
(72, 'oredepot', 7, 42, 9, 7, 4, 9480),
(73, 'oremine', 7, 49, 7, 6, 4, 9480),
(74, 'researchcenter', 7, 35, 15, 9, 5, 9480),
(75, 'shipyard', 7, 49, 17, 7, 5, 9480),
(76, 'uraniumdepot', 7, 31, 15, 9, 2, 9480),
(77, 'uraniummine', 7, 28, 15, 10, 2, 9480),
(78, 'base', 8, 49, 24, 12, 4, 11676),
(79, 'coaldepot', 8, 24, 20, 8, 4, 11676),
(80, 'coalmine', 8, 20, 24, 8, 3, 11676),
(81, 'copperdepot', 8, 41, 15, 5, 5, 11676),
(82, 'coppermine', 8, 41, 14, 4, 6, 11676),
(83, 'oredepot', 8, 49, 10, 8, 4, 11676),
(84, 'oremine', 8, 57, 8, 7, 4, 11676),
(85, 'researchcenter', 8, 41, 17, 10, 6, 11676),
(86, 'shipyard', 8, 57, 20, 8, 6, 11676),
(87, 'uraniumdepot', 8, 37, 17, 10, 3, 11676),
(88, 'uraniummine', 8, 33, 17, 12, 2, 11676),
(89, 'base', 9, 56, 27, 14, 5, 14242),
(90, 'coaldepot', 9, 28, 23, 10, 4, 14242),
(91, 'coalmine', 9, 23, 27, 10, 4, 14242),
(92, 'copperdepot', 9, 47, 17, 6, 6, 14242),
(93, 'coppermine', 9, 47, 16, 5, 7, 14242),
(94, 'oredepot', 9, 56, 12, 9, 5, 14242),
(95, 'oremine', 9, 65, 10, 8, 5, 14242),
(96, 'researchcenter', 9, 47, 19, 12, 6, 14242),
(97, 'shipyard', 9, 65, 23, 10, 6, 14242),
(98, 'uraniumdepot', 9, 42, 19, 12, 3, 14242),
(99, 'uraniummine', 9, 37, 19, 14, 2, 14242),
(100, 'base', 10, 63, 31, 15, 6, 17280),
(101, 'coaldepot', 10, 32, 26, 11, 5, 17280),
(102, 'coalmine', 10, 26, 31, 11, 4, 17280),
(103, 'copperdepot', 10, 53, 20, 7, 7, 17280),
(104, 'coppermine', 10, 53, 18, 6, 8, 17280),
(105, 'oredepot', 10, 63, 13, 10, 6, 17280),
(106, 'oremine', 10, 74, 11, 9, 6, 17280),
(107, 'researchcenter', 10, 53, 22, 13, 7, 17280),
(108, 'shipyard', 10, 74, 26, 11, 7, 17280),
(109, 'uraniumdepot', 10, 48, 22, 13, 3, 17280),
(110, 'uraniummine', 10, 42, 22, 15, 3, 17280),
(111, 'base', 11, 106, 74, 31, 11, 20934),
(112, 'coaldepot', 11, 53, 63, 22, 10, 20934),
(113, 'coalmine', 11, 44, 74, 22, 9, 20934),
(114, 'copperdepot', 11, 88, 48, 13, 13, 20934),
(115, 'coppermine', 11, 88, 42, 11, 15, 20934),
(116, 'oredepot', 11, 106, 32, 20, 11, 20934),
(117, 'oremine', 11, 123, 26, 18, 11, 20934),
(118, 'researchcenter', 11, 88, 53, 26, 14, 20934),
(119, 'shipyard', 11, 123, 63, 22, 14, 20934),
(120, 'uraniumdepot', 11, 79, 53, 26, 7, 20934),
(121, 'uraniummine', 11, 70, 53, 31, 6, 20934),
(122, 'base', 12, 230, 161, 67, 24, 25412),
(123, 'coaldepot', 12, 115, 138, 48, 22, 25412),
(124, 'coalmine', 12, 96, 161, 48, 19, 25412),
(125, 'copperdepot', 12, 192, 104, 29, 29, 25412),
(126, 'coppermine', 12, 192, 92, 24, 34, 25412),
(127, 'oredepot', 12, 230, 69, 43, 24, 25412),
(128, 'oremine', 12, 269, 58, 38, 24, 25412),
(129, 'researchcenter', 12, 192, 115, 58, 31, 25412),
(130, 'shipyard', 12, 269, 138, 48, 31, 25412),
(131, 'uraniumdepot', 12, 173, 115, 58, 14, 25412),
(132, 'uraniummine', 12, 154, 115, 67, 12, 25412),
(133, 'Transporter', 1, 134, 69, 24, 16, 25412),
(134, 'Transporter', 2, 202, 104, 36, 23, 25412),
(135, 'Transporter', 3, 269, 138, 48, 31, 25412),
(136, 'Transporter', 4, 336, 173, 60, 39, 25412),
(137, 'Transporter', 5, 403, 207, 72, 47, 25412),
(138, 'Transporter', 6, 470, 242, 84, 55, 25412),
(139, 'Transporter', 7, 538, 276, 96, 62, 25412),
(140, 'Transporter', 8, 605, 311, 108, 70, 25412),
(141, 'Transporter', 9, 672, 346, 120, 78, 25412),
(142, 'Transporter', 10, 739, 380, 132, 86, 25412),
(143, 'Transporter', 11, 806, 415, 144, 94, 25412),
(144, 'Transporter', 12, 874, 449, 156, 101, 25412),
(145, 'Transporter', 13, 941, 484, 168, 109, 25412),
(146, 'Transporter', 14, 1008, 518, 180, 117, 25412),
(147, 'Transporter', 15, 1075, 553, 192, 125, 25412),
(148, 'Transporter', 16, 1142, 588, 204, 133, 25412),
(149, 'Transporter', 17, 1210, 622, 216, 140, 25412),
(150, 'Transporter', 18, 1277, 657, 228, 148, 25412),
(151, 'Transporter', 19, 1344, 691, 240, 156, 25412),
(152, 'Transporter', 20, 1411, 726, 252, 164, 25412),
(153, 'base', 13, 499, 349, 146, 52, 31028),
(154, 'coaldepot', 13, 250, 300, 104, 47, 31028),
(155, 'coalmine', 13, 208, 349, 104, 42, 31028),
(156, 'copperdepot', 13, 416, 225, 62, 62, 31028),
(157, 'coppermine', 13, 416, 200, 52, 73, 31028),
(158, 'oredepot', 13, 499, 150, 94, 52, 31028),
(159, 'oremine', 13, 582, 125, 83, 52, 31028),
(160, 'researchcenter', 13, 416, 250, 125, 68, 31028),
(161, 'shipyard', 13, 582, 300, 104, 68, 31028),
(162, 'uraniumdepot', 13, 374, 250, 125, 31, 31028),
(163, 'uraniummine', 13, 333, 250, 146, 26, 31028),
(164, 'Explorer', 1, 104, 50, 13, 18, 31028),
(165, 'Explorer', 2, 156, 75, 20, 27, 31028),
(166, 'Explorer', 3, 208, 100, 26, 36, 31028),
(167, 'Explorer', 4, 260, 125, 33, 46, 31028),
(168, 'Explorer', 5, 312, 150, 39, 55, 31028),
(169, 'Explorer', 6, 364, 175, 46, 64, 31028),
(170, 'Explorer', 7, 416, 200, 52, 73, 31028),
(171, 'Explorer', 8, 468, 225, 59, 82, 31028),
(172, 'Explorer', 9, 520, 250, 65, 91, 31028),
(173, 'Explorer', 10, 572, 275, 72, 100, 31028),
(174, 'Explorer', 11, 624, 300, 78, 109, 31028),
(175, 'Explorer', 12, 676, 324, 85, 118, 31028),
(176, 'Explorer', 13, 728, 349, 91, 127, 31028),
(177, 'Explorer', 14, 780, 374, 98, 137, 31028),
(178, 'Explorer', 15, 832, 399, 104, 146, 31028),
(179, 'Explorer', 16, 884, 424, 111, 155, 31028),
(180, 'Explorer', 17, 936, 449, 117, 164, 31028),
(181, 'Explorer', 18, 988, 474, 124, 173, 31028),
(182, 'Explorer', 19, 1040, 499, 130, 182, 31028),
(183, 'Explorer', 20, 1092, 524, 137, 191, 31028),
(184, 'base', 14, 806, 470, 282, 84, 38278),
(185, 'coaldepot', 14, 403, 403, 202, 76, 38278),
(186, 'coalmine', 14, 336, 470, 202, 67, 38278),
(187, 'copperdepot', 14, 672, 302, 121, 101, 38278),
(188, 'coppermine', 14, 672, 269, 101, 118, 38278),
(189, 'oredepot', 14, 806, 202, 181, 84, 38278),
(190, 'oremine', 14, 941, 168, 161, 84, 38278),
(191, 'researchcenter', 14, 672, 336, 242, 109, 38278),
(192, 'shipyard', 14, 941, 403, 202, 109, 38278),
(193, 'uraniumdepot', 14, 605, 336, 242, 50, 38278),
(194, 'uraniummine', 14, 538, 336, 282, 42, 38278),
(195, 'Corvette', 1, 56, 78, 34, 11, 38278),
(196, 'Corvette', 2, 84, 118, 50, 17, 38278),
(197, 'Corvette', 3, 112, 157, 67, 22, 38278),
(198, 'Corvette', 4, 140, 196, 84, 28, 38278),
(199, 'Corvette', 5, 168, 235, 101, 34, 38278),
(200, 'Corvette', 6, 196, 274, 118, 39, 38278),
(201, 'Corvette', 7, 224, 314, 134, 45, 38278),
(202, 'Corvette', 8, 252, 353, 151, 50, 38278),
(203, 'Corvette', 9, 280, 392, 168, 56, 38278),
(204, 'Corvette', 10, 308, 431, 185, 62, 38278),
(205, 'Corvette', 11, 336, 470, 202, 67, 38278),
(206, 'Corvette', 12, 364, 510, 218, 73, 38278),
(207, 'Corvette', 13, 392, 549, 235, 78, 38278),
(208, 'Corvette', 14, 420, 588, 252, 84, 38278),
(209, 'Corvette', 15, 448, 627, 269, 90, 38278),
(210, 'Corvette', 16, 476, 666, 286, 95, 38278),
(211, 'Corvette', 17, 504, 706, 302, 101, 38278),
(212, 'Corvette', 18, 532, 745, 319, 106, 38278),
(213, 'Corvette', 19, 560, 784, 336, 112, 38278),
(214, 'Corvette', 20, 588, 823, 353, 118, 38278),
(215, 'base', 15, 1152, 672, 403, 120, 48000),
(216, 'coaldepot', 15, 576, 576, 288, 108, 48000),
(217, 'coalmine', 15, 480, 672, 288, 96, 48000),
(218, 'copperdepot', 15, 960, 432, 173, 144, 48000),
(219, 'coppermine', 15, 960, 384, 144, 168, 48000),
(220, 'oredepot', 15, 1152, 288, 259, 120, 48000),
(221, 'oremine', 15, 1344, 240, 230, 120, 48000),
(222, 'researchcenter', 15, 960, 480, 346, 156, 48000),
(223, 'shipyard', 15, 1344, 576, 288, 156, 48000),
(224, 'uraniumdepot', 15, 864, 480, 346, 72, 48000),
(225, 'uraniummine', 15, 768, 480, 403, 60, 48000),
(226, 'Frigate', 1, 120, 48, 18, 21, 48000),
(227, 'Frigate', 2, 180, 72, 27, 32, 48000),
(228, 'Frigate', 3, 240, 96, 36, 42, 48000),
(229, 'Frigate', 4, 300, 120, 45, 53, 48000),
(230, 'Frigate', 5, 360, 144, 54, 63, 48000),
(231, 'Frigate', 6, 420, 168, 63, 74, 48000),
(232, 'Frigate', 7, 480, 192, 72, 84, 48000),
(233, 'Frigate', 8, 540, 216, 81, 95, 48000),
(234, 'Frigate', 9, 600, 240, 90, 105, 48000),
(235, 'Frigate', 10, 660, 264, 99, 116, 48000),
(236, 'Frigate', 11, 720, 288, 108, 126, 48000),
(237, 'Frigate', 12, 780, 312, 117, 137, 48000),
(238, 'Frigate', 13, 840, 336, 126, 147, 48000),
(239, 'Frigate', 14, 900, 360, 135, 158, 48000),
(240, 'Frigate', 15, 960, 384, 144, 168, 48000),
(241, 'Frigate', 16, 1020, 408, 153, 179, 48000),
(242, 'Frigate', 17, 1080, 432, 162, 189, 48000),
(243, 'Frigate', 18, 1140, 456, 171, 200, 48000),
(244, 'Frigate', 19, 1200, 480, 180, 210, 48000),
(245, 'Frigate', 20, 1260, 504, 189, 221, 48000),
(246, 'base', 16, 1536, 896, 538, 160, 61714),
(247, 'coaldepot', 16, 768, 768, 384, 144, 61714),
(248, 'coalmine', 16, 640, 896, 384, 128, 61714),
(249, 'copperdepot', 16, 1280, 576, 230, 192, 61714),
(250, 'coppermine', 16, 1280, 512, 192, 224, 61714),
(251, 'oredepot', 16, 1536, 384, 346, 160, 61714),
(252, 'oremine', 16, 1792, 320, 307, 160, 61714),
(253, 'researchcenter', 16, 1280, 640, 461, 208, 61714),
(254, 'shipyard', 16, 1792, 768, 384, 208, 61714),
(255, 'uraniumdepot', 16, 1152, 640, 461, 96, 61714),
(256, 'uraniummine', 16, 1024, 640, 538, 80, 61714),
(257, 'Destroyer', 1, 128, 51, 19, 22, 61714),
(258, 'Destroyer', 2, 192, 77, 29, 34, 61714),
(259, 'Destroyer', 3, 256, 102, 38, 45, 61714),
(260, 'Destroyer', 4, 320, 128, 48, 56, 61714),
(261, 'Destroyer', 5, 384, 154, 58, 67, 61714),
(262, 'Destroyer', 6, 448, 179, 67, 78, 61714),
(263, 'Destroyer', 7, 512, 205, 77, 90, 61714),
(264, 'Destroyer', 8, 576, 230, 86, 101, 61714),
(265, 'Destroyer', 9, 640, 256, 96, 112, 61714),
(266, 'Destroyer', 10, 704, 282, 106, 123, 61714),
(267, 'Destroyer', 11, 768, 307, 115, 134, 61714),
(268, 'Destroyer', 12, 832, 333, 125, 146, 61714),
(269, 'Destroyer', 13, 896, 358, 134, 157, 61714),
(270, 'Destroyer', 14, 960, 384, 144, 168, 61714),
(271, 'Destroyer', 15, 1024, 410, 154, 179, 61714),
(272, 'Destroyer', 16, 1088, 435, 163, 190, 61714),
(273, 'Destroyer', 17, 1152, 461, 173, 202, 61714),
(274, 'Destroyer', 18, 1216, 486, 182, 213, 61714),
(275, 'Destroyer', 19, 1280, 512, 192, 224, 61714),
(276, 'Destroyer', 20, 1344, 538, 202, 235, 61714),
(277, 'base', 17, 1958, 1142, 571, 245, 82517),
(278, 'coaldepot', 17, 979, 979, 408, 220, 82517),
(279, 'coalmine', 17, 816, 1142, 408, 196, 82517),
(280, 'copperdepot', 17, 1632, 734, 245, 294, 82517),
(281, 'coppermine', 17, 1632, 653, 204, 343, 82517),
(282, 'oredepot', 17, 1958, 490, 367, 245, 82517),
(283, 'oremine', 17, 2285, 408, 326, 245, 82517),
(284, 'researchcenter', 17, 1632, 816, 490, 318, 82517),
(285, 'shipyard', 17, 2285, 979, 408, 318, 82517),
(286, 'uraniumdepot', 17, 1469, 816, 490, 147, 82517),
(287, 'uraniummine', 17, 1306, 816, 571, 122, 82517),
(288, 'Cruiser', 1, 136, 54, 17, 29, 82517),
(289, 'Cruiser', 2, 204, 82, 26, 43, 82517),
(290, 'Cruiser', 3, 272, 109, 34, 57, 82517),
(291, 'Cruiser', 4, 340, 136, 43, 71, 82517),
(292, 'Cruiser', 5, 408, 163, 51, 86, 82517),
(293, 'Cruiser', 6, 476, 190, 60, 100, 82517),
(294, 'Cruiser', 7, 544, 218, 68, 114, 82517),
(295, 'Cruiser', 8, 612, 245, 77, 129, 82517),
(296, 'Cruiser', 9, 680, 272, 85, 143, 82517),
(297, 'Cruiser', 10, 748, 299, 94, 157, 82517),
(298, 'Cruiser', 11, 816, 326, 102, 171, 82517),
(299, 'Cruiser', 12, 884, 354, 111, 186, 82517),
(300, 'Cruiser', 13, 952, 381, 119, 200, 82517),
(301, 'Cruiser', 14, 1020, 408, 128, 214, 82517),
(302, 'Cruiser', 15, 1088, 435, 136, 228, 82517),
(303, 'Cruiser', 16, 1156, 462, 145, 243, 82517),
(304, 'Cruiser', 17, 1224, 490, 153, 257, 82517),
(305, 'Cruiser', 18, 1292, 517, 162, 271, 82517),
(306, 'Cruiser', 19, 1360, 544, 170, 286, 82517),
(307, 'Cruiser', 20, 1428, 571, 179, 300, 82517),
(308, 'base', 18, 2419, 1411, 706, 302, 117818),
(309, 'coaldepot', 18, 1210, 1210, 504, 272, 117818),
(310, 'coalmine', 18, 1008, 1411, 504, 242, 117818),
(311, 'copperdepot', 18, 2016, 907, 302, 363, 117818),
(312, 'coppermine', 18, 2016, 806, 252, 423, 117818),
(313, 'oredepot', 18, 2419, 605, 454, 302, 117818),
(314, 'oremine', 18, 2822, 504, 403, 302, 117818),
(315, 'researchcenter', 18, 2016, 1008, 605, 393, 117818),
(316, 'shipyard', 18, 2822, 1210, 504, 393, 117818),
(317, 'uraniumdepot', 18, 1814, 1008, 605, 181, 117818),
(318, 'uraniummine', 18, 1613, 1008, 706, 151, 117818),
(319, 'Battlecruiser', 1, 173, 101, 50, 22, 117818),
(320, 'Battlecruiser', 2, 259, 151, 76, 32, 117818),
(321, 'Battlecruiser', 3, 346, 202, 101, 43, 117818),
(322, 'Battlecruiser', 4, 432, 252, 126, 54, 117818),
(323, 'Battlecruiser', 5, 518, 302, 151, 65, 117818),
(324, 'Battlecruiser', 6, 605, 353, 176, 76, 117818),
(325, 'Battlecruiser', 7, 691, 403, 202, 86, 117818),
(326, 'Battlecruiser', 8, 778, 454, 227, 97, 117818),
(327, 'Battlecruiser', 9, 864, 504, 252, 108, 117818),
(328, 'Battlecruiser', 10, 950, 554, 277, 119, 117818),
(329, 'Battlecruiser', 11, 1037, 605, 302, 130, 117818),
(330, 'Battlecruiser', 12, 1123, 655, 328, 140, 117818),
(331, 'Battlecruiser', 13, 1210, 706, 353, 151, 117818),
(332, 'Battlecruiser', 14, 1296, 756, 378, 162, 117818),
(333, 'Battlecruiser', 15, 1382, 806, 403, 173, 117818),
(334, 'Battlecruiser', 16, 1469, 857, 428, 184, 117818),
(335, 'Battlecruiser', 17, 1555, 907, 454, 194, 117818),
(336, 'Battlecruiser', 18, 1642, 958, 479, 205, 117818),
(337, 'Battlecruiser', 19, 1728, 1008, 504, 216, 117818),
(338, 'Battlecruiser', 20, 1814, 1058, 529, 227, 117818),
(339, 'base', 19, 2918, 1702, 851, 365, 190884),
(340, 'coaldepot', 19, 1459, 1459, 608, 328, 190884),
(341, 'coalmine', 19, 1216, 1702, 608, 292, 190884),
(342, 'copperdepot', 19, 2432, 1094, 365, 438, 190884),
(343, 'coppermine', 19, 2432, 973, 304, 511, 190884),
(344, 'oredepot', 19, 2918, 730, 547, 365, 190884),
(345, 'oremine', 19, 3405, 608, 486, 365, 190884),
(346, 'researchcenter', 19, 2432, 1216, 730, 474, 190884),
(347, 'shipyard', 19, 3405, 1459, 608, 474, 190884),
(348, 'uraniumdepot', 19, 2189, 1216, 730, 219, 190884),
(349, 'uraniummine', 19, 1946, 1216, 851, 182, 190884),
(350, 'Carrier', 1, 182, 106, 53, 23, 190884),
(351, 'Carrier', 2, 274, 160, 80, 34, 190884),
(352, 'Carrier', 3, 365, 213, 106, 46, 190884),
(353, 'Carrier', 4, 456, 266, 133, 57, 190884),
(354, 'Carrier', 5, 547, 319, 160, 68, 190884),
(355, 'Carrier', 6, 638, 372, 186, 80, 190884),
(356, 'Carrier', 7, 730, 426, 213, 91, 190884),
(357, 'Carrier', 8, 821, 479, 239, 103, 190884),
(358, 'Carrier', 9, 912, 532, 266, 114, 190884),
(359, 'Carrier', 10, 1003, 585, 293, 125, 190884),
(360, 'Carrier', 11, 1094, 638, 319, 137, 190884),
(361, 'Carrier', 12, 1186, 692, 346, 148, 190884),
(362, 'Carrier', 13, 1277, 745, 372, 160, 190884),
(363, 'Carrier', 14, 1368, 798, 399, 171, 190884),
(364, 'Carrier', 15, 1459, 851, 426, 182, 190884),
(365, 'Carrier', 16, 1550, 904, 452, 194, 190884),
(366, 'Carrier', 17, 1642, 958, 479, 205, 190884),
(367, 'Carrier', 18, 1733, 1011, 505, 217, 190884),
(368, 'Carrier', 19, 1824, 1064, 532, 228, 190884),
(369, 'Carrier', 20, 1915, 1117, 559, 239, 190884),
(370, 'base', 20, 3456, 2016, 1008, 432, 432000),
(371, 'coalbooster', 1, 192, 112, 56, 24, 432000),
(372, 'coalbooster', 10, 1920, 1120, 560, 240, 432000),
(373, 'coalbooster', 11, 2112, 1232, 616, 264, 432000),
(374, 'coalbooster', 12, 2304, 1344, 672, 288, 432000),
(375, 'coalbooster', 13, 2496, 1456, 728, 312, 432000),
(376, 'coalbooster', 14, 2688, 1568, 784, 336, 432000),
(377, 'coalbooster', 15, 2880, 1680, 840, 360, 432000),
(378, 'coalbooster', 16, 3072, 1792, 896, 384, 432000),
(379, 'coalbooster', 17, 3264, 1904, 952, 408, 432000),
(380, 'coalbooster', 18, 3456, 2016, 1008, 432, 432000),
(381, 'coalbooster', 19, 3648, 2128, 1064, 456, 432000),
(382, 'coalbooster', 2, 384, 224, 112, 48, 432000),
(383, 'coalbooster', 20, 3840, 2240, 1120, 480, 432000),
(384, 'coalbooster', 3, 576, 336, 168, 72, 432000),
(385, 'coalbooster', 4, 768, 448, 224, 96, 432000),
(386, 'coalbooster', 5, 960, 560, 280, 120, 432000),
(387, 'coalbooster', 6, 1152, 672, 336, 144, 432000),
(388, 'coalbooster', 7, 1344, 784, 392, 168, 432000),
(389, 'coalbooster', 8, 1536, 896, 448, 192, 432000),
(390, 'coalbooster', 9, 1728, 1008, 504, 216, 432000),
(391, 'coaldepot', 20, 1728, 1728, 720, 389, 432000),
(392, 'coalmine', 20, 1440, 2016, 720, 346, 432000),
(393, 'copperbooster', 1, 80, 112, 40, 19, 432000),
(394, 'copperbooster', 10, 800, 1120, 400, 192, 432000),
(395, 'copperbooster', 11, 880, 1232, 440, 211, 432000),
(396, 'copperbooster', 12, 960, 1344, 480, 230, 432000),
(397, 'copperbooster', 13, 1040, 1456, 520, 250, 432000),
(398, 'copperbooster', 14, 1120, 1568, 560, 269, 432000),
(399, 'copperbooster', 15, 1200, 1680, 600, 288, 432000),
(400, 'copperbooster', 16, 1280, 1792, 640, 307, 432000),
(401, 'copperbooster', 17, 1360, 1904, 680, 326, 432000),
(402, 'copperbooster', 18, 1440, 2016, 720, 346, 432000),
(403, 'copperbooster', 19, 1520, 2128, 760, 365, 432000),
(404, 'copperbooster', 2, 160, 224, 80, 38, 432000),
(405, 'copperbooster', 20, 1600, 2240, 800, 384, 432000),
(406, 'copperbooster', 3, 240, 336, 120, 58, 432000),
(407, 'copperbooster', 4, 320, 448, 160, 77, 432000),
(408, 'copperbooster', 5, 400, 560, 200, 96, 432000),
(409, 'copperbooster', 6, 480, 672, 240, 115, 432000),
(410, 'copperbooster', 7, 560, 784, 280, 134, 432000),
(411, 'copperbooster', 8, 640, 896, 320, 154, 432000),
(412, 'copperbooster', 9, 720, 1008, 360, 173, 432000),
(413, 'copperdepot', 20, 2880, 1296, 432, 518, 432000),
(414, 'coppermine', 20, 2880, 1152, 360, 605, 432000),
(415, 'orebooster', 1, 240, 120, 60, 29, 432000),
(416, 'orebooster', 10, 2400, 1200, 600, 288, 432000),
(417, 'orebooster', 11, 2640, 1320, 660, 317, 432000),
(418, 'orebooster', 12, 2880, 1440, 720, 346, 432000),
(419, 'orebooster', 13, 3120, 1560, 780, 374, 432000),
(420, 'orebooster', 14, 3360, 1680, 840, 403, 432000),
(421, 'orebooster', 15, 3600, 1800, 900, 432, 432000),
(422, 'orebooster', 16, 3840, 1920, 960, 461, 432000),
(423, 'orebooster', 17, 4080, 2040, 1020, 490, 432000),
(424, 'orebooster', 18, 4320, 2160, 1080, 518, 432000),
(425, 'orebooster', 19, 4560, 2280, 1140, 547, 432000),
(426, 'orebooster', 2, 480, 240, 120, 58, 432000),
(427, 'orebooster', 20, 4800, 2400, 1200, 576, 432000),
(428, 'orebooster', 3, 720, 360, 180, 86, 432000),
(429, 'orebooster', 4, 960, 480, 240, 115, 432000),
(430, 'orebooster', 5, 1200, 600, 300, 144, 432000),
(431, 'orebooster', 6, 1440, 720, 360, 173, 432000),
(432, 'orebooster', 7, 1680, 840, 420, 202, 432000),
(433, 'orebooster', 8, 1920, 960, 480, 230, 432000),
(434, 'orebooster', 9, 2160, 1080, 540, 259, 432000),
(435, 'oredepot', 20, 3456, 864, 648, 432, 432000),
(436, 'oremine', 20, 4032, 720, 576, 432, 432000),
(437, 'researchcenter', 20, 2880, 1440, 864, 562, 432000),
(438, 'shipyard', 20, 4032, 1728, 720, 562, 432000),
(439, 'uraniumbooster', 1, 224, 96, 40, 31, 432000),
(440, 'uraniumbooster', 10, 2240, 960, 400, 312, 432000),
(441, 'uraniumbooster', 11, 2464, 1056, 440, 343, 432000),
(442, 'uraniumbooster', 12, 2688, 1152, 480, 374, 432000),
(443, 'uraniumbooster', 13, 2912, 1248, 520, 406, 432000),
(444, 'uraniumbooster', 14, 3136, 1344, 560, 437, 432000),
(445, 'uraniumbooster', 15, 3360, 1440, 600, 468, 432000),
(446, 'uraniumbooster', 16, 3584, 1536, 640, 499, 432000),
(447, 'uraniumbooster', 17, 3808, 1632, 680, 530, 432000),
(448, 'uraniumbooster', 18, 4032, 1728, 720, 562, 432000),
(449, 'uraniumbooster', 19, 4256, 1824, 760, 593, 432000),
(450, 'uraniumbooster', 2, 448, 192, 80, 62, 432000),
(451, 'uraniumbooster', 20, 4480, 1920, 800, 624, 432000),
(452, 'uraniumbooster', 3, 672, 288, 120, 94, 432000),
(453, 'uraniumbooster', 4, 896, 384, 160, 125, 432000),
(454, 'uraniumbooster', 5, 1120, 480, 200, 156, 432000),
(455, 'uraniumbooster', 6, 1344, 576, 240, 187, 432000),
(456, 'uraniumbooster', 7, 1568, 672, 280, 218, 432000),
(457, 'uraniumbooster', 8, 1792, 768, 320, 250, 432000),
(458, 'uraniumbooster', 9, 2016, 864, 360, 281, 432000),
(459, 'uraniumdepot', 20, 2592, 1440, 864, 259, 432000),
(460, 'uraniummine', 20, 2304, 1440, 1008, 216, 432000),
(461, 'Dreadnought', 1, 160, 64, 20, 34, 432000),
(462, 'Dreadnought', 2, 240, 96, 30, 50, 432000),
(463, 'Dreadnought', 3, 320, 128, 40, 67, 432000),
(464, 'Dreadnought', 4, 400, 160, 50, 84, 432000),
(465, 'Dreadnought', 5, 480, 192, 60, 101, 432000),
(466, 'Dreadnought', 6, 560, 224, 70, 118, 432000),
(467, 'Dreadnought', 7, 640, 256, 80, 134, 432000),
(468, 'Dreadnought', 8, 720, 288, 90, 151, 432000),
(469, 'Dreadnought', 9, 800, 320, 100, 168, 432000),
(470, 'Dreadnought', 10, 880, 352, 110, 185, 432000),
(471, 'Dreadnought', 11, 960, 384, 120, 202, 432000),
(472, 'Dreadnought', 12, 1040, 416, 130, 218, 432000),
(473, 'Dreadnought', 13, 1120, 448, 140, 235, 432000),
(474, 'Dreadnought', 14, 1200, 480, 150, 252, 432000),
(475, 'Dreadnought', 15, 1280, 512, 160, 269, 432000),
(476, 'Dreadnought', 16, 1360, 544, 170, 286, 432000),
(477, 'Dreadnought', 17, 1440, 576, 180, 302, 432000),
(478, 'Dreadnought', 18, 1520, 608, 190, 319, 432000),
(479, 'Dreadnought', 19, 1600, 640, 200, 336, 432000),
(480, 'Dreadnought', 20, 1680, 672, 210, 353, 432000),
(481, 'missioncontrol', 1, 2400, 1200, 600, 288, 432000),
(482, 'missioncontrol', 2, 2520, 1260, 630, 302, 432000),
(483, 'missioncontrol', 3, 2640, 1320, 660, 317, 432000),
(484, 'missioncontrol', 4, 2760, 1380, 690, 331, 432000),
(485, 'missioncontrol', 5, 2880, 1440, 720, 346, 432000),
(486, 'missioncontrol', 6, 3000, 1500, 750, 360, 432000),
(487, 'missioncontrol', 7, 3120, 1560, 780, 374, 432000),
(488, 'missioncontrol', 8, 3240, 1620, 810, 389, 432000),
(489, 'missioncontrol', 9, 3360, 1680, 840, 403, 432000),
(490, 'missioncontrol', 10, 3480, 1740, 870, 418, 432000),
(491, 'missioncontrol', 11, 3600, 1800, 900, 432, 432000),
(492, 'missioncontrol', 12, 3720, 1860, 930, 446, 432000),
(493, 'missioncontrol', 13, 3840, 1920, 960, 461, 432000),
(494, 'missioncontrol', 14, 3960, 1980, 990, 475, 432000),
(495, 'missioncontrol', 15, 4080, 2040, 1020, 490, 432000),
(496, 'missioncontrol', 16, 4200, 2100, 1050, 504, 432000),
(497, 'missioncontrol', 17, 4320, 2160, 1080, 518, 432000),
(498, 'missioncontrol', 18, 4440, 2220, 1110, 533, 432000),
(499, 'missioncontrol', 19, 4560, 2280, 1140, 547, 432000),
(500, 'missioncontrol', 20, 4680, 2340, 1170, 562, 432000),
(501, 'bunker', 1, 4, 2, 1, 0, 945),
(502, 'bunker', 2, 8, 4, 2, 1, 1991),
(503, 'bunker', 3, 12, 6, 2, 1, 3153),
(504, 'bunker', 4, 15, 8, 3, 2, 4454),
(505, 'bunker', 5, 24, 12, 5, 2, 5918),
(506, 'bunker', 6, 35, 17, 7, 4, 7579),
(507, 'bunker', 7, 47, 24, 10, 5, 9480),
(508, 'bunker', 8, 61, 31, 13, 6, 11676),
(509, 'bunker', 9, 78, 39, 16, 8, 14242),
(510, 'bunker', 10, 96, 48, 20, 10, 17280),
(511, 'bunker', 11, 176, 106, 44, 26, 20934),
(512, 'bunker', 12, 384, 230, 96, 58, 25412),
(513, 'bunker', 13, 624, 374, 156, 94, 31028),
(514, 'bunker', 14, 896, 538, 224, 134, 38278),
(515, 'bunker', 15, 1200, 720, 300, 180, 48000),
(516, 'bunker', 16, 1536, 922, 384, 230, 61714),
(517, 'bunker', 17, 1904, 1142, 476, 286, 82517),
(518, 'bunker', 18, 2304, 1382, 576, 346, 117818),
(519, 'bunker', 19, 2736, 1642, 684, 410, 190884),
(520, 'bunker', 20, 3200, 1920, 800, 480, 432000),
(521, 'shieldgenerator', 1, 4, 2, 1, 0, 945),
(522, 'shieldgenerator', 2, 8, 3, 2, 1, 1991),
(523, 'shieldgenerator', 3, 12, 5, 2, 1, 3153),
(524, 'shieldgenerator', 4, 15, 6, 3, 2, 4454),
(525, 'shieldgenerator', 5, 24, 10, 5, 3, 5918),
(526, 'shieldgenerator', 6, 35, 14, 7, 4, 7579),
(527, 'shieldgenerator', 7, 47, 20, 10, 6, 9480),
(528, 'shieldgenerator', 8, 61, 26, 13, 8, 11676),
(529, 'shieldgenerator', 9, 78, 32, 16, 10, 14242),
(530, 'shieldgenerator', 10, 96, 40, 20, 12, 17280),
(531, 'shieldgenerator', 11, 176, 88, 44, 32, 20934),
(532, 'shieldgenerator', 12, 384, 192, 96, 69, 25412),
(533, 'shieldgenerator', 13, 624, 312, 156, 112, 31028),
(534, 'shieldgenerator', 14, 896, 448, 224, 161, 38278),
(535, 'shieldgenerator', 15, 1200, 600, 300, 216, 48000),
(536, 'shieldgenerator', 16, 1536, 768, 384, 276, 61714),
(537, 'shieldgenerator', 17, 1904, 952, 476, 343, 82517),
(538, 'shieldgenerator', 18, 2304, 1152, 576, 415, 117818),
(539, 'shieldgenerator', 19, 2736, 1368, 684, 492, 190884),
(540, 'shieldgenerator', 20, 3200, 1600, 800, 576, 432000),
(541, 'enlargebunker', 1, 8, 4, 2, 1, 945),
(542, 'enlargebunker', 2, 32, 16, 8, 5, 1991),
(543, 'enlargebunker', 3, 72, 36, 18, 11, 3153),
(544, 'enlargebunker', 4, 128, 64, 32, 19, 4454),
(545, 'enlargebunker', 5, 200, 100, 50, 30, 5918),
(546, 'enlargebunker', 6, 288, 144, 72, 43, 7579),
(547, 'enlargebunker', 7, 392, 196, 98, 59, 9480),
(548, 'enlargebunker', 8, 512, 256, 128, 77, 11676),
(549, 'enlargebunker', 9, 648, 324, 162, 97, 14242),
(550, 'enlargebunker', 10, 800, 400, 200, 120, 17280),
(551, 'enlargebunker', 11, 968, 484, 242, 145, 20934),
(552, 'enlargebunker', 12, 1152, 576, 288, 173, 25412),
(553, 'enlargebunker', 13, 1352, 676, 338, 203, 31028),
(554, 'enlargebunker', 14, 1568, 784, 392, 235, 38278),
(555, 'enlargebunker', 15, 1800, 900, 450, 270, 48000),
(556, 'enlargebunker', 16, 2048, 1024, 512, 307, 61714),
(557, 'enlargebunker', 17, 2312, 1156, 578, 347, 82517),
(558, 'enlargebunker', 18, 2592, 1296, 648, 389, 117818),
(559, 'enlargebunker', 19, 2888, 1444, 722, 433, 190884),
(560, 'enlargebunker', 20, 3200, 1600, 800, 480, 432000);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `space`
--

CREATE TABLE `space` (
  `id` int(11) NOT NULL,
  `user` varchar(256) NOT NULL,
  `date` datetime NOT NULL,
  `c_hor` int(11) NOT NULL,
  `c_ver` int(11) NOT NULL,
  `trx_id` varchar(50) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `planet_id` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `status`
--

CREATE TABLE `status` (
  `id` int(11) NOT NULL,
  `start_block_num` int(11) DEFAULT NULL,
  `latest_block_num` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `trx` varchar(50) NOT NULL,
  `block_num` int(11) DEFAULT NULL,
  `user` varchar(256) NOT NULL,
  `tr_type` varchar(256) NOT NULL,
  `tr_var1` varchar(256) NOT NULL,
  `tr_var2` varchar(256) DEFAULT NULL,
  `tr_var3` varchar(256) DEFAULT NULL,
  `tr_var4` varchar(256) DEFAULT NULL,
  `tr_var5` varchar(256) DEFAULT NULL,
  `tr_var6` varchar(256) DEFAULT NULL,
  `tr_var7` varchar(256) DEFAULT NULL,
  `tr_var8` varchar(256) DEFAULT NULL,
  `tr_status` int(11) NOT NULL,
  `date` datetime(6) DEFAULT NULL,
  `trigger_block_num` int(11) DEFAULT NULL,
  `virtualop` tinyint(1) NOT NULL DEFAULT '0',
  `error` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `transfers`
--

CREATE TABLE `transfers` (
  `id` int(11) NOT NULL,
  `trx` varchar(50) NOT NULL,
  `block_num` int(11) DEFAULT NULL,
  `user` varchar(256) NOT NULL,
  `amount` varchar(256) NOT NULL,
  `memo` varchar(256) NOT NULL,
  `tr_status` int(11) NOT NULL,
  `date` datetime(6) DEFAULT NULL,
  `error` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `translate`
--

CREATE TABLE `translate` (
  `id` int(11) NOT NULL,
  `variable` varchar(255) NOT NULL,
  `translation` text NOT NULL,
  `lang` varchar(255) NOT NULL DEFAULT 'eng'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `upgradecosts`
--

CREATE TABLE `upgradecosts` (
  `id` int(11) NOT NULL,
  `name` varchar(256) NOT NULL,
  `level` int(11) NOT NULL,
  `coal` int(11) NOT NULL,
  `ore` int(11) NOT NULL,
  `copper` int(11) NOT NULL,
  `uranium` int(11) NOT NULL,
  `upgrade_time` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Daten für Tabelle `upgradecosts`
--

INSERT INTO `upgradecosts` (`id`, `name`, `level`, `coal`, `ore`, `copper`, `uranium`, `upgrade_time`) VALUES
(1, 'base', 1, 5, 3, 1, 0, 945),
(2, 'coaldepot', 1, 3, 2, 1, 0, 945),
(3, 'coalmine', 1, 2, 3, 1, 0, 945),
(4, 'copperdepot', 1, 4, 2, 1, 1, 945),
(5, 'coppermine', 1, 4, 1, 0, 1, 945),
(6, 'oredepot', 1, 5, 1, 1, 0, 945),
(7, 'oremine', 1, 6, 1, 1, 0, 945),
(8, 'researchcenter', 1, 4, 2, 1, 1, 945),
(9, 'shipyard', 1, 6, 2, 1, 1, 945),
(10, 'uraniumdepot', 1, 4, 2, 1, 0, 945),
(11, 'uraniummine', 1, 3, 2, 1, 0, 945),
(12, 'base', 2, 11, 5, 3, 1, 1991),
(13, 'coaldepot', 2, 5, 4, 2, 1, 1991),
(14, 'coalmine', 2, 4, 5, 2, 1, 1991),
(15, 'copperdepot', 2, 9, 3, 1, 1, 1991),
(16, 'coppermine', 2, 9, 3, 1, 1, 1991),
(17, 'oredepot', 2, 11, 2, 2, 1, 1991),
(18, 'oremine', 2, 12, 2, 1, 1, 1991),
(19, 'researchcenter', 2, 9, 4, 2, 1, 1991),
(20, 'shipyard', 2, 12, 4, 2, 1, 1991),
(21, 'uraniumdepot', 2, 8, 4, 2, 1, 1991),
(22, 'uraniummine', 2, 7, 4, 3, 0, 1991),
(23, 'base', 3, 16, 8, 4, 1, 3153),
(24, 'coaldepot', 3, 8, 7, 3, 1, 3153),
(25, 'coalmine', 3, 7, 8, 3, 1, 3153),
(26, 'copperdepot', 3, 14, 5, 2, 2, 3153),
(27, 'coppermine', 3, 14, 5, 1, 2, 3153),
(28, 'oredepot', 3, 16, 3, 3, 1, 3153),
(29, 'oremine', 3, 19, 3, 2, 1, 3153),
(30, 'researchcenter', 3, 14, 6, 3, 2, 3153),
(31, 'shipyard', 3, 19, 7, 3, 2, 3153),
(32, 'uraniumdepot', 3, 12, 6, 3, 1, 3153),
(33, 'uraniummine', 3, 11, 6, 4, 1, 3153),
(34, 'base', 4, 22, 11, 5, 2, 4454),
(35, 'coaldepot', 4, 11, 9, 4, 2, 4454),
(36, 'coalmine', 4, 9, 11, 4, 2, 4454),
(37, 'copperdepot', 4, 18, 7, 2, 2, 4454),
(38, 'coppermine', 4, 18, 6, 2, 3, 4454),
(39, 'oredepot', 4, 22, 5, 3, 2, 4454),
(40, 'oremine', 4, 26, 4, 3, 2, 4454),
(41, 'researchcenter', 4, 18, 8, 5, 2, 4454),
(42, 'shipyard', 4, 26, 9, 4, 2, 4454),
(43, 'uraniumdepot', 4, 17, 8, 5, 1, 4454),
(44, 'uraniummine', 4, 15, 8, 5, 1, 4454),
(45, 'base', 5, 28, 14, 7, 2, 5918),
(46, 'coaldepot', 5, 14, 12, 5, 2, 5918),
(47, 'coalmine', 5, 12, 14, 5, 2, 5918),
(48, 'copperdepot', 5, 24, 9, 3, 3, 5918),
(49, 'coppermine', 5, 24, 8, 2, 3, 5918),
(50, 'oredepot', 5, 28, 6, 4, 2, 5918),
(51, 'oremine', 5, 33, 5, 4, 2, 5918),
(52, 'researchcenter', 5, 24, 10, 6, 3, 5918),
(53, 'shipyard', 5, 33, 12, 5, 3, 5918),
(54, 'uraniumdepot', 5, 21, 10, 6, 1, 5918),
(55, 'uraniummine', 5, 19, 10, 7, 1, 5918),
(56, 'base', 6, 35, 17, 8, 3, 7579),
(57, 'coaldepot', 6, 17, 14, 6, 3, 7579),
(58, 'coalmine', 6, 14, 17, 6, 2, 7579),
(59, 'copperdepot', 6, 29, 11, 4, 4, 7579),
(60, 'coppermine', 6, 29, 10, 3, 4, 7579),
(61, 'oredepot', 6, 35, 7, 5, 3, 7579),
(62, 'oremine', 6, 40, 6, 5, 3, 7579),
(63, 'researchcenter', 6, 29, 12, 7, 4, 7579),
(64, 'shipyard', 6, 40, 14, 6, 4, 7579),
(65, 'uraniumdepot', 6, 26, 12, 7, 2, 7579),
(66, 'uraniummine', 6, 23, 12, 8, 2, 7579),
(67, 'base', 7, 42, 20, 10, 4, 9480),
(68, 'coaldepot', 7, 21, 17, 7, 3, 9480),
(69, 'coalmine', 7, 17, 20, 7, 3, 9480),
(70, 'copperdepot', 7, 35, 13, 4, 4, 9480),
(71, 'coppermine', 7, 35, 12, 4, 5, 9480),
(72, 'oredepot', 7, 42, 9, 7, 4, 9480),
(73, 'oremine', 7, 49, 7, 6, 4, 9480),
(74, 'researchcenter', 7, 35, 15, 9, 5, 9480),
(75, 'shipyard', 7, 49, 17, 7, 5, 9480),
(76, 'uraniumdepot', 7, 31, 15, 9, 2, 9480),
(77, 'uraniummine', 7, 28, 15, 10, 2, 9480),
(78, 'base', 8, 49, 24, 12, 4, 11676),
(79, 'coaldepot', 8, 24, 20, 8, 4, 11676),
(80, 'coalmine', 8, 20, 24, 8, 3, 11676),
(81, 'copperdepot', 8, 41, 15, 5, 5, 11676),
(82, 'coppermine', 8, 41, 14, 4, 6, 11676),
(83, 'oredepot', 8, 49, 10, 8, 4, 11676),
(84, 'oremine', 8, 57, 8, 7, 4, 11676),
(85, 'researchcenter', 8, 41, 17, 10, 6, 11676),
(86, 'shipyard', 8, 57, 20, 8, 6, 11676),
(87, 'uraniumdepot', 8, 37, 17, 10, 3, 11676),
(88, 'uraniummine', 8, 33, 17, 12, 2, 11676),
(89, 'base', 9, 56, 27, 14, 5, 14242),
(90, 'coaldepot', 9, 28, 23, 10, 4, 14242),
(91, 'coalmine', 9, 23, 27, 10, 4, 14242),
(92, 'copperdepot', 9, 47, 17, 6, 6, 14242),
(93, 'coppermine', 9, 47, 16, 5, 7, 14242),
(94, 'oredepot', 9, 56, 12, 9, 5, 14242),
(95, 'oremine', 9, 65, 10, 8, 5, 14242),
(96, 'researchcenter', 9, 47, 19, 12, 6, 14242),
(97, 'shipyard', 9, 65, 23, 10, 6, 14242),
(98, 'uraniumdepot', 9, 42, 19, 12, 3, 14242),
(99, 'uraniummine', 9, 37, 19, 14, 2, 14242),
(100, 'base', 10, 63, 31, 15, 6, 17280),
(101, 'coaldepot', 10, 32, 26, 11, 5, 17280),
(102, 'coalmine', 10, 26, 31, 11, 4, 17280),
(103, 'copperdepot', 10, 53, 20, 7, 7, 17280),
(104, 'coppermine', 10, 53, 18, 6, 8, 17280),
(105, 'oredepot', 10, 63, 13, 10, 6, 17280),
(106, 'oremine', 10, 74, 11, 9, 6, 17280),
(107, 'researchcenter', 10, 53, 22, 13, 7, 17280),
(108, 'shipyard', 10, 74, 26, 11, 7, 17280),
(109, 'uraniumdepot', 10, 48, 22, 13, 3, 17280),
(110, 'uraniummine', 10, 42, 22, 15, 3, 17280),
(111, 'base', 11, 106, 74, 31, 11, 20934),
(112, 'coaldepot', 11, 53, 63, 22, 10, 20934),
(113, 'coalmine', 11, 44, 74, 22, 9, 20934),
(114, 'copperdepot', 11, 88, 48, 13, 13, 20934),
(115, 'coppermine', 11, 88, 42, 11, 15, 20934),
(116, 'oredepot', 11, 106, 32, 20, 11, 20934),
(117, 'oremine', 11, 123, 26, 18, 11, 20934),
(118, 'researchcenter', 11, 88, 53, 26, 14, 20934),
(119, 'shipyard', 11, 123, 63, 22, 14, 20934),
(120, 'uraniumdepot', 11, 79, 53, 26, 7, 20934),
(121, 'uraniummine', 11, 70, 53, 31, 6, 20934),
(122, 'base', 12, 230, 161, 67, 24, 25412),
(123, 'coaldepot', 12, 115, 138, 48, 22, 25412),
(124, 'coalmine', 12, 96, 161, 48, 19, 25412),
(125, 'copperdepot', 12, 192, 104, 29, 29, 25412),
(126, 'coppermine', 12, 192, 92, 24, 34, 25412),
(127, 'oredepot', 12, 230, 69, 43, 24, 25412),
(128, 'oremine', 12, 269, 58, 38, 24, 25412),
(129, 'researchcenter', 12, 192, 115, 58, 31, 25412),
(130, 'shipyard', 12, 269, 138, 48, 31, 25412),
(131, 'uraniumdepot', 12, 173, 115, 58, 14, 25412),
(132, 'uraniummine', 12, 154, 115, 67, 12, 25412),
(133, 'base', 13, 499, 349, 146, 52, 31028),
(134, 'coaldepot', 13, 250, 300, 104, 47, 31028),
(135, 'coalmine', 13, 208, 349, 104, 42, 31028),
(136, 'copperdepot', 13, 416, 225, 62, 62, 31028),
(137, 'coppermine', 13, 416, 200, 52, 73, 31028),
(138, 'oredepot', 13, 499, 150, 94, 52, 31028),
(139, 'oremine', 13, 582, 125, 83, 52, 31028),
(140, 'researchcenter', 13, 416, 250, 125, 68, 31028),
(141, 'shipyard', 13, 582, 300, 104, 68, 31028),
(142, 'uraniumdepot', 13, 374, 250, 125, 31, 31028),
(143, 'uraniummine', 13, 333, 250, 146, 26, 31028),
(144, 'base', 14, 806, 470, 282, 84, 38278),
(145, 'coaldepot', 14, 403, 403, 202, 76, 38278),
(146, 'coalmine', 14, 336, 470, 202, 67, 38278),
(147, 'copperdepot', 14, 672, 302, 121, 101, 38278),
(148, 'coppermine', 14, 672, 269, 101, 118, 38278),
(149, 'oredepot', 14, 806, 202, 181, 84, 38278),
(150, 'oremine', 14, 941, 168, 161, 84, 38278),
(151, 'researchcenter', 14, 672, 336, 242, 109, 38278),
(152, 'shipyard', 14, 941, 403, 202, 109, 38278),
(153, 'uraniumdepot', 14, 605, 336, 242, 50, 38278),
(154, 'uraniummine', 14, 538, 336, 282, 42, 38278),
(155, 'base', 15, 1152, 672, 403, 120, 48000),
(156, 'coaldepot', 15, 576, 576, 288, 108, 48000),
(157, 'coalmine', 15, 480, 672, 288, 96, 48000),
(158, 'copperdepot', 15, 960, 432, 173, 144, 48000),
(159, 'coppermine', 15, 960, 384, 144, 168, 48000),
(160, 'oredepot', 15, 1152, 288, 259, 120, 48000),
(161, 'oremine', 15, 1344, 240, 230, 120, 48000),
(162, 'researchcenter', 15, 960, 480, 346, 156, 48000),
(163, 'shipyard', 15, 1344, 576, 288, 156, 48000),
(164, 'uraniumdepot', 15, 864, 480, 346, 72, 48000),
(165, 'uraniummine', 15, 768, 480, 403, 60, 48000),
(166, 'base', 16, 1536, 896, 538, 160, 61714),
(167, 'coaldepot', 16, 768, 768, 384, 144, 61714),
(168, 'coalmine', 16, 640, 896, 384, 128, 61714),
(169, 'copperdepot', 16, 1280, 576, 230, 192, 61714),
(170, 'coppermine', 16, 1280, 512, 192, 224, 61714),
(171, 'oredepot', 16, 1536, 384, 346, 160, 61714),
(172, 'oremine', 16, 1792, 320, 307, 160, 61714),
(173, 'researchcenter', 16, 1280, 640, 461, 208, 61714),
(174, 'shipyard', 16, 1792, 768, 384, 208, 61714),
(175, 'uraniumdepot', 16, 1152, 640, 461, 96, 61714),
(176, 'uraniummine', 16, 1024, 640, 538, 80, 61714),
(177, 'base', 17, 1958, 1142, 571, 245, 82517),
(178, 'coaldepot', 17, 979, 979, 408, 220, 82517),
(179, 'coalmine', 17, 816, 1142, 408, 196, 82517),
(180, 'copperdepot', 17, 1632, 734, 245, 294, 82517),
(181, 'coppermine', 17, 1632, 653, 204, 343, 82517),
(182, 'oredepot', 17, 1958, 490, 367, 245, 82517),
(183, 'oremine', 17, 2285, 408, 326, 245, 82517),
(184, 'researchcenter', 17, 1632, 816, 490, 318, 82517),
(185, 'shipyard', 17, 2285, 979, 408, 318, 82517),
(186, 'uraniumdepot', 17, 1469, 816, 490, 147, 82517),
(187, 'uraniummine', 17, 1306, 816, 571, 122, 82517),
(188, 'base', 18, 2419, 1411, 706, 302, 117818),
(189, 'coaldepot', 18, 1210, 1210, 504, 272, 117818),
(190, 'coalmine', 18, 1008, 1411, 504, 242, 117818),
(191, 'copperdepot', 18, 2016, 907, 302, 363, 117818),
(192, 'coppermine', 18, 2016, 806, 252, 423, 117818),
(193, 'oredepot', 18, 2419, 605, 454, 302, 117818),
(194, 'oremine', 18, 2822, 504, 403, 302, 117818),
(195, 'researchcenter', 18, 2016, 1008, 605, 393, 117818),
(196, 'shipyard', 18, 2822, 1210, 504, 393, 117818),
(197, 'uraniumdepot', 18, 1814, 1008, 605, 181, 117818),
(198, 'uraniummine', 18, 1613, 1008, 706, 151, 117818),
(199, 'base', 19, 2918, 1702, 851, 365, 190884),
(200, 'coaldepot', 19, 1459, 1459, 608, 328, 190884),
(201, 'coalmine', 19, 1216, 1702, 608, 292, 190884),
(202, 'copperdepot', 19, 2432, 1094, 365, 438, 190884),
(203, 'coppermine', 19, 2432, 973, 304, 511, 190884),
(204, 'oredepot', 19, 2918, 730, 547, 365, 190884),
(205, 'oremine', 19, 3405, 608, 486, 365, 190884),
(206, 'researchcenter', 19, 2432, 1216, 730, 474, 190884),
(207, 'shipyard', 19, 3405, 1459, 608, 474, 190884),
(208, 'uraniumdepot', 19, 2189, 1216, 730, 219, 190884),
(209, 'uraniummine', 19, 1946, 1216, 851, 182, 190884),
(210, 'base', 20, 3456, 2016, 1008, 432, 432000),
(211, 'coaldepot', 20, 1728, 1728, 720, 389, 432000),
(212, 'coalmine', 20, 1440, 2016, 720, 346, 432000),
(213, 'copperdepot', 20, 2880, 1296, 432, 518, 432000),
(214, 'coppermine', 20, 2880, 1152, 360, 605, 432000),
(215, 'oredepot', 20, 3456, 864, 648, 432, 432000),
(216, 'oremine', 20, 4032, 720, 576, 432, 432000),
(217, 'researchcenter', 20, 2880, 1440, 864, 562, 432000),
(218, 'shipyard', 20, 4032, 1728, 720, 562, 432000),
(219, 'uraniumdepot', 20, 2592, 1440, 864, 259, 432000),
(220, 'uraniummine', 20, 2304, 1440, 1008, 216, 432000),
(221, 'transportship', 1, 538, 276, 96, 62, 25412),
(222, 'explorership', 1, 520, 250, 65, 91, 31028),
(223, 'corvette', 1, 1736, 2430, 1042, 347, 38278),
(224, 'frigate', 1, 3720, 1488, 558, 651, 48000),
(225, 'destroyer', 1, 3968, 1587, 595, 694, 61714),
(226, 'cruiser', 1, 4216, 1686, 527, 885, 82517),
(227, 'battlecruiser', 1, 5357, 3125, 1562, 670, 117818),
(228, 'carrier', 1, 5654, 3298, 1649, 707, 190884),
(229, 'dreadnought', 1, 4960, 1984, 620, 1042, 432000),
(230, 'shieldgenerator', 1, 4, 2, 1, 0, 945),
(231, 'shieldgenerator', 2, 8, 3, 2, 1, 1991),
(232, 'shieldgenerator', 3, 12, 5, 2, 1, 3153),
(233, 'shieldgenerator', 4, 15, 6, 3, 2, 4454),
(234, 'shieldgenerator', 5, 24, 10, 5, 3, 5918),
(235, 'shieldgenerator', 6, 35, 14, 7, 4, 7579),
(236, 'shieldgenerator', 7, 47, 20, 10, 6, 9480),
(237, 'shieldgenerator', 8, 61, 26, 13, 8, 11676),
(238, 'shieldgenerator', 9, 78, 32, 16, 10, 14242),
(239, 'shieldgenerator', 10, 96, 40, 20, 12, 17280),
(240, 'shieldgenerator', 11, 176, 88, 44, 32, 20934),
(241, 'shieldgenerator', 12, 384, 192, 96, 69, 25412),
(242, 'shieldgenerator', 13, 624, 312, 156, 112, 31028),
(243, 'shieldgenerator', 14, 896, 448, 224, 161, 38278),
(244, 'shieldgenerator', 15, 1200, 600, 300, 216, 48000),
(245, 'shieldgenerator', 16, 1536, 768, 384, 276, 61714),
(246, 'shieldgenerator', 17, 1904, 952, 476, 343, 82517),
(247, 'shieldgenerator', 18, 2304, 1152, 576, 415, 117818),
(248, 'shieldgenerator', 19, 2736, 1368, 684, 492, 190884),
(249, 'shieldgenerator', 20, 3200, 1600, 800, 576, 432000),
(250, 'bunker', 1, 4, 2, 1, 0, 945),
(251, 'bunker', 2, 8, 4, 2, 1, 1991),
(252, 'bunker', 3, 12, 6, 2, 1, 3153),
(253, 'bunker', 4, 15, 8, 3, 2, 4454),
(254, 'bunker', 5, 24, 12, 5, 2, 5918),
(255, 'bunker', 6, 35, 17, 7, 4, 7579),
(256, 'bunker', 7, 47, 24, 10, 5, 9480),
(257, 'bunker', 8, 61, 31, 13, 6, 11676),
(258, 'bunker', 9, 78, 39, 16, 8, 14242),
(259, 'bunker', 10, 96, 48, 20, 10, 17280),
(260, 'bunker', 11, 176, 106, 44, 26, 20934),
(261, 'bunker', 12, 384, 230, 96, 58, 25412),
(262, 'bunker', 13, 624, 374, 156, 94, 31028),
(263, 'bunker', 14, 896, 538, 224, 134, 38278),
(264, 'bunker', 15, 1200, 720, 300, 180, 48000),
(265, 'bunker', 16, 1536, 922, 384, 230, 61714),
(266, 'bunker', 17, 1904, 1142, 476, 286, 82517),
(267, 'bunker', 18, 2304, 1382, 576, 346, 117818),
(268, 'bunker', 19, 2736, 1642, 684, 410, 190884),
(269, 'bunker', 20, 3200, 1920, 800, 480, 432000);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `trx_id` varchar(50) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `sp_h` int(5) DEFAULT NULL,
  `sp_v` int(5) DEFAULT NULL,
  `r_oremine` int(11) DEFAULT NULL,
  `r_coalmine` int(11) DEFAULT NULL,
  `r_coppermine` int(11) DEFAULT NULL,
  `r_uraniummine` int(11) DEFAULT NULL,
  `r_oredepot` int(11) DEFAULT NULL,
  `r_coaldepot` int(11) DEFAULT NULL,
  `r_copperdepot` int(11) DEFAULT NULL,
  `r_uraniumdepot` int(11) DEFAULT NULL,
  `r_base` int(11) DEFAULT NULL,
  `r_researchcenter` int(11) DEFAULT NULL,
  `r_shipyard` int(11) DEFAULT NULL,
  `r_bunker` int(11) DEFAULT NULL,
  `r_shieldgenerator` int(11) DEFAULT NULL,
  `r_orebooster` int(11) DEFAULT NULL,
  `r_coalbooster` int(11) DEFAULT NULL,
  `r_copperbooster` int(11) DEFAULT NULL,
  `r_uraniumbooster` int(11) DEFAULT NULL,
  `r_enlargebunker` int(11) DEFAULT NULL,
  `r_missioncontrol` int(11) DEFAULT NULL,
  `r_Transporter` int(11) DEFAULT NULL,
  `r_Explorer` int(11) DEFAULT NULL,
  `r_Corvette` int(11) DEFAULT NULL,
  `r_Frigate` int(11) DEFAULT NULL,
  `r_Destroyer` int(11) DEFAULT NULL,
  `r_Cruiser` int(11) DEFAULT NULL,
  `r_Battlecruiser` int(11) DEFAULT NULL,
  `r_Carrier` int(11) DEFAULT NULL,
  `r_Dreadnought` int(11) DEFAULT NULL,
  `r_oremine_busy` datetime DEFAULT NULL,
  `r_coalmine_busy` datetime DEFAULT NULL,
  `r_coppermine_busy` datetime DEFAULT NULL,
  `r_uraniummine_busy` datetime DEFAULT NULL,
  `r_oredepot_busy` datetime DEFAULT NULL,
  `r_coaldepot_busy` datetime DEFAULT NULL,
  `r_copperdepot_busy` datetime DEFAULT NULL,
  `r_uraniumdepot_busy` datetime DEFAULT NULL,
  `r_base_busy` datetime DEFAULT NULL,
  `r_researchcenter_busy` datetime DEFAULT NULL,
  `r_shipyard_busy` datetime DEFAULT NULL,
  `r_bunker_busy` datetime DEFAULT NULL,
  `r_shieldgenerator_busy` datetime DEFAULT NULL,
  `r_orebooster_busy` datetime DEFAULT NULL,
  `r_coalbooster_busy` datetime DEFAULT NULL,
  `r_copperbooster_busy` datetime DEFAULT NULL,
  `r_uraniumbooster_busy` datetime DEFAULT NULL,
  `r_enlargebunker_busy` datetime DEFAULT NULL,
  `r_missioncontrol_busy` datetime DEFAULT NULL,
  `r_Transporter_busy` datetime DEFAULT NULL,
  `r_Explorer_busy` datetime DEFAULT NULL,
  `r_Corvette_busy` datetime DEFAULT NULL,
  `r_Frigate_busy` datetime DEFAULT NULL,
  `r_Destroyer_busy` datetime DEFAULT NULL,
  `r_Cruiser_busy` datetime DEFAULT NULL,
  `r_Battlecruiser_busy` datetime DEFAULT NULL,
  `r_Carrier_busy` datetime DEFAULT NULL,
  `r_Dreadnought_busy` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `virtualops`
--

CREATE TABLE `virtualops` (
  `id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `parent_trx` varchar(50) DEFAULT NULL,
  `trigger_date` datetime NOT NULL,
  `trigger_block_num` int(11) DEFAULT NULL,
  `user` varchar(20) NOT NULL,
  `tr_type` varchar(256) NOT NULL,
  `tr_var1` varchar(256) DEFAULT NULL,
  `tr_var2` varchar(256) DEFAULT NULL,
  `tr_var3` varchar(256) DEFAULT NULL,
  `tr_var4` varchar(256) DEFAULT NULL,
  `tr_var5` varchar(256) DEFAULT NULL,
  `tr_var6` varchar(256) DEFAULT NULL,
  `tr_var7` varchar(256) DEFAULT NULL,
  `tr_var8` varchar(256) DEFAULT NULL,
  `tr_status` int(11) NOT NULL,
  `trx` text,
  `block_num` int(11) DEFAULT NULL,
  `block_date` datetime DEFAULT NULL,
  `cords_hor` int(11) DEFAULT NULL,
  `cords_ver` int(11) DEFAULT NULL,
  `mission_id` varchar(50) DEFAULT NULL,
  `qyt_coal` float DEFAULT NULL,
  `qyt_ore` float DEFAULT NULL,
  `qyt_copper` float DEFAULT NULL,
  `qyt_uranium` float DEFAULT NULL,
  `busy_until` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `activity`
--
ALTER TABLE `activity`
  ADD PRIMARY KEY (`id`),
  ADD KEY `mission_id` (`mission_id`);

--
-- Indizes für die Tabelle `auction`
--
ALTER TABLE `auction`
  ADD PRIMARY KEY (`trx_id`);

--
-- Indizes für die Tabelle `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`uid`),
  ADD KEY `owner` (`owner`,`activated_trx`,`last_owner`),
  ADD KEY `owner_2` (`owner`,`activated_trx`,`item_gifted_at`,`last_owner`);

--
-- Indizes für die Tabelle `missions`
--
ALTER TABLE `missions`
  ADD PRIMARY KEY (`mission_id`),
  ADD KEY `user` (`user`,`date`),
  ADD KEY `user_2` (`user`),
  ADD KEY `cords_hor` (`cords_hor`,`cords_ver`),
  ADD KEY `cords_hor_dest` (`cords_hor_dest`,`cords_ver_dest`);

--
-- Indizes für die Tabelle `planetlevels`
--
ALTER TABLE `planetlevels`
  ADD PRIMARY KEY (`id`),
  ADD KEY `rarity` (`rarity`);

--
-- Indizes für die Tabelle `planets`
--
ALTER TABLE `planets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user` (`user`),
  ADD KEY `cords_hor` (`cords_hor`,`cords_ver`),
  ADD KEY `bonus` (`bonus`,`planet_type`);

--
-- Indizes für die Tabelle `planettypes`
--
ALTER TABLE `planettypes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type_id` (`type_id`);

--
-- Indizes für die Tabelle `productivity`
--
ALTER TABLE `productivity`
  ADD PRIMARY KEY (`id`),
  ADD KEY `name` (`name`,`level`);

--
-- Indizes für die Tabelle `ranking`
--
ALTER TABLE `ranking`
  ADD PRIMARY KEY (`user`),
  ADD KEY `ix_ranking_12dea96fec205935` (`user`);

--
-- Indizes für die Tabelle `ships`
--
ALTER TABLE `ships`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type` (`type`,`cords_hor`,`cords_ver`),
  ADD KEY `mission_id` (`mission_id`);

--
-- Indizes für die Tabelle `shipstats`
--
ALTER TABLE `shipstats`
  ADD PRIMARY KEY (`name`),
  ADD KEY `name` (`name`,`level`),
  ADD KEY `name_2` (`name`);

--
-- Indizes für die Tabelle `shop`
--
ALTER TABLE `shop`
  ADD PRIMARY KEY (`itemid`),
  ADD KEY `boost_percentage` (`boost_percentage`);

--
-- Indizes für die Tabelle `skillcosts`
--
ALTER TABLE `skillcosts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `name` (`name`),
  ADD KEY `name_2` (`name`,`level`);

--
-- Indizes für die Tabelle `space`
--
ALTER TABLE `space`
  ADD PRIMARY KEY (`id`),
  ADD KEY `c_hor` (`c_hor`,`c_ver`),
  ADD KEY `user` (`user`);

--
-- Indizes für die Tabelle `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_status_87ea5dfc8b8e384d` (`id`);

--
-- Indizes für die Tabelle `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trx` (`trx`),
  ADD KEY `block_num` (`block_num`),
  ADD KEY `block_num_2` (`block_num`,`virtualop`),
  ADD KEY `tr_status` (`tr_status`,`date`);

--
-- Indizes für die Tabelle `transfers`
--
ALTER TABLE `transfers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trx` (`trx`),
  ADD KEY `tr_status` (`tr_status`,`date`);

--
-- Indizes für die Tabelle `translate`
--
ALTER TABLE `translate`
  ADD PRIMARY KEY (`id`),
  ADD KEY `variable` (`variable`);

--
-- Indizes für die Tabelle `upgradecosts`
--
ALTER TABLE `upgradecosts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `name` (`name`,`level`);

--
-- Indizes für die Tabelle `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `username` (`username`);

--
-- Indizes für die Tabelle `virtualops`
--
ALTER TABLE `virtualops`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trigger_date` (`trigger_date`),
  ADD KEY `trigger_date_2` (`trigger_date`,`tr_status`),
  ADD KEY `mission_id` (`mission_id`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `activity`
--
ALTER TABLE `activity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;
--
-- AUTO_INCREMENT für Tabelle `auction`
--
ALTER TABLE `auction`
  MODIFY `trx_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT für Tabelle `planetlevels`
--
ALTER TABLE `planetlevels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT für Tabelle `planettypes`
--
ALTER TABLE `planettypes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT für Tabelle `productivity`
--
ALTER TABLE `productivity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=189;
--
-- AUTO_INCREMENT für Tabelle `skillcosts`
--
ALTER TABLE `skillcosts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=561;
--
-- AUTO_INCREMENT für Tabelle `space`
--
ALTER TABLE `space`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;
--
-- AUTO_INCREMENT für Tabelle `status`
--
ALTER TABLE `status`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT für Tabelle `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=145876;
--
-- AUTO_INCREMENT für Tabelle `transfers`
--
ALTER TABLE `transfers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=914;
--
-- AUTO_INCREMENT für Tabelle `translate`
--
ALTER TABLE `translate`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=64;
--
-- AUTO_INCREMENT für Tabelle `upgradecosts`
--
ALTER TABLE `upgradecosts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=270;
--
-- AUTO_INCREMENT für Tabelle `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1686;
--
-- AUTO_INCREMENT für Tabelle `virtualops`
--
ALTER TABLE `virtualops`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=59977;

