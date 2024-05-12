-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 12, 2024 at 09:54 AM
-- Server version: 8.3.0
-- PHP Version: 8.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `gamification`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('a65f284effd4');

-- --------------------------------------------------------

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
CREATE TABLE IF NOT EXISTS `course` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `course`
--

INSERT INTO `course` (`id`, `name`) VALUES
(1, 'Geography'),
(2, 'History');

-- --------------------------------------------------------

--
-- Table structure for table `quiz_question`
--

DROP TABLE IF EXISTS `quiz_question`;
CREATE TABLE IF NOT EXISTS `quiz_question` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question` varchar(255) NOT NULL,
  `option1` varchar(255) NOT NULL,
  `option2` varchar(255) NOT NULL,
  `option3` varchar(255) NOT NULL,
  `option4` varchar(255) NOT NULL,
  `correct_answer` int NOT NULL,
  `quiz_set_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `quiz_set_id` (`quiz_set_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `quiz_question`
--

INSERT INTO `quiz_question` (`id`, `question`, `option1`, `option2`, `option3`, `option4`, `correct_answer`, `quiz_set_id`) VALUES
(1, 'What is the tallest mountain in the world?', 'Denali', 'Mount Everest', 'Mount Cameroon', 'Aconcagua', 2, 1),
(2, 'What is the longest river in the world?', 'Darling River', 'Indus River', 'The Nile', 'Narmada River', 3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `quiz_set`
--

DROP TABLE IF EXISTS `quiz_set`;
CREATE TABLE IF NOT EXISTS `quiz_set` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `course_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `quiz_set`
--

INSERT INTO `quiz_set` (`id`, `name`, `course_id`) VALUES
(1, 'Geography Quiz One', 1),
(2, 'Geography Quiz Two', 1);

-- --------------------------------------------------------

--
-- Table structure for table `quiz_submission`
--

DROP TABLE IF EXISTS `quiz_submission`;
CREATE TABLE IF NOT EXISTS `quiz_submission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `quiz_set_id` int DEFAULT NULL,
  `quiz_question_id` int DEFAULT NULL,
  `given_answer` int NOT NULL,
  `is_correct_answer` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `quiz_set_id` (`quiz_set_id`),
  KEY `quiz_question_id` (`quiz_question_id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(200) NOT NULL,
  `last_name` varchar(200) NOT NULL,
  `username` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `role` varchar(50) NOT NULL,
  `date_added` datetime DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `first_name`, `last_name`, `username`, `email`, `role`, `date_added`, `password_hash`) VALUES
(1, 'Anindita', 'Podder', 'oni123', 'aninditapoddernitu@gmail.com', 'student', '2024-05-07 07:50:15', 'pbkdf2:sha256:600000$qMZ67eXgbzppiP6J$cd0dfabc46628f7a2ee06e51fab0b867b29797200f8f0cae1da951f3fd59b4de'),
(2, 'Test', 'Test02', 'test002', 'test02@gmail.com', 'student', '2024-05-07 08:56:59', 'pbkdf2:sha256:600000$F0n7XZt8xX0wK6ix$3f3e37f356042107b6ccef92e6adc48165fd2f54249761bce7385c3da893383f');

-- --------------------------------------------------------

--
-- Table structure for table `user_course`
--

DROP TABLE IF EXISTS `user_course`;
CREATE TABLE IF NOT EXISTS `user_course` (
  `user_id` int DEFAULT NULL,
  `course_id` int DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `course_id` (`course_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user_course`
--

INSERT INTO `user_course` (`user_id`, `course_id`) VALUES
(1, 1),
(1, 2);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
