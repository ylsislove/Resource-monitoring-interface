CREATE TABLE `stat` (
  `time` int(11) NOT NULL,
  `host` varchar(256) DEFAULT NULL,
  `mem_free` int(11) DEFAULT NULL,
  `mem_usage` int(11) DEFAULT NULL,
  `mem_total` int(11) DEFAULT NULL,
  `mem_percent` float(255,0) DEFAULT NULL,
  `cpu_percent` float(255,0) DEFAULT NULL,
  `network_sent` int(255) DEFAULT NULL,
  `network_recv` int(255) DEFAULT NULL,
  PRIMARY KEY (`time`) USING BTREE,
  KEY `host` (`host`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;