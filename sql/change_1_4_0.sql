CREATE TABLE `blocks` (
  `block_num` int(11) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `blocks`
--
ALTER TABLE `blocks`
  ADD PRIMARY KEY (`block_num`),
  ADD KEY `timestamp` (`timestamp`);

ALTER TABLE `blocks`
ADD `block_id` varchar(50) NULL,
ADD `previous` varchar(50) NULL AFTER `block_id`;