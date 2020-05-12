
CREATE TABLE `stardust` (
  `id` int(11) NOT NULL,
  `trx` varchar(50) DEFAULT NULL,
  `from_user` varchar(16) DEFAULT NULL,
  `tr_type` varchar(256) NOT NULL,
  `tr_status` int(11) NOT NULL,
  `date` datetime(6) DEFAULT NULL,
  `to_user` varchar(16) DEFAULT NULL,
  `amount` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `stardust`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trx` (`trx`),
  ADD KEY `from_user` (`from_user`),
  ADD KEY `to_user` (`to_user`);

ALTER TABLE `stardust`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
  
ALTER TABLE `users` ADD INDEX( `stardust`);