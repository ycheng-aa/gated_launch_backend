-- MySQL dump 10.13  Distrib 5.7.18, for macos10.12 (x86_64)
--
-- Host: localhost    Database: gated_launch
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app_app`
--

DROP TABLE IF EXISTS `app_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `desc` longtext,
  `image_id` varchar(18) NOT NULL,
  `bp_app_id` int(11) DEFAULT NULL,
  `apphub_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `apphub_name` (`apphub_name`),
  KEY `app_app_image_id_9dfebc45_fk_common_image_image_id` (`image_id`),
  CONSTRAINT `app_app_image_id_9dfebc45_fk_common_image_image_id` FOREIGN KEY (`image_id`) REFERENCES `common_image` (`image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_app`
--

LOCK TABLES `app_app` WRITE;
/*!40000 ALTER TABLE `app_app` DISABLE KEYS */;
INSERT INTO `app_app` VALUES (1,'2017-06-29 18:25:11.681308','2017-06-29 18:25:11.681342','ffan','非凡','ffffffffffffff',1,NULL),(2,'2017-06-29 18:44:34.375291','2017-06-29 18:44:34.375329','快钱','快钱','ffffffffffffff',17,NULL);
/*!40000 ALTER TABLE `app_app` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_app_types`
--

DROP TABLE IF EXISTS `app_app_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_app_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` int(11) NOT NULL,
  `apptype_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_app_types_app_id_0cd57f57_uniq` (`app_id`,`apptype_id`),
  KEY `app_app_types_apptype_id_a84f5027_fk_app_apptype_id` (`apptype_id`),
  CONSTRAINT `app_app_types_app_id_fee81654_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`),
  CONSTRAINT `app_app_types_apptype_id_a84f5027_fk_app_apptype_id` FOREIGN KEY (`apptype_id`) REFERENCES `app_apptype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_app_types`
--

