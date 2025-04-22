-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 22, 2025 at 12:12 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_platinum_spa`
--

-- --------------------------------------------------------

--
-- Table structure for table `table_test`
--

CREATE TABLE `table_test` (
  `id` int(11) NOT NULL,
  `nama_barang` varchar(30) NOT NULL,
  `harga` int(11) NOT NULL,
  `ket` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `table_test`
--

INSERT INTO `table_test` (`id`, `nama_barang`, `harga`, `ket`) VALUES
(1, 'Paket Massage', 20000, 'Haihia'),
(2, 'Budi', 200000, 'Ini Test fastapi'),
(3, 'Budi', 200000, 'Ini Test fastapi'),
(4, 'Budi', 200000, 'Ini Test fastapi'),
(5, 'Budi', 200000, 'Ini Test fastapi'),
(6, 'Budi', 200000, 'Ini Test fastapi'),
(7, 'Budi', 200000, 'Ini Test fastapi'),
(8, 'Budaaa', 200000, 'Ini Test fastapi');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `table_test`
--
ALTER TABLE `table_test`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `table_test`
--
ALTER TABLE `table_test`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
