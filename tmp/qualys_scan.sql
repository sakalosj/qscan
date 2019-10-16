-- MySQL dump 10.13  Distrib 8.0.17, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: qualys_scan
-- ------------------------------------------------------
-- Server version	8.0.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `patch`
--
CREATE DATABASE `qualys_scan1` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */
DROP TABLE IF EXISTS `patch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patch` (
  `qid` int(11) NOT NULL AUTO_INCREMENT,
  `severity` int(11) DEFAULT NULL,
  `title` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`qid`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `qid` int(11) DEFAULT NULL,
  `request_id_fk` int(11) NOT NULL,
  `title` varchar(50) NOT NULL,
  `status` varchar(30) NOT NULL,
  `launched` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `request_id_fk` (`request_id_fk`),
  CONSTRAINT `report_ibfk_1` FOREIGN KEY (`request_id_fk`) REFERENCES `request` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1028 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `request`
--

DROP TABLE IF EXISTS `request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `request` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(30) NOT NULL,
  `status` varchar(50) NOT NULL,
  `ip` varchar(300) NOT NULL,
  `owner` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=568 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scan`
--

DROP TABLE IF EXISTS `scan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scan` (
  `id` varchar(30) NOT NULL,
  `request_id_fk` int(11) DEFAULT NULL,
  `region` varchar(10) NOT NULL,
  `scan_title` varchar(100) DEFAULT NULL,
  `status` varchar(15) NOT NULL DEFAULT 'New' COMMENT '0 - new entry\n1 - scan processed\n9xx - error messages',
  `ip` text,
  `option_title` varchar(45) DEFAULT NULL,
  `iscanner_name` varchar(45) NOT NULL,
  `priority` varchar(45) DEFAULT '5',
  `datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `UNIQUE_qrequest_fk_region` (`request_id_fk`,`region`),
  KEY `FK_qsca_qreq_idx` (`request_id_fk`),
  CONSTRAINT `FK_qsca_qreq` FOREIGN KEY (`request_id_fk`) REFERENCES `request` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `server`
--

DROP TABLE IF EXISTS `server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server` (
  `ip` varchar(15) NOT NULL,
  `server_id_fk` int(11) DEFAULT NULL,
  `last_report` varchar(45) DEFAULT NULL,
  `temp` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ip`),
  KEY `FK_ops.server_server_idx` (`server_id_fk`),
  CONSTRAINT `FK_server_qualys_server` FOREIGN KEY (`server_id_fk`) REFERENCES `data`.`server` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `server2patch`
--

DROP TABLE IF EXISTS `server2patch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server2patch` (
  `request2server_request_id_fk` int(11) NOT NULL,
  `request2server_server_ip_fk` varchar(15) NOT NULL,
  `patch_qid_fk` int(11) NOT NULL,
  PRIMARY KEY (`request2server_server_ip_fk`,`request2server_request_id_fk`,`patch_qid_fk`),
  KEY `FK_pat_ser2pat_idx` (`patch_qid_fk`),
  KEY `FK_req2ser_ser2pat` (`request2server_request_id_fk`,`request2server_server_ip_fk`),
  CONSTRAINT `FK_pat_ser2pat` FOREIGN KEY (`patch_qid_fk`) REFERENCES `patch` (`qid`),
  CONSTRAINT `FK_req2ser_ser2pat` FOREIGN KEY (`request2server_request_id_fk`, `request2server_server_ip_fk`) REFERENCES `request2server` (`request_id_fk`, `server_ip_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `server2vulner`
--

DROP TABLE IF EXISTS `server2vulner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server2vulner` (
  `request2server_request_id_fk` int(11) NOT NULL,
  `request2server_server_ip_fk` varchar(15) NOT NULL,
  `vulner_qid_fk` int(11) NOT NULL,
  `qualys_cat` text,
  PRIMARY KEY (`request2server_request_id_fk`,`request2server_server_ip_fk`,`vulner_qid_fk`),
  KEY `FK_vul_ser2vul_idx` (`vulner_qid_fk`),
  CONSTRAINT `FK_req2ser_ser2vul` FOREIGN KEY (`request2server_request_id_fk`, `request2server_server_ip_fk`) REFERENCES `request2server` (`request_id_fk`, `server_ip_fk`),
  CONSTRAINT `FK_vul_ser2vul` FOREIGN KEY (`vulner_qid_fk`) REFERENCES `vulner` (`qid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vulner`
--

DROP TABLE IF EXISTS `vulner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vulner` (
  `qid` int(11) NOT NULL,
  `severity` int(11) DEFAULT NULL,
  `cveid` text,
  `title` varchar(100) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `xml_data` text,
  `category` varchar(45) DEFAULT NULL,
  `solution` text,
  `dhl_category` varchar(45) DEFAULT NULL,
  `dhl_type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`qid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'qualys_scan'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-10-11 22:02:14