LOCK TABLES `app_app_types` WRITE;
/*!40000 ALTER TABLE `app_app_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_app_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `app_apptype`
--

DROP TABLE IF EXISTS `app_apptype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_apptype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(20) NOT NULL,
  `desc` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_apptype`
--

LOCK TABLES `app_apptype` WRITE;
/*!40000 ALTER TABLE `app_apptype` DISABLE KEYS */;
INSERT INTO `app_apptype` VALUES (1,'2017-06-29 18:24:46.630373','2017-06-29 18:24:46.630407','ios','ios'),(2,'2017-07-03 15:37:40.795271','2017-07-03 15:37:40.795321','android',NULL);
/*!40000 ALTER TABLE `app_apptype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permissi_content_type_id_2f476e4b_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add permission',3,'add_permission'),(8,'Can change permission',3,'change_permission'),(9,'Can delete permission',3,'delete_permission'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add Token',6,'add_token'),(17,'Can change Token',6,'change_token'),(18,'Can delete Token',6,'delete_token'),(19,'Can add gray task run status',7,'add_graytaskrunstatus'),(20,'Can change gray task run status',7,'change_graytaskrunstatus'),(21,'Can delete gray task run status',7,'delete_graytaskrunstatus'),(22,'Can add gray app version',8,'add_grayappversion'),(23,'Can change gray app version',8,'change_grayappversion'),(24,'Can delete gray app version',8,'delete_grayappversion'),(25,'Can add gray status',9,'add_graystatus'),(26,'Can change gray status',9,'change_graystatus'),(27,'Can delete gray status',9,'delete_graystatus'),(28,'Can add snapshot outer strategy',10,'add_snapshotouterstrategy'),(29,'Can change snapshot outer strategy',10,'change_snapshotouterstrategy'),(30,'Can delete snapshot outer strategy',10,'delete_snapshotouterstrategy'),(31,'Can add gray task',11,'add_graytask'),(32,'Can change gray task',11,'change_graytask'),(33,'Can delete gray task',11,'delete_graytask'),(34,'Can add gray task log',12,'add_graytasklog'),(35,'Can change gray task log',12,'change_graytasklog'),(36,'Can delete gray task log',12,'delete_graytasklog'),(37,'Can add snapshot inner strategy',13,'add_snapshotinnerstrategy'),(38,'Can change snapshot inner strategy',13,'change_snapshotinnerstrategy'),(39,'Can delete snapshot inner strategy',13,'delete_snapshotinnerstrategy'),(40,'Can add image',14,'add_image'),(41,'Can change image',14,'change_image'),(42,'Can delete image',14,'delete_image'),(43,'Can add app module',15,'add_appmodule'),(44,'Can change app module',15,'change_appmodule'),(45,'Can delete app module',15,'delete_appmodule'),(46,'Can add user group',16,'add_usergroup'),(47,'Can change user group',16,'change_usergroup'),(48,'Can delete user group',16,'delete_usergroup'),(49,'Can add user group type',17,'add_usergrouptype'),(50,'Can change user group type',17,'change_usergrouptype'),(51,'Can delete user group type',17,'delete_usergrouptype'),(52,'Can add department',18,'add_department'),(53,'Can change department',18,'change_department'),(54,'Can delete department',18,'delete_department'),(55,'Can add user',19,'add_user'),(56,'Can change user',19,'change_user'),(57,'Can delete user',19,'delete_user'),(58,'Can add role',20,'add_role'),(59,'Can change role',20,'change_role'),(60,'Can delete role',20,'delete_role'),(61,'Can add app',21,'add_app'),(62,'Can change app',21,'change_app'),(63,'Can delete app',21,'delete_app'),(64,'Can add app type',22,'add_apptype'),(65,'Can change app type',22,'change_apptype'),(66,'Can delete app type',22,'delete_apptype'),(67,'Can add awardee',23,'add_awardee'),(68,'Can change awardee',23,'change_awardee'),(69,'Can delete awardee',23,'delete_awardee'),(70,'Can add award',24,'add_award'),(71,'Can change award',24,'change_award'),(72,'Can delete award',24,'delete_award'),(73,'Can add issue',25,'add_issue'),(74,'Can change issue',25,'change_issue'),(75,'Can delete issue',25,'delete_issue'),(79,'Can add push channel',27,'add_pushchannel'),(80,'Can change push channel',27,'change_pushchannel'),(81,'Can delete push channel',27,'delete_pushchannel'),(82,'Can add inner strategy',28,'add_innerstrategy'),(83,'Can change inner strategy',28,'change_innerstrategy'),(84,'Can delete inner strategy',28,'delete_innerstrategy'),(85,'Can add outer strategy',29,'add_outerstrategy'),(86,'Can change outer strategy',29,'change_outerstrategy'),(87,'Can delete outer strategy',29,'delete_outerstrategy'),(88,'Can add app versions',30,'add_appversions'),(89,'Can change app versions',30,'change_appversions'),(90,'Can delete app versions',30,'delete_appversions'),(91,'Can add clientversion',31,'add_clientversion'),(92,'Can change clientversion',31,'change_clientversion'),(93,'Can delete clientversion',31,'delete_clientversion'),(94,'Can add issue status',32,'add_issuestatus'),(95,'Can change issue status',32,'change_issuestatus'),(96,'Can delete issue status',32,'delete_issuestatus');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken_token`
--

DROP TABLE IF EXISTS `authtoken_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
INSERT INTO `authtoken_token` VALUES ('05a684b49b9578e5808431f9858800827025ea2d','2017-06-30 15:13:03.101443',6),('0ceeb664c0e59912fff9b76aa3906d1d5114644b','2017-06-30 15:13:15.926135',7),('aef193215eeac6e55b6620fd9bac130f16270170','2017-06-29 18:54:01.506323',1),('db3af52c59a50670715c2182a8c8f1c27f07bc07','2017-06-30 15:12:31.964171',5);
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `award_award`
--

DROP TABLE IF EXISTS `award_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `award_award` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `desc` longtext,
  `image_id` varchar(18) NOT NULL,
  `app_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `award_award_f33175e6` (`image_id`),
  KEY `award_award_f382adfe` (`app_id`),
  CONSTRAINT `award_award_app_id_646b6d9b_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`),
  CONSTRAINT `award_award_image_id_04351b5b_fk_common_image_image_id` FOREIGN KEY (`image_id`) REFERENCES `common_image` (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `award_award`
--

LOCK TABLES `award_award` WRITE;
/*!40000 ALTER TABLE `award_award` DISABLE KEYS */;
/*!40000 ALTER TABLE `award_award` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `award_awardee`
--

DROP TABLE IF EXISTS `award_awardee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `award_awardee` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `desc` longtext,
  `award_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `award_awardee_award_id_4b866bde_uniq` (`award_id`,`user_id`),
  KEY `award_awardee_award_id_62c9df04_fk_award_award_id` (`award_id`),
  KEY `award_awardee_user_id_580f0aa8_fk_gated_launch_auth_user_id` (`user_id`),
  CONSTRAINT `award_awardee_award_id_62c9df04_fk_award_award_id` FOREIGN KEY (`award_id`) REFERENCES `award_award` (`id`),
  CONSTRAINT `award_awardee_user_id_580f0aa8_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `award_awardee`
--

LOCK TABLES `award_awardee` WRITE;
/*!40000 ALTER TABLE `award_awardee` DISABLE KEYS */;
/*!40000 ALTER TABLE `award_awardee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `common_appmodule`
--

DROP TABLE IF EXISTS `common_appmodule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `common_appmodule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `module_name` varchar(100) NOT NULL,
  `app_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `common_appmodule_app_id_38fe2c44_fk_app_app_id` (`app_id`),
  CONSTRAINT `common_appmodule_app_id_38fe2c44_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_appmodule`
--

LOCK TABLES `common_appmodule` WRITE;
/*!40000 ALTER TABLE `common_appmodule` DISABLE KEYS */;
/*!40000 ALTER TABLE `common_appmodule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `common_image`
--

DROP TABLE IF EXISTS `common_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `common_image` (
  `image_id` varchar(18) NOT NULL,
  `image_name` varchar(1024) DEFAULT NULL,
  `image_desc` longtext,
  PRIMARY KEY (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_image`
--

LOCK TABLES `common_image` WRITE;
/*!40000 ALTER TABLE `common_image` DISABLE KEYS */;
INSERT INTO `common_image` VALUES ('ffffffffffffff','1.jgp','图片');
/*!40000 ALTER TABLE `common_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_gated_launch_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2017-06-29 18:24:07.445580','ffffffffffffff','Image object',1,'[{\"added\": {}}]',14,1),(2,'2017-06-29 18:24:46.630969','1','ios',1,'[{\"added\": {}}]',22,1),(3,'2017-06-29 18:25:11.685374','1','ffan',1,'[{\"added\": {}}]',21,1),(4,'2017-06-29 18:44:34.383749','2','快钱',1,'[{\"added\": {}}]',21,1),(5,'2017-06-30 11:47:32.048945','2','normal_user',1,'[{\"added\": {}}]',19,1),(6,'2017-06-30 11:48:53.153954','3','admin_user',1,'[{\"added\": {}}]',19,1),(7,'2017-06-30 11:50:18.172504','4','app_owner_user',1,'[{\"added\": {}}]',19,1),(8,'2017-06-30 11:52:12.944312','6','ffan: owner ffan_owner_group',1,'[{\"added\": {}}]',16,1),(9,'2017-06-30 14:12:23.359192','4','app_owner_user',2,'[{\"changed\": {\"fields\": [\"is_staff\"]}}]',19,1),(10,'2017-06-30 14:15:31.588947','2','normal_user',3,'',19,1),(11,'2017-06-30 14:15:41.560555','3','admin_user',3,'',19,1),(12,'2017-06-30 14:15:47.591095','4','app_owner_user',3,'',19,1),(13,'2017-06-30 14:21:50.825024','6','admin_user',2,'[{\"changed\": {\"fields\": [\"role\"]}}]',19,1),(14,'2017-06-30 14:22:08.848741','7','app_owner_user',2,'[{\"changed\": {\"fields\": [\"role\"]}}]',19,1),(15,'2017-06-30 14:22:44.678730','6','ffan: owner ffan_owner_group',2,'[]',16,1),(16,'2017-07-10 16:54:02.921264','1','一级部门 1',1,'[{\"added\": {}}]',18,1),(17,'2017-07-10 16:54:13.044301','2','一级部门 2',1,'[{\"added\": {}}]',18,1),(18,'2017-07-10 16:54:33.370228','3','二级部门 1',1,'[{\"added\": {}}]',18,1),(19,'2017-07-10 16:54:50.832940','4','二级部门 2',1,'[{\"added\": {}}]',18,1),(20,'2017-07-10 16:59:56.459665','8','lurena',2,'[{\"changed\": {\"fields\": [\"department\"]}}]',19,1),(21,'2017-07-10 17:00:08.676614','9','lurenb',2,'[{\"changed\": {\"fields\": [\"department\"]}}]',19,1),(22,'2017-07-19 20:10:43.096779','12','chengyu21',3,'',19,1),(23,'2017-07-19 20:15:00.610774','13','chengyu21',3,'',19,1),(24,'2017-07-20 09:01:41.606257','21','chengyu21',3,'',19,1),(25,'2017-07-20 09:04:16.727521','23','chengyu21',3,'',19,1),(26,'2017-07-20 09:06:54.106040','24','chengyu21',3,'',19,1),(27,'2017-07-20 09:52:25.413132','26','chengyu21',2,'[{\"changed\": {\"fields\": [\"password\", \"department\"]}}]',19,1),(28,'2017-07-20 15:48:13.820446','26','chengyu21',3,'',19,1),(29,'2017-07-20 15:49:55.391980','566','chengyu21',3,'',19,1),(30,'2017-07-20 15:50:28.365377','567','chengyu21',3,'',19,1),(31,'2017-07-20 15:54:33.503908','568','chengyu21',3,'',19,1),(32,'2017-07-20 16:46:14.090288','570','chengyu21',3,'',19,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(21,'app','app'),(22,'app','apptype'),(2,'auth','group'),(3,'auth','permission'),(6,'authtoken','token'),(24,'award','award'),(23,'award','awardee'),(30,'bp','appversions'),(31,'bp','clientversion'),(15,'common','appmodule'),(14,'common','image'),(4,'contenttypes','contenttype'),(18,'gated_launch_auth','department'),(20,'gated_launch_auth','role'),(19,'gated_launch_auth','user'),(25,'issue','issue'),(32,'issue','issuestatus'),(5,'sessions','session'),(28,'strategy','innerstrategy'),(29,'strategy','outerstrategy'),(27,'strategy','pushchannel'),(8,'task_manager','grayappversion'),(9,'task_manager','graystatus'),(11,'task_manager','graytask'),(12,'task_manager','graytasklog'),(7,'task_manager','graytaskrunstatus'),(13,'task_manager','snapshotinnerstrategy'),(10,'task_manager','snapshotouterstrategy'),(16,'user_group','usergroup'),(17,'user_group','usergrouptype');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2017-06-29 18:18:59.315166'),(2,'contenttypes','0002_remove_content_type_name','2017-06-29 18:18:59.367363'),(3,'auth','0001_initial','2017-06-29 18:18:59.496446'),(4,'auth','0002_alter_permission_name_max_length','2017-06-29 18:18:59.516234'),(5,'auth','0003_alter_user_email_max_length','2017-06-29 18:18:59.524895'),(6,'auth','0004_alter_user_username_opts','2017-06-29 18:18:59.543425'),(7,'auth','0005_alter_user_last_login_null','2017-06-29 18:18:59.555131'),(8,'auth','0006_require_contenttypes_0002','2017-06-29 18:18:59.557582'),(9,'auth','0007_alter_validators_add_error_messages','2017-06-29 18:18:59.568812'),(10,'auth','0008_alter_user_username_max_length','2017-06-29 18:18:59.582220'),(11,'gated_launch_auth','0001_initial','2017-06-29 18:18:59.899078'),(12,'admin','0001_initial','2017-06-29 18:18:59.965995'),(13,'admin','0002_logentry_remove_auto_add','2017-06-29 18:19:00.016439'),(14,'common','0001_initial','2017-06-29 18:19:00.031653'),(15,'app','0001_initial','2017-06-29 18:19:00.180038'),(16,'app','0002_auto_20170629_1517','2017-06-29 18:19:00.182329'),(17,'authtoken','0001_initial','2017-06-29 18:19:00.232990'),(18,'authtoken','0002_auto_20160226_1747','2017-06-29 18:19:00.369139'),(19,'common','0002_appmodule','2017-06-29 18:19:00.422600'),(20,'common','0003_auto_20170629_1023','2017-06-29 18:19:00.479149'),(21,'common','0003_auto_20170628_0205','2017-06-29 18:19:00.575932'),(22,'common','0004_merge_20170629_1517','2017-06-29 18:19:00.578481'),(23,'common','0005_auto_20170629_1517','2017-06-29 18:19:00.700930'),(24,'award','0001_initial','2017-06-29 18:19:00.786720'),(25,'award','0002_auto_20170629_1517','2017-06-29 18:19:00.950872'),(26,'gated_launch_auth','0002_auto_20170628_0831','2017-06-29 18:19:01.053777'),(27,'gated_launch_auth','0003_auto_20170629_1022','2017-06-29 18:19:01.166200'),(28,'task_manager','0001_initial','2017-06-29 18:19:02.314000'),(29,'task_manager','0002_auto_20170627_1123','2017-06-29 18:19:02.682601'),(30,'issue','0001_initial','2017-06-29 18:19:02.968072'),(31,'sessions','0001_initial','2017-06-29 18:19:03.000834'),(32,'user_group','0001_initial','2017-06-29 18:19:03.114185'),(33,'user_group','0002_auto_20170621_0314','2017-06-29 18:19:03.259773'),(34,'user_group','0003_usergroup_users','2017-06-29 18:19:03.378023'),(35,'strategy','0001_initial','2017-06-29 18:19:03.808999'),(36,'strategy','0002_auto_20170628_1547','2017-06-29 18:19:03.996433'),(37,'task_manager','0003_auto_20170628_1547','2017-06-29 18:19:04.822132'),(38,'user_group','0004_auto_20170628_0842','2017-06-29 18:19:05.154208'),(39,'user_group','0005_auto_20170629_1022','2017-06-29 18:19:05.370999'),(40,'user_group','0006_auto_20170629_1517','2017-06-29 18:19:05.544228'),(41,'app','0001_squashed_0002_auto_20170629_1517','2017-06-29 18:19:05.549599'),(42,'user_group','0007_auto_20170630_0955','2017-06-30 09:56:08.011923'),(43,'app','0002_remove_app_managers','2017-06-30 19:42:27.436679'),(44,'app','0002_auto_20170630_1027','2017-07-03 15:37:40.838180'),(45,'app','0003_merge_20170703_1410','2017-07-03 15:37:40.841442'),(46,'gated_launch_auth','0004_user_phone','2017-07-07 13:37:44.376718'),(47,'award','0003_auto_20170711_1308','2017-07-12 19:57:18.857103'),(48,'bp','0001_initial','2017-07-12 19:57:18.867502'),(49,'gated_launch_auth','0005_auto_20170712_1430','2017-07-12 19:57:19.098051'),(50,'task_manager','0004_auto_20170705_1624','2017-07-12 19:57:20.446669'),(51,'strategy','0003_auto_20170705_1624','2017-07-12 19:57:20.594379'),(52,'task_manager','0004_auto_20170706_1706','2017-07-12 19:57:21.201816'),(53,'task_manager','0005_merge_20170707_1058','2017-07-12 19:57:21.205334'),(54,'task_manager','0006_auto_20170710_1526','2017-07-12 19:57:22.292951'),(55,'app','0004_app_apphub_name','2017-07-14 09:12:36.736715'),(56,'app','0005_auto_20170714_1052','2017-07-14 11:24:15.561545'),(57,'task_manager','0007_auto_20170714_1253','2017-07-14 13:04:16.149623'),(58,'issue','0002_auto_20170718_1211','2017-07-19 20:10:32.326661'),(59,'issue','0003_auto_20170719_1122','2017-07-19 20:10:32.508369'),(60,'strategy','0004_auto_20170719_1444','2017-07-19 20:10:33.760129'),(61,'task_manager','0008_auto_20170719_1444','2017-07-19 20:10:35.143227');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('enx1t8rfzciaxn25tfbvkbeklv5cpga1','NzAzMGU1MjgxOTIzNDJjZjg3MjBiNTNlZTVmZmRjMjJkOTYxYzRkODp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZDliMDEwYzZkMGEzZWU2N2JhN2NiNzY3NGU0M2UzZDY5YTM0Y2YwYSIsIl9hdXRoX3VzZXJfaWQiOiI1In0=','2017-07-14 15:12:04.375586'),('n6k488yip2mr1tgzv04hmtq987wdh5lo','Mjk4OWYyOGE1Y2YxNDcwMjE5YmQ2NWM1MmUxY2FlZjUzNjRlMTFjODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5YzhmMWIzZDgzMzZhZWNjMWVhNDhjOTBkY2ZmNWE3OGQ2MTU0MjJlIn0=','2017-07-13 18:23:49.860049'),('q1k8xjxjqhjg7fsfqy0gfjatro2wwaef','MjA5NTI1NWI2ZTMyNWQ2ZjE0YjNkZjhlZDIyYmQ0YWYwZTM5ZmFhZTp7Il9hdXRoX3VzZXJfaGFzaCI6IjljOGYxYjNkODMzNmFlY2MxZWE0OGM5MGRjZmY1YTc4ZDYxNTQyMmUiLCJfYXV0aF91c2VyX2lkIjoiMSIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIn0=','2017-08-02 16:15:19.409965');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gated_launch_auth_department`
--

DROP TABLE IF EXISTS `gated_launch_auth_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gated_launch_auth_department` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gated_launch_auth_department_caf7cc51` (`lft`),
  KEY `gated_launch_auth_department_3cfbd988` (`rght`),
  KEY `gated_launch_auth_department_656442a0` (`tree_id`),
  KEY `gated_launch_auth_department_c9e9a848` (`level`),
  KEY `gated_launch_auth_department_6be37982` (`parent_id`),
  CONSTRAINT `gated_laun_parent_id_0f792ea1_fk_gated_launch_auth_department_id` FOREIGN KEY (`parent_id`) REFERENCES `gated_launch_auth_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gated_launch_auth_department`
--

LOCK TABLES `gated_launch_auth_department` WRITE;
/*!40000 ALTER TABLE `gated_launch_auth_department` DISABLE KEYS */;
INSERT INTO `gated_launch_auth_department` VALUES (1,'一级部门 1','2017-07-10 16:54:02.916446','2017-07-10 16:54:02.916482',1,4,1,0,NULL),(2,'一级部门 2','2017-07-10 16:54:13.043457','2017-07-10 16:54:13.043490',1,4,2,0,NULL),(3,'二级部门 1','2017-07-10 16:54:33.367307','2017-07-10 16:54:33.367376',2,3,1,1,1),(4,'二级部门 2','2017-07-10 16:54:50.832021','2017-07-10 16:54:50.832057',2,3,2,1,2),(5,'飞凡信息公司','2017-07-19 15:16:24.193636','2017-07-19 15:16:24.193691',1,4,3,0,NULL),(6,'产品技术体系','2017-07-19 15:34:11.782051','2017-07-19 15:34:11.782093',2,3,3,1,5),(7,'','2017-07-20 09:07:07.867601','2017-07-20 09:07:07.867751',1,2,4,0,NULL);
/*!40000 ALTER TABLE `gated_launch_auth_department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gated_launch_auth_role`
--

DROP TABLE IF EXISTS `gated_launch_auth_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gated_launch_auth_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gated_launch_auth_role_name_4f7598e7_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gated_launch_auth_role`
--

LOCK TABLES `gated_launch_auth_role` WRITE;
/*!40000 ALTER TABLE `gated_launch_auth_role` DISABLE KEYS */;
INSERT INTO `gated_launch_auth_role` VALUES (1,'2017-06-29 18:19:01.024613','2017-06-29 18:19:01.024770','admin'),(2,'2017-06-29 18:19:01.028038','2017-06-29 18:19:01.028285','app_owner');
/*!40000 ALTER TABLE `gated_launch_auth_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gated_launch_auth_user`
--

DROP TABLE IF EXISTS `gated_launch_auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gated_launch_auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(255) NOT NULL,
  `full_name` varchar(80) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `last_connected` datetime(6) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `_role_id` int(11) DEFAULT NULL,
  `phone` varchar(20),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `gated_launch_auth_user_bf691be4` (`department_id`),
  KEY `gated_launch_auth_user_18fdd3a7` (`_role_id`),
  CONSTRAINT `gated__department_id_7d8edbb3_fk_gated_launch_auth_department_id` FOREIGN KEY (`department_id`) REFERENCES `gated_launch_auth_department` (`id`),
  CONSTRAINT `gated_launch_auth__role_id_760523cd_fk_gated_launch_auth_role_id` FOREIGN KEY (`_role_id`) REFERENCES `gated_launch_auth_role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=572 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gated_launch_auth_user`
--

LOCK TABLES `gated_launch_auth_user` WRITE;
/*!40000 ALTER TABLE `gated_launch_auth_user` DISABLE KEYS */;
INSERT INTO `gated_launch_auth_user` VALUES (1,'pbkdf2_sha256$30000$94FopcikwGIj$kenRMiio9acpA9Om0UOwaQgkEXc0v4JB5jMFHgfpjYE=','2017-07-19 16:15:19.407189',1,'ycheng','','chengyu21@wanda.cn',1,1,'2017-06-29 18:23:41.303771',NULL,NULL,NULL,NULL),(5,'pbkdf2_sha256$30000$rt5BTJ81SNPs$JY1SG3hwBXElYrnAINL710k2SubaQxe6wqZwPQLWQDo=','2017-06-30 15:12:04.368257',1,'normal_user','','normal_user@wanda.cn',1,1,'2017-06-30 14:19:46.618448',NULL,NULL,NULL,NULL),(6,'pbkdf2_sha256$30000$GC4Dr2NS2IGO$e5X7/fh4zEuPgF//qVPfn3iGUtnNsI0K+9JFGbal/S0=',NULL,1,'admin_user','','admin_user@wanda.cn',1,1,'2017-06-30 14:20:23.000000',NULL,NULL,1,NULL),(7,'pbkdf2_sha256$30000$Z2uOw6ow6fAC$Jktq0Jz8y49wQQaUxGIRo7PReP2LIsXBAwuc1jh7l+0=',NULL,1,'app_owner_user','','app_owner_user@wanda.cn',1,1,'2017-06-30 14:21:17.000000',NULL,NULL,2,NULL),(8,'pbkdf2_sha256$30000$w1XZZuoGAqPn$Csc/WE+yxg7/ma/RR8F9bbHdVlpE+auQO5yArvTbPV4=',NULL,1,'lurena','','lurena@test.com',1,1,'2017-07-07 15:39:12.000000',NULL,4,NULL,''),(9,'pbkdf2_sha256$30000$OB6dveAZVqLv$IrgbL5VZuvzhvPQctm79P3PuipSlREaZLBXtZnLiExs=',NULL,1,'lurenb','','lurenb@test.com',1,1,'2017-07-07 15:39:46.000000',NULL,4,NULL,''),(10,'pbkdf2_sha256$30000$SMeYULbndS2O$IoQSXwMKSsw7XDft6ZkVAmo7PLiPYbfFgzhnnGYqS5k=',NULL,1,'lurenc','','lurenc@test.com',1,1,'2017-07-07 15:40:12.957417',NULL,NULL,NULL,NULL),(11,'pbkdf2_sha256$30000$HqGvXXbWcjUz$olTjkG5Zbd6f0p9LmSpRiEELp8s1+81cLCvqxVLqHgM=',NULL,1,'lurend','','lurend@test.com',1,1,'2017-07-07 15:40:53.430397',NULL,NULL,NULL,NULL),(571,'',NULL,0,'chengyu21','','chengyu21@wanda.cn',0,1,'2017-07-20 16:47:08.531828',NULL,6,NULL,'18600478348');
/*!40000 ALTER TABLE `gated_launch_auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gated_launch_auth_user_groups`
--

DROP TABLE IF EXISTS `gated_launch_auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gated_launch_auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gated_launch_auth_user_groups_user_id_7bfdfca6_uniq` (`user_id`,`group_id`),
  KEY `gated_launch_auth_user_groups_group_id_05916489_fk_auth_group_id` (`group_id`),
  CONSTRAINT `gated_launch_auth__user_id_365a3543_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `gated_launch_auth_user_groups_group_id_05916489_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gated_launch_auth_user_groups`
--

LOCK TABLES `gated_launch_auth_user_groups` WRITE;
/*!40000 ALTER TABLE `gated_launch_auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `gated_launch_auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gated_launch_auth_user_user_permissions`
--

DROP TABLE IF EXISTS `gated_launch_auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gated_launch_auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gated_launch_auth_user_user_permissions_user_id_5b5a3290_uniq` (`user_id`,`permission_id`),
  KEY `gated_launch_auth_u_permission_id_4d90615b_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `gated_launch_auth__user_id_0871beb7_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `gated_launch_auth_u_permission_id_4d90615b_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gated_launch_auth_user_user_permissions`
--

LOCK TABLES `gated_launch_auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `gated_launch_auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `gated_launch_auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `issue_issue`
--

DROP TABLE IF EXISTS `issue_issue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `issue_issue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `detail` longtext NOT NULL,
  `score` int(11),
  `jira_link` varchar(200) NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `marker_id` int(11) DEFAULT NULL,
  `task_id` int(11) NOT NULL,
  `app_module_id` int(11),
  `status_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `issue_issue_app_id_52685046_fk_app_app_id` (`app_id`),
  KEY `issue_issue_creator_id_691c300c_fk_gated_launch_auth_user_id` (`creator_id`),
  KEY `issue_issue_marker_id_f7671017_fk_gated_launch_auth_user_id` (`marker_id`),
  KEY `issue_issue_task_id_79332112_fk_task_manager_graytask_id` (`task_id`),
  KEY `issue_issue_c5d9ddac` (`app_module_id`),
  KEY `issue_issue_dc91ed4b` (`status_id`),
  CONSTRAINT `issue_issue_app_id_52685046_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`),
  CONSTRAINT `issue_issue_app_module_id_2bca34f9_fk_common_appmodule_id` FOREIGN KEY (`app_module_id`) REFERENCES `common_appmodule` (`id`),
  CONSTRAINT `issue_issue_creator_id_691c300c_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `issue_issue_marker_id_f7671017_fk_gated_launch_auth_user_id` FOREIGN KEY (`marker_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `issue_issue_status_id_5f411ef1_fk_issue_issuestatus_id` FOREIGN KEY (`status_id`) REFERENCES `issue_issuestatus` (`id`),
  CONSTRAINT `issue_issue_task_id_79332112_fk_task_manager_graytask_id` FOREIGN KEY (`task_id`) REFERENCES `task_manager_graytask` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `issue_issue`
--

LOCK TABLES `issue_issue` WRITE;
/*!40000 ALTER TABLE `issue_issue` DISABLE KEYS */;
/*!40000 ALTER TABLE `issue_issue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `issue_issue_images`
--

DROP TABLE IF EXISTS `issue_issue_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `issue_issue_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `issue_id` int(11) NOT NULL,
  `image_id` varchar(18) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue_issue_images_issue_id_38c1005a_uniq` (`issue_id`,`image_id`),
  KEY `issue_issue_images_image_id_1efebf42_fk_common_image_image_id` (`image_id`),
  CONSTRAINT `issue_issue_images_image_id_1efebf42_fk_common_image_image_id` FOREIGN KEY (`image_id`) REFERENCES `common_image` (`image_id`),
  CONSTRAINT `issue_issue_images_issue_id_d2afd8c1_fk_issue_issue_id` FOREIGN KEY (`issue_id`) REFERENCES `issue_issue` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `issue_issue_images`
--

LOCK TABLES `issue_issue_images` WRITE;
/*!40000 ALTER TABLE `issue_issue_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `issue_issue_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `issue_issuestatus`
--

DROP TABLE IF EXISTS `issue_issuestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `issue_issuestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `issue_issuestatus`
--

LOCK TABLES `issue_issuestatus` WRITE;
/*!40000 ALTER TABLE `issue_issuestatus` DISABLE KEYS */;
INSERT INTO `issue_issuestatus` VALUES (1,'2017-07-19 20:10:32.046662','2017-07-19 20:10:32.046711','新增问题'),(2,'2017-07-19 20:10:32.048758','2017-07-19 20:10:32.048785','问题处理中'),(3,'2017-07-19 20:10:32.050804','2017-07-19 20:10:32.050836','问题关闭');
/*!40000 ALTER TABLE `issue_issuestatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategy_innerstrategy`
--

DROP TABLE IF EXISTS `strategy_innerstrategy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategy_innerstrategy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `push_content` longtext NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `strategy_innerstrategy_app_id_73879a51_fk_app_app_id` (`app_id`),
  KEY `strategy_inners_creator_id_35016f59_fk_gated_launch_auth_user_id` (`creator_id`),
  CONSTRAINT `strategy_inners_creator_id_35016f59_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `strategy_innerstrategy_app_id_73879a51_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategy_innerstrategy`
--

LOCK TABLES `strategy_innerstrategy` WRITE;
/*!40000 ALTER TABLE `strategy_innerstrategy` DISABLE KEYS */;
/*!40000 ALTER TABLE `strategy_innerstrategy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategy_innerstrategy_push_channels`
--

DROP TABLE IF EXISTS `strategy_innerstrategy_push_channels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategy_innerstrategy_push_channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `innerstrategy_id` int(11) NOT NULL,
  `pushchannel_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `strategy_innerstrategy_push_chann_innerstrategy_id_78d9966f_uniq` (`innerstrategy_id`,`pushchannel_id`),
  KEY `strategy_inne_pushchannel_id_44a5c385_fk_strategy_pushchannel_id` (`pushchannel_id`),
  CONSTRAINT `strategy__innerstrategy_id_fb18a183_fk_strategy_innerstrategy_id` FOREIGN KEY (`innerstrategy_id`) REFERENCES `strategy_innerstrategy` (`id`),
  CONSTRAINT `strategy_inne_pushchannel_id_44a5c385_fk_strategy_pushchannel_id` FOREIGN KEY (`pushchannel_id`) REFERENCES `strategy_pushchannel` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategy_innerstrategy_push_channels`
--

LOCK TABLES `strategy_innerstrategy_push_channels` WRITE;
/*!40000 ALTER TABLE `strategy_innerstrategy_push_channels` DISABLE KEYS */;
/*!40000 ALTER TABLE `strategy_innerstrategy_push_channels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategy_innerstrategy_user_groups`
--

DROP TABLE IF EXISTS `strategy_innerstrategy_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategy_innerstrategy_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `innerstrategy_id` int(11) NOT NULL,
  `usergroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `strategy_innerstrategy_user_group_innerstrategy_id_9f54a059_uniq` (`innerstrategy_id`,`usergroup_id`),
  KEY `strategy_inners_usergroup_id_cd5751fc_fk_user_group_usergroup_id` (`usergroup_id`),
  CONSTRAINT `strategy__innerstrategy_id_84ae5f3e_fk_strategy_innerstrategy_id` FOREIGN KEY (`innerstrategy_id`) REFERENCES `strategy_innerstrategy` (`id`),
  CONSTRAINT `strategy_inners_usergroup_id_cd5751fc_fk_user_group_usergroup_id` FOREIGN KEY (`usergroup_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategy_innerstrategy_user_groups`
--

LOCK TABLES `strategy_innerstrategy_user_groups` WRITE;
/*!40000 ALTER TABLE `strategy_innerstrategy_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `strategy_innerstrategy_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategy_outerstrategy`
--

DROP TABLE IF EXISTS `strategy_outerstrategy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategy_outerstrategy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `version` varchar(255) NOT NULL,
  `allow_users` longtext NOT NULL,
  `range_dates` varchar(2048) NOT NULL,
  `cities` varchar(1024) NOT NULL,
  `city_enable` tinyint(1) NOT NULL,
  `percentage` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `is_compatible` int(11) NOT NULL,
  `frequency` int(11) NOT NULL,
  `change_log` longtext NOT NULL,
  `change_log_img` varchar(200) NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `channels` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `strategy_outerstrategy_app_id_bb82a0fc_fk_app_app_id` (`app_id`),
  KEY `strategy_outers_creator_id_7f9f8236_fk_gated_launch_auth_user_id` (`creator_id`),
  CONSTRAINT `strategy_outers_creator_id_7f9f8236_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `strategy_outerstrategy_app_id_bb82a0fc_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategy_outerstrategy`
--

LOCK TABLES `strategy_outerstrategy` WRITE;
/*!40000 ALTER TABLE `strategy_outerstrategy` DISABLE KEYS */;
/*!40000 ALTER TABLE `strategy_outerstrategy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `strategy_pushchannel`
--

DROP TABLE IF EXISTS `strategy_pushchannel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `strategy_pushchannel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `strategy_pushchannel`
--

LOCK TABLES `strategy_pushchannel` WRITE;
/*!40000 ALTER TABLE `strategy_pushchannel` DISABLE KEYS */;
INSERT INTO `strategy_pushchannel` VALUES (1,'2017-07-12 19:57:20.589470','2017-07-12 19:57:20.589508','sms'),(2,'2017-07-12 19:57:20.591337','2017-07-12 19:57:20.591366','mail');
/*!40000 ALTER TABLE `strategy_pushchannel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_grayappversion`
--

DROP TABLE IF EXISTS `task_manager_grayappversion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_grayappversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `current_step` int(11) NOT NULL,
  `is_current_use` tinyint(1) NOT NULL,
  `expired` tinyint(1) NOT NULL,
  `app_id` int(11) NOT NULL,
  `current_status_id` int(11) NOT NULL,
  `gray_task_id` int(11) NOT NULL,
  `operator_id` int(11) NOT NULL,
  `android_version` varchar(256) NOT NULL,
  `ios_version` varchar(256) NOT NULL,
  `release_date` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_manager_grayappversion_gray_task_id_a1333686_uniq` (`gray_task_id`,`current_step`),
  KEY `task_manager_grayappversion_app_id_5b872783_fk_app_app_id` (`app_id`),
  KEY `task_manager_grayappversion_b0e0b0e0` (`current_status_id`),
  KEY `task_manager_grayappversion_c25832d1` (`gray_task_id`),
  KEY `task_manager_grayappversion_4d14a16b` (`operator_id`),
  CONSTRAINT `task_ma_current_status_id_d70f3ce9_fk_task_manager_graystatus_id` FOREIGN KEY (`current_status_id`) REFERENCES `task_manager_graystatus` (`id`),
  CONSTRAINT `task_manager_g_gray_task_id_67cc5aed_fk_task_manager_graytask_id` FOREIGN KEY (`gray_task_id`) REFERENCES `task_manager_graytask` (`id`),
  CONSTRAINT `task_manager_g_operator_id_548412dd_fk_gated_launch_auth_user_id` FOREIGN KEY (`operator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `task_manager_grayappversion_app_id_5b872783_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_grayappversion`
--

LOCK TABLES `task_manager_grayappversion` WRITE;
/*!40000 ALTER TABLE `task_manager_grayappversion` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_grayappversion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_graystatus`
--

DROP TABLE IF EXISTS `task_manager_graystatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_graystatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_graystatus`
--

LOCK TABLES `task_manager_graystatus` WRITE;
/*!40000 ALTER TABLE `task_manager_graystatus` DISABLE KEYS */;
INSERT INTO `task_manager_graystatus` VALUES (1,'2017-07-14 13:04:16.138514','2017-07-14 13:04:16.138569','preparation'),(2,'2017-07-14 13:04:16.142813','2017-07-14 13:04:16.142851','testing'),(3,'2017-07-14 13:04:16.145631','2017-07-14 13:04:16.145670','finished');
/*!40000 ALTER TABLE `task_manager_graystatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_graytask`
--

DROP TABLE IF EXISTS `task_manager_graytask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_graytask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `task_name` varchar(256) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `inner_strategy` varchar(256) NOT NULL,
  `outer_strategy` varchar(256) NOT NULL,
  `current_step` int(11) NOT NULL,
  `is_display` tinyint(1) NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `current_status_id` int(11) NOT NULL,
  `image_id` varchar(18),
  PRIMARY KEY (`id`),
  KEY `task_manager_graytasks_app_id_4ef1b40d_fk_app_app_id` (`app_id`),
  KEY `task_manager_gr_creator_id_f82ce419_fk_gated_launch_auth_user_id` (`creator_id`),
  KEY `task_ma_current_status_id_cbbffdf0_fk_task_manager_graystatus_id` (`current_status_id`),
  KEY `task_manager_graytask_f33175e6` (`image_id`),
  CONSTRAINT `task_ma_current_status_id_cbbffdf0_fk_task_manager_graystatus_id` FOREIGN KEY (`current_status_id`) REFERENCES `task_manager_graystatus` (`id`),
  CONSTRAINT `task_manager_gr_creator_id_f82ce419_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `task_manager_graytask_image_id_1cd7470b_fk_common_image_image_id` FOREIGN KEY (`image_id`) REFERENCES `common_image` (`image_id`),
  CONSTRAINT `task_manager_graytasks_app_id_4ef1b40d_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_graytask`
--

LOCK TABLES `task_manager_graytask` WRITE;
/*!40000 ALTER TABLE `task_manager_graytask` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_graytask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_graytasklog`
--

DROP TABLE IF EXISTS `task_manager_graytasklog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_graytasklog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `update_log` longtext NOT NULL,
  `gray_task_id` int(11) NOT NULL,
  `operator_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `task_manager_graytasklog_c25832d1` (`gray_task_id`),
  KEY `task_manager_graytasklog_4d14a16b` (`operator_id`),
  CONSTRAINT `task_manager_g_gray_task_id_1544aa40_fk_task_manager_graytask_id` FOREIGN KEY (`gray_task_id`) REFERENCES `task_manager_graytask` (`id`),
  CONSTRAINT `task_manager_g_operator_id_71c895e2_fk_gated_launch_auth_user_id` FOREIGN KEY (`operator_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_graytasklog`
--

LOCK TABLES `task_manager_graytasklog` WRITE;
/*!40000 ALTER TABLE `task_manager_graytasklog` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_graytasklog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_graytaskrunstatus`
--

DROP TABLE IF EXISTS `task_manager_graytaskrunstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_graytaskrunstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `current_step` int(11) NOT NULL,
  `update_info` longtext NOT NULL,
  `gray_task_id` int(11) NOT NULL,
  `operator_id` int(11) NOT NULL,
  `task_status_id` int(11) NOT NULL,
  `current_step_name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `task_manager_graytaskrunstatus_c25832d1` (`gray_task_id`),
  KEY `task_manager_graytaskrunstatus_4d14a16b` (`operator_id`),
  KEY `task_manager_graytaskrunstatus_e49ec891` (`task_status_id`),
  CONSTRAINT `task_manag_task_status_id_69a47e4f_fk_task_manager_graystatus_id` FOREIGN KEY (`task_status_id`) REFERENCES `task_manager_graystatus` (`id`),
  CONSTRAINT `task_manager_g_gray_task_id_6176937c_fk_task_manager_graytask_id` FOREIGN KEY (`gray_task_id`) REFERENCES `task_manager_graytask` (`id`),
  CONSTRAINT `task_manager_g_operator_id_e952dce7_fk_gated_launch_auth_user_id` FOREIGN KEY (`operator_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_graytaskrunstatus`
--

LOCK TABLES `task_manager_graytaskrunstatus` WRITE;
/*!40000 ALTER TABLE `task_manager_graytaskrunstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_graytaskrunstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_snapshotinnerstrategy`
--

DROP TABLE IF EXISTS `task_manager_snapshotinnerstrategy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_snapshotinnerstrategy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `push_content` longtext NOT NULL,
  `index` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `gray_task_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `task_manager_snapshotinnerstrategy_app_id_2f3a1d4a_fk_app_app_id` (`app_id`),
  KEY `task_manager_sn_creator_id_88101001_fk_gated_launch_auth_user_id` (`creator_id`),
  KEY `task_manager_s_gray_task_id_d3e49926_fk_task_manager_graytask_id` (`gray_task_id`),
  CONSTRAINT `task_manager_s_gray_task_id_d3e49926_fk_task_manager_graytask_id` FOREIGN KEY (`gray_task_id`) REFERENCES `task_manager_graytask` (`id`),
  CONSTRAINT `task_manager_sn_creator_id_88101001_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `task_manager_snapshotinnerstrategy_app_id_2f3a1d4a_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_snapshotinnerstrategy`
--

LOCK TABLES `task_manager_snapshotinnerstrategy` WRITE;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_snapshotinnerstrategy_push_channels`
--

DROP TABLE IF EXISTS `task_manager_snapshotinnerstrategy_push_channels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_snapshotinnerstrategy_push_channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshotinnerstrategy_id` int(11) NOT NULL,
  `pushchannel_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_manager_snapshotinne_snapshotinnerstrategy_id_2c26abf3_uniq` (`snapshotinnerstrategy_id`,`pushchannel_id`),
  KEY `task_manager__pushchannel_id_af25528c_fk_strategy_pushchannel_id` (`pushchannel_id`),
  CONSTRAINT `D3d1534caf7facb11d97b4afb017bc26` FOREIGN KEY (`snapshotinnerstrategy_id`) REFERENCES `task_manager_snapshotinnerstrategy` (`id`),
  CONSTRAINT `task_manager__pushchannel_id_af25528c_fk_strategy_pushchannel_id` FOREIGN KEY (`pushchannel_id`) REFERENCES `strategy_pushchannel` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_snapshotinnerstrategy_push_channels`
--

LOCK TABLES `task_manager_snapshotinnerstrategy_push_channels` WRITE;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy_push_channels` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy_push_channels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_snapshotinnerstrategy_user_groups`
--

DROP TABLE IF EXISTS `task_manager_snapshotinnerstrategy_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_snapshotinnerstrategy_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshotinnerstrategy_id` int(11) NOT NULL,
  `usergroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_manager_snapshotinne_snapshotinnerstrategy_id_129459f8_uniq` (`snapshotinnerstrategy_id`,`usergroup_id`),
  KEY `task_manager_sn_usergroup_id_56a6211b_fk_user_group_usergroup_id` (`usergroup_id`),
  CONSTRAINT `D28a42fd94727402ec809f07be010246` FOREIGN KEY (`snapshotinnerstrategy_id`) REFERENCES `task_manager_snapshotinnerstrategy` (`id`),
  CONSTRAINT `task_manager_sn_usergroup_id_56a6211b_fk_user_group_usergroup_id` FOREIGN KEY (`usergroup_id`) REFERENCES `user_group_usergroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_snapshotinnerstrategy_user_groups`
--

LOCK TABLES `task_manager_snapshotinnerstrategy_user_groups` WRITE;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_snapshotinnerstrategy_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_manager_snapshotouterstrategy`
--

DROP TABLE IF EXISTS `task_manager_snapshotouterstrategy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task_manager_snapshotouterstrategy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(255) NOT NULL,
  `version` varchar(255) NOT NULL,
  `allow_users` longtext NOT NULL,
  `range_dates` varchar(2048) NOT NULL,
  `cities` varchar(1024) NOT NULL,
  `city_enable` tinyint(1) NOT NULL,
  `percentage` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `is_compatible` int(11) NOT NULL,
  `frequency` int(11) NOT NULL,
  `change_log` longtext NOT NULL,
  `change_log_img` varchar(200) NOT NULL,
  `index` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `gray_task_id` int(11) NOT NULL,
  `channels` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `task_manager_snapshotouterstrategy_app_id_c37272b7_fk_app_app_id` (`app_id`),
  KEY `task_manager_sn_creator_id_8438d7ca_fk_gated_launch_auth_user_id` (`creator_id`),
  KEY `task_manager_s_gray_task_id_a60e46d0_fk_task_manager_graytask_id` (`gray_task_id`),
  CONSTRAINT `task_manager_s_gray_task_id_a60e46d0_fk_task_manager_graytask_id` FOREIGN KEY (`gray_task_id`) REFERENCES `task_manager_graytask` (`id`),
  CONSTRAINT `task_manager_sn_creator_id_8438d7ca_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `task_manager_snapshotouterstrategy_app_id_c37272b7_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_manager_snapshotouterstrategy`
--

LOCK TABLES `task_manager_snapshotouterstrategy` WRITE;
/*!40000 ALTER TABLE `task_manager_snapshotouterstrategy` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_manager_snapshotouterstrategy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_usergroup`
--

DROP TABLE IF EXISTS `user_group_usergroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_usergroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(200) NOT NULL,
  `type_id` int(11) NOT NULL,
  `app_id` int(11) DEFAULT NULL,
  `creator_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_usergroup_app_id_63fc35ff_uniq` (`app_id`,`name`),
  KEY `user_group_usergroup_94757cae` (`type_id`),
  KEY `user_group_usergroup_f382adfe` (`app_id`),
  KEY `user_group_usergroup_3700153c` (`creator_id`),
  CONSTRAINT `user_group_user_creator_id_00f78012_fk_gated_launch_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `gated_launch_auth_user` (`id`),
  CONSTRAINT `user_group_userg_type_id_a2f20df2_fk_user_group_usergrouptype_id` FOREIGN KEY (`type_id`) REFERENCES `user_group_usergrouptype` (`id`),
  CONSTRAINT `user_group_usergroup_app_id_53dd5356_fk_app_app_id` FOREIGN KEY (`app_id`) REFERENCES `app_app` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergroup`
--

LOCK TABLES `user_group_usergroup` WRITE;
/*!40000 ALTER TABLE `user_group_usergroup` DISABLE KEYS */;
INSERT INTO `user_group_usergroup` VALUES (5,'2017-06-30 09:40:37.213744','2017-07-11 14:48:57.496885','changed_name',3,1,1),(6,'2017-06-30 11:52:12.937117','2017-06-30 14:22:44.670346','ffan_owner_group',4,1,1),(8,'2017-06-30 15:41:12.083570','2017-06-30 15:41:12.083707','angel4',3,1,7),(13,'2017-06-30 16:25:55.887988','2017-06-30 16:25:55.888121','custom',3,1,7),(15,'2017-07-05 15:44:34.971852','2017-07-05 15:44:34.971894','custom3',3,1,7),(16,'2017-07-05 16:37:45.254262','2017-07-05 16:37:45.254303','custom4',3,1,7),(17,'2017-07-10 16:25:07.095303','2017-07-10 16:25:07.095389','angel_group',1,1,7),(18,'2017-07-11 15:18:11.724793','2017-07-11 15:18:11.724841','company',2,NULL,6);
/*!40000 ALTER TABLE `user_group_usergroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_usergroup_members`
--

DROP TABLE IF EXISTS `user_group_usergroup_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_usergroup_members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usergroup_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_usergroup_users_usergroup_id_6aa8929a_uniq` (`usergroup_id`,`user_id`),
  KEY `user_group_usergro_user_id_881a60be_fk_gated_launch_auth_user_id` (`user_id`),
  CONSTRAINT `user_group_user_usergroup_id_5ab43e50_fk_user_group_usergroup_id` FOREIGN KEY (`usergroup_id`) REFERENCES `user_group_usergroup` (`id`),
  CONSTRAINT `user_group_usergro_user_id_881a60be_fk_gated_launch_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `gated_launch_auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergroup_members`
--

LOCK TABLES `user_group_usergroup_members` WRITE;
/*!40000 ALTER TABLE `user_group_usergroup_members` DISABLE KEYS */;
INSERT INTO `user_group_usergroup_members` VALUES (8,5,5),(9,5,8),(17,5,571),(4,6,7),(12,8,8),(14,17,8);
/*!40000 ALTER TABLE `user_group_usergroup_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_usergrouptype`
--

DROP TABLE IF EXISTS `user_group_usergrouptype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_usergrouptype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_usergrouptype_name_9d6b34ed_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_usergrouptype`
--

LOCK TABLES `user_group_usergrouptype` WRITE;
/*!40000 ALTER TABLE `user_group_usergrouptype` DISABLE KEYS */;
INSERT INTO `user_group_usergrouptype` VALUES (1,'2017-06-29 18:19:03.086248','2017-06-29 18:19:03.086288','angel'),(2,'2017-06-29 18:19:03.087124','2017-06-29 18:19:03.087153','company'),(3,'2017-06-29 18:19:03.087893','2017-06-29 18:19:03.087939','custom'),(4,'2017-06-29 18:19:05.093743','2017-06-29 18:19:05.093794','owner');
/*!40000 ALTER TABLE `user_group_usergrouptype` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-07-20 17:09:55
