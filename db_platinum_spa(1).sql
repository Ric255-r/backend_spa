-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 02, 2025 at 03:00 AM
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
-- Table structure for table `data_loker`
--

CREATE TABLE `data_loker` (
  `id_loker` int(2) NOT NULL,
  `nomor_locker` varchar(3) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = not occupied, 1 = occupied'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `data_loker`
--

INSERT INTO `data_loker` (`id_loker`, `nomor_locker`, `status`) VALUES
(50, '1', 1),
(51, '2', 1),
(52, '3', 1),
(53, '4', 1),
(54, '5', 1),
(55, '6', 1),
(56, '7', 1),
(57, '8', 1),
(58, '9', 1),
(59, '10', 1),
(60, '11', 1),
(61, '12', 1),
(62, '13', 1),
(63, '14', 1),
(64, '15', 1),
(65, '16', 0),
(66, '17', 0),
(67, '18', 0),
(68, '19', 0),
(69, '20', 0),
(70, '21', 0),
(71, '22', 0),
(72, '23', 0),
(73, '24', 0),
(74, '25', 0),
(75, '26', 0),
(76, '27', 0),
(77, '28', 0),
(78, '29', 0),
(79, '30', 0),
(80, '31', 0),
(81, '32', 0),
(82, '33', 0),
(83, '34', 0),
(84, '35', 0),
(85, '36', 0),
(86, '37', 0),
(87, '38', 0),
(88, '39', 0),
(89, '40', 0);

-- --------------------------------------------------------

--
-- Table structure for table `detail_promo_happyhour`
--

CREATE TABLE `detail_promo_happyhour` (
  `id` int(11) NOT NULL,
  `detail_kode_promo` varchar(6) NOT NULL,
  `senin` tinyint(1) NOT NULL DEFAULT 1,
  `selasa` tinyint(1) NOT NULL DEFAULT 1,
  `rabu` tinyint(1) NOT NULL DEFAULT 1,
  `kamis` tinyint(1) NOT NULL DEFAULT 1,
  `jumat` tinyint(1) NOT NULL DEFAULT 1,
  `sabtu` tinyint(1) NOT NULL DEFAULT 1,
  `minggu` tinyint(1) NOT NULL DEFAULT 1,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `disc` double NOT NULL COMMENT 'potongan harga',
  `member` tinyint(1) NOT NULL DEFAULT 1,
  `vip` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_promo_happyhour`
--

INSERT INTO `detail_promo_happyhour` (`id`, `detail_kode_promo`, `senin`, `selasa`, `rabu`, `kamis`, `jumat`, `sabtu`, `minggu`, `jam_mulai`, `jam_selesai`, `disc`, `member`, `vip`, `created_at`, `updated_at`) VALUES
(2, 'DP001', 1, 1, 1, 1, 1, 1, 1, '14:30:00', '15:30:00', 20, 1, 1, '2025-04-29 07:07:50', NULL),
(3, 'DP002', 1, 1, 1, 1, 1, 1, 1, '18:00:00', '20:00:00', 20, 1, 1, '2025-04-29 07:38:27', NULL),
(5, 'DP003', 1, 1, 1, 1, 1, 1, 1, '18:00:00', '20:00:00', 40, 1, 1, '2025-04-29 07:56:15', NULL),
(6, 'DP004', 1, 1, 1, 1, 1, 1, 1, '18:40:00', '20:40:00', 15, 1, 0, '2025-04-29 13:23:22', NULL),
(7, 'DP005', 1, 0, 1, 1, 0, 1, 0, '18:40:00', '21:40:00', 15, 1, 1, '2025-04-29 13:24:04', NULL),
(8, 'DP006', 1, 1, 0, 1, 0, 1, 0, '12:30:00', '21:40:00', 15, 1, 1, '2025-04-29 13:25:18', NULL),
(9, 'DP007', 1, 1, 1, 0, 1, 0, 1, '10:40:00', '22:00:00', 20, 0, 1, '2025-04-29 13:28:37', NULL),
(10, 'DP008', 1, 0, 1, 0, 1, 0, 1, '18:00:00', '22:00:00', 20, 1, 1, '2025-04-30 05:18:17', NULL),
(11, 'DP009', 1, 0, 1, 0, 0, 0, 0, '10:00:00', '20:00:00', 10, 1, 0, '2025-05-03 13:26:21', NULL),
(12, 'DP010', 1, 1, 1, 1, 1, 1, 1, '09:00:00', '22:00:00', 25, 1, 1, '2025-05-07 05:58:28', NULL),
(13, 'DP011', 1, 1, 1, 0, 0, 0, 0, '08:00:00', '16:00:00', 10, 0, 1, '2025-05-08 12:19:21', '2025-05-08 12:20:19');

-- --------------------------------------------------------

--
-- Table structure for table `detail_promo_kunjungan`
--

CREATE TABLE `detail_promo_kunjungan` (
  `id` int(11) NOT NULL,
  `detail_kode_promo` varchar(6) NOT NULL,
  `limit_kunjungan` int(2) NOT NULL,
  `harga_promo` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_promo_kunjungan`
--

INSERT INTO `detail_promo_kunjungan` (`id`, `detail_kode_promo`, `limit_kunjungan`, `harga_promo`, `created_at`, `updated_at`) VALUES
(2, 'DK001', 1, 1000000, '2025-04-30 05:31:10', '2025-05-07 06:42:35'),
(4, 'DK002', 15, 200000, '2025-04-30 05:45:02', NULL),
(5, 'DK003', 15, 200000, '2025-04-30 05:45:15', NULL),
(7, 'DK005', 1, 40000000, '2025-04-30 06:07:40', NULL),
(8, 'DK006', 15, 1500000, '2025-05-03 13:27:15', NULL),
(9, 'DK007', 20, 4000000, '2025-05-07 06:01:26', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `detail_promo_tahunan`
--

CREATE TABLE `detail_promo_tahunan` (
  `id` int(11) NOT NULL,
  `detail_kode_promo` varchar(6) NOT NULL,
  `jangka_tahun` int(1) NOT NULL,
  `harga_promo` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_promo_tahunan`
--

INSERT INTO `detail_promo_tahunan` (`id`, `detail_kode_promo`, `jangka_tahun`, `harga_promo`, `created_at`, `updated_at`) VALUES
(1, 'DT001', 2, 50000000, '2025-04-30 06:12:49', NULL),
(2, 'DT002', 1, 4500000, '2025-04-30 06:13:18', NULL),
(3, 'DT003', 2, 4000000, '2025-04-30 06:17:27', NULL),
(4, 'DT004', 2, 43000000, '2025-04-30 06:18:10', '2025-05-07 06:43:30'),
(5, 'DT005', 1, 2000000, '2025-05-03 13:28:32', NULL),
(6, 'DT006', 2, 2500000, '2025-05-07 06:02:05', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `detail_transaksi_fasilitas`
--

CREATE TABLE `detail_transaksi_fasilitas` (
  `id_detail_transaksi` varchar(30) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_fasilitas` varchar(6) NOT NULL,
  `qty` int(11) NOT NULL,
  `satuan` varchar(10) NOT NULL,
  `harga` int(11) NOT NULL,
  `status` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_transaksi_fasilitas`
--

INSERT INTO `detail_transaksi_fasilitas` (`id_detail_transaksi`, `id_transaksi`, `id_fasilitas`, `qty`, `satuan`, `harga`, `status`) VALUES
('DTcfabcd44e1cc4fb5', 'TF0004', 'F003', 1, 'Paket', 12300, 'paid');

-- --------------------------------------------------------

--
-- Table structure for table `detail_transaksi_fnb`
--

CREATE TABLE `detail_transaksi_fnb` (
  `id_detail_transaksi` varchar(30) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_fnb` varchar(6) DEFAULT NULL,
  `qty` int(11) NOT NULL,
  `satuan` varchar(10) NOT NULL,
  `harga_item` int(11) NOT NULL,
  `harga_total` int(11) NOT NULL,
  `status` varchar(12) DEFAULT NULL COMMENT 'unpaid, paid',
  `is_addon` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_transaksi_fnb`
--

INSERT INTO `detail_transaksi_fnb` (`id_detail_transaksi`, `id_transaksi`, `id_fnb`, `qty`, `satuan`, `harga_item`, `harga_total`, `status`, `is_addon`) VALUES
('DT186336dfa3f849c6', 'TF0007', 'F002', 2, 'PCS', 10000, 20000, 'paid', 1),
('DT964a69b4b7be4043', 'TF0005', 'F003', 3, 'PCS', 10000, 30000, NULL, 0),
('DTe6eebc4dd4a64455', 'TF0006', 'F003', 2, 'PCS', 10000, 20000, 'paid', 1);

-- --------------------------------------------------------

--
-- Table structure for table `detail_transaksi_member`
--

CREATE TABLE `detail_transaksi_member` (
  `id_detail_transaksi` varchar(30) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_member` varchar(10) NOT NULL,
  `kode_promo` varchar(6) NOT NULL,
  `harga_promo` int(11) NOT NULL,
  `status` varchar(12) NOT NULL,
  `sisa_kunjungan` int(11) DEFAULT NULL,
  `exp_kunjungan` date DEFAULT NULL,
  `exp_tahunan` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_transaksi_member`
--

INSERT INTO `detail_transaksi_member` (`id_detail_transaksi`, `id_transaksi`, `id_member`, `kode_promo`, `harga_promo`, `status`, `sisa_kunjungan`, `exp_kunjungan`, `exp_tahunan`, `created_at`, `updated_at`) VALUES
('DT8d4942c4bd2241b2', 'TF0057', 'MV001', 'THN123', 7500000, 'paid', NULL, NULL, '2026-06-01', '2025-06-01 06:06:15', NULL),
('DT43f8f5e4912b44cb', 'TF0058', 'MM008', 'PAK001', 73687500, 'paid', 13, '2026-06-01', NULL, '2025-06-01 06:50:15', NULL),
('DT523d4018d52444ab', 'TF0059', 'MM008', 'THN123', 7500000, 'paid', NULL, NULL, '2026-06-01', '2025-06-01 06:51:20', NULL),
('DT66392f29cde04834', 'TF0064', 'MV001', 'PAK002', 5625000, 'paid', 15, '2026-06-01', NULL, '2025-06-01 10:18:08', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `detail_transaksi_paket`
--

CREATE TABLE `detail_transaksi_paket` (
  `id_detail_transaksi` varchar(30) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_paket` varchar(11) DEFAULT NULL,
  `qty` int(11) NOT NULL,
  `satuan` varchar(12) NOT NULL,
  `durasi_awal` int(3) NOT NULL,
  `total_durasi` int(3) NOT NULL,
  `harga_item` int(11) NOT NULL,
  `harga_total` int(11) NOT NULL,
  `status` varchar(12) NOT NULL COMMENT 'unpaid, paid',
  `is_returned` tinyint(1) NOT NULL DEFAULT 0,
  `alasan_retur` text DEFAULT NULL,
  `replaced_by_id_detail` varchar(30) DEFAULT NULL,
  `is_addon` tinyint(1) NOT NULL COMMENT '0 = not, 1 addon'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_transaksi_paket`
--

INSERT INTO `detail_transaksi_paket` (`id_detail_transaksi`, `id_transaksi`, `id_paket`, `qty`, `satuan`, `durasi_awal`, `total_durasi`, `harga_item`, `harga_total`, `status`, `is_returned`, `alasan_retur`, `replaced_by_id_detail`, `is_addon`) VALUES
('DT11607d7600a743af', 'TF0001', 'M003', 1, 'Paket', 60, 60, 500000, 500000, 'retur', 1, 'ganti_paket', 'DTFE64318287CF424A', 0),
('DT2cd6583d811e4184', 'TF0006', 'M002', 2, 'Paket', 60, 120, 500000, 1000000, 'paid', 0, NULL, NULL, 1),
('DT5e7da4dc34fa431b', 'TF0006', 'M002', 2, 'Paket', 60, 120, 500000, 1000000, 'paid', 0, NULL, NULL, 0),
('DT8aad27bf53e6401b', 'TF0007', 'M002', 1, 'Paket', 60, 60, 500000, 500000, 'paid', 0, NULL, NULL, 1),
('DTa26e1a8bffc546d2', 'TF0002', 'M003', 1, 'Paket', 60, 60, 500000, 500000, 'paid', 0, NULL, NULL, 0),
('DTa9e9fc8cc6f749cc', 'TF0003', 'M003', 1, 'Paket', 60, 60, 500000, 500000, 'retur', 1, 'ganti_paket', 'DTD6F8DCBC371A4CE8', 0),
('DTbda4856f986e437b', 'TF0007', 'M002', 2, 'Paket', 60, 120, 500000, 1000000, 'paid', 0, NULL, NULL, 0),
('DTD6F8DCBC371A4CE8', 'TF0003', 'M011', 1, 'paket', 60, 60, 650000, 650000, 'paid', 0, NULL, NULL, 0),
('DTdb9722ca73b94148', 'TF0008', 'M002', 2, 'Paket', 60, 120, 500000, 1000000, 'paid', 0, NULL, NULL, 0),
('DTFE64318287CF424A', 'TF0001', 'M011', 1, 'paket', 60, 60, 650000, 650000, 'paid', 0, NULL, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `detail_transaksi_produk`
--

CREATE TABLE `detail_transaksi_produk` (
  `id_detail_transaksi` varchar(30) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_produk` varchar(11) DEFAULT NULL,
  `qty` int(11) NOT NULL,
  `satuan` varchar(12) NOT NULL,
  `durasi_awal` int(3) NOT NULL,
  `total_durasi` int(3) NOT NULL,
  `harga_item` int(11) NOT NULL,
  `harga_total` int(11) NOT NULL,
  `status` varchar(12) NOT NULL COMMENT 'unpaid, paid',
  `is_addon` tinyint(1) NOT NULL COMMENT '0 = not, 1 addon'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `detail_transaksi_produk`
--

INSERT INTO `detail_transaksi_produk` (`id_detail_transaksi`, `id_transaksi`, `id_produk`, `qty`, `satuan`, `durasi_awal`, `total_durasi`, `harga_item`, `harga_total`, `status`, `is_addon`) VALUES
('DT2351fe41e52f4fb2', 'TF0008', 'P003', 1, 'Pcs', 30, 30, 90000, 90000, 'paid', 0),
('DT4130f73311c04df1', 'TF0002', 'P001', 2, 'Pcs', 20, 40, 60000, 120000, 'paid', 1),
('DT42104f4605d8412c', 'TF0007', 'P008', 1, 'Pcs', 20, 20, 450000, 450000, 'paid', 0),
('DT6945cd2b967249d9', 'TF0006', 'P003', 1, 'Pcs', 30, 30, 90000, 90000, 'paid', 0),
('DT97976bfe800e46fe', 'TF0001', 'P007', 1, 'Pcs', 30, 30, 160000, 160000, 'paid', 0),
('DTcda40c7e445644d4', 'TF0003', 'P007', 1, 'Pcs', 30, 30, 160000, 160000, 'paid', 0),
('DTe8a54fb4bc43475a', 'TF0002', 'P001', 1, 'Pcs', 20, 20, 60000, 60000, 'paid', 0);

-- --------------------------------------------------------

--
-- Table structure for table `durasi_kerja_sementara`
--

CREATE TABLE `durasi_kerja_sementara` (
  `id` int(11) NOT NULL,
  `kode_ruangan` varchar(6) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `sum_durasi_menit` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `durasi_kerja_sementara`
--

INSERT INTO `durasi_kerja_sementara` (`id`, `kode_ruangan`, `id_transaksi`, `sum_durasi_menit`) VALUES
(1, 'KT001', 'TF0001', 78),
(2, 'KT002', 'TF0002', 120),
(3, 'KT004', 'TF0003', 89);

-- --------------------------------------------------------

--
-- Table structure for table `hak_akses`
--

CREATE TABLE `hak_akses` (
  `id` int(11) NOT NULL,
  `nama_hakakses` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hak_akses`
--

INSERT INTO `hak_akses` (`id`, `nama_hakakses`) VALUES
(1, 'admin'),
(2, 'owner'),
(3, 'resepsionis'),
(4, 'kitchen'),
(5, 'spv'),
(6, 'gro'),
(7, 'ruangan'),
(8, 'terapis'),
(9, 'ob');

-- --------------------------------------------------------

--
-- Table structure for table `hari_kerja_ob`
--

CREATE TABLE `hari_kerja_ob` (
  `id` int(10) NOT NULL,
  `kode_ob` varchar(10) NOT NULL,
  `senin` tinyint(1) NOT NULL,
  `selasa` tinyint(1) NOT NULL,
  `rabu` tinyint(1) NOT NULL,
  `kamis` tinyint(1) NOT NULL,
  `jumat` tinyint(1) NOT NULL,
  `sabtu` tinyint(1) NOT NULL,
  `minggu` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hari_kerja_ob`
--

INSERT INTO `hari_kerja_ob` (`id`, `kode_ob`, `senin`, `selasa`, `rabu`, `kamis`, `jumat`, `sabtu`, `minggu`) VALUES
(1, 'O001', 1, 1, 1, 0, 0, 0, 1),
(2, 'O002', 0, 1, 0, 1, 0, 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `hari_kerja_terapis`
--

CREATE TABLE `hari_kerja_terapis` (
  `id` int(10) NOT NULL,
  `kode_terapis` varchar(10) NOT NULL,
  `senin` tinyint(1) NOT NULL DEFAULT 0,
  `selasa` tinyint(1) NOT NULL DEFAULT 0,
  `rabu` tinyint(1) NOT NULL DEFAULT 0,
  `kamis` tinyint(1) NOT NULL DEFAULT 0,
  `jumat` tinyint(1) NOT NULL DEFAULT 0,
  `sabtu` tinyint(1) NOT NULL DEFAULT 0,
  `minggu` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hari_kerja_terapis`
--

INSERT INTO `hari_kerja_terapis` (`id`, `kode_terapis`, `senin`, `selasa`, `rabu`, `kamis`, `jumat`, `sabtu`, `minggu`) VALUES
(1, 'T001', 1, 0, 0, 0, 0, 0, 0),
(2, 'T002', 1, 0, 1, 1, 0, 0, 1),
(3, 'T003', 1, 0, 0, 1, 0, 1, 1),
(4, 'T004', 1, 0, 1, 0, 1, 0, 1),
(5, 'T005', 0, 0, 1, 0, 1, 0, 0),
(6, 'T004', 1, 0, 0, 1, 0, 0, 1),
(7, 'T001', 1, 1, 1, 1, 1, 1, 1),
(8, 'T002', 1, 1, 1, 1, 1, 1, 1),
(9, 'T003', 1, 1, 1, 1, 1, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `karyawan`
--

CREATE TABLE `karyawan` (
  `id_karyawan` varchar(10) NOT NULL,
  `nik` varchar(17) NOT NULL,
  `nama_karyawan` varchar(50) NOT NULL,
  `alamat` text NOT NULL,
  `umur` int(2) NOT NULL,
  `jk` varchar(10) NOT NULL,
  `no_hp` varchar(14) NOT NULL,
  `jabatan` varchar(20) NOT NULL,
  `status` varchar(30) DEFAULT NULL,
  `kontrak_img` text NOT NULL,
  `is_occupied` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'khusus buat terapis.\r\ndefault 0, 1 = occupied'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `karyawan`
--

INSERT INTO `karyawan` (`id_karyawan`, `nik`, `nama_karyawan`, `alamat`, `umur`, `jk`, `no_hp`, `jabatan`, `status`, `kontrak_img`, `is_occupied`) VALUES
('A001', '61718181818181', 'Rio', 'Jl Jeruju', 20, 'Laki-Laki', '08171717171', 'admin', 'Aktif', 'img/kontrak.png', 0),
('A003', '855885864717', 'adminsmxoms', 'jl kokomsn', 20, 'Perempuan', '0883565354', 'Admin', 'Aktif', 'img/kontrak.png', 0),
('G001', '74747475', 'Sdu', 'dffghhbnj', 12, 'Perempuan', '42425585', 'GRO', 'Aktif', 'img/kontrak.png', 0),
('G002', '1245675433', 'Desi', 'Jl. Siantan', 0, 'Perempuan', '23424234', 'GRO', 'Aktif', 'img/kontrak.png', 0),
('G003', '1232134213132', 'Putri', 'Jl. Pattimura', 0, 'Perempuan', '23131313133', 'GRO', 'Aktif', 'img/kontrak.png', 0),
('K001', '121212', 'Agus', 'Jl Tanray', 0, 'Laki-Laki', '12121212', 'Kitchen', 'Aktif', 'img/kontrak.png', 0),
('O001', '121212', 'rr', 'ghjjj', 0, 'Laki-Laki', '1212', 'Office Boy', 'Aktif', 'img/kontrak.png', 0),
('R001', '121212', 'Lala', 'Jl Tanray', 0, 'Laki-Laki', '12211212', 'Resepsionis', 'Non Aktif', 'img/kontrak.png', 0),
('R002', '20929392', 'Alvin', 'pontianak', 0, 'Laki-Laki', '983292', 'Resepsionis', 'Non Aktif', 'img/kontrak.png', 0),
('S001', '611202845625', 'Susi', 'jl. kikima', 18, 'Laki-Laki', '0855565752562', 'Supervisor', 'Non Aktif', 'img/kontrak.png', 0),
('S002', '1231314151414', 'Superrrr', 'ff', 0, 'Laki-Laki', '2131455213233', 'Supervisor', 'Aktif', 'img/kontrak.png', 0),
('T001', '123321313213', 'Yola', 'Jl. Harapan', 0, 'Perempuan', '21314214414', 'Terapis', 'Aktif', 'img/kontrak.png', 0),
('T002', '12313213123', 'Sasa', 'Jl. Purnama', 0, 'Perempuan', '324543234', 'Terapis', 'Aktif', 'img/kontrak.png', 1),
('T003', '5654325432', 'Lola', 'Jl. Setia budi', 0, 'Perempuan', '43525342525', 'Terapis', 'Aktif', 'img/kontrak.png', 0),
('T004', '5654325432', 'Budiana', 'Jl. Setia budi', 0, 'Perempuan', '43525342525', 'Terapis', 'Aktif', 'img/kontrak.png', 0);

-- --------------------------------------------------------

--
-- Table structure for table `karyawan_hakakses_tambahan`
--

CREATE TABLE `karyawan_hakakses_tambahan` (
  `id` int(11) NOT NULL,
  `id_karyawan` varchar(10) NOT NULL,
  `id_hak_akses` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `karyawan_hakakses_tambahan`
--

INSERT INTO `karyawan_hakakses_tambahan` (`id`, `id_karyawan`, `id_hak_akses`) VALUES
(2, 'A001', 2),
(8, 'R001', 2),
(9, 'K001', 3),
(10, 'A002', 3),
(11, 'G003', 4),
(12, 'S002', 1),
(13, 'S002', 3);

-- --------------------------------------------------------

--
-- Table structure for table `kategori_fnb`
--

CREATE TABLE `kategori_fnb` (
  `id_kategori` varchar(6) NOT NULL,
  `nama_kategori` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `kategori_fnb`
--

INSERT INTO `kategori_fnb` (`id_kategori`, `nama_kategori`, `created_at`) VALUES
('', 'mankann', '2025-04-28 05:06:28'),
('M001', 'kamina', '2025-04-28 04:46:19'),
('M002', 'nambali', '2025-04-28 04:46:50'),
('M003', 'lamona', '2025-04-28 04:47:05'),
('M004', 'manda', '2025-04-28 04:47:20'),
('M005', 'lamnak', '2025-04-28 04:47:29'),
('M006', 'mandilah', '2025-04-28 04:49:09'),
('M007', 'daripada', '2025-04-28 04:49:50'),
('M008', 'nanti', '2025-04-28 04:49:58'),
('M009', 'jika', '2025-04-28 04:51:17'),
('M010', 'baruah', '2025-04-28 04:51:44'),
('M011', 'daripadaa', '2025-04-28 04:51:56'),
('M012', 'nanti ye', '2025-04-28 04:52:12'),
('M013', 'okede', '2025-04-28 04:52:16'),
('M014', 'okede', '2025-04-28 04:52:27'),
('M015', 'siap', '2025-04-28 04:52:46'),
('M016', 'darii', '2025-04-28 04:53:32'),
('M017', 'mungkinkah', '2025-04-28 04:53:38'),
('M018', 'nabcia', '2025-04-28 04:54:11'),
('M019', 'bila', '2025-04-28 04:54:16'),
('M020', 'nanti', '2025-04-28 04:54:24'),
('M021', 'mungkinkah', '2025-04-28 04:54:29'),
('M022', 'aku', '2025-04-28 04:55:02'),
('M023', 'suka', '2025-04-28 04:55:06'),
('M024', 'Panassss', '2025-05-03 13:10:42');

-- --------------------------------------------------------

--
-- Table structure for table `kategori_produk`
--

CREATE TABLE `kategori_produk` (
  `id_kategori` varchar(6) NOT NULL,
  `nama_kategori` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `kategori_produk`
--

INSERT INTO `kategori_produk` (`id_kategori`, `nama_kategori`, `created_at`) VALUES
('K001', 'satu', '2025-04-27 09:31:21'),
('K002', 'dua', '2025-04-27 09:31:24');

-- --------------------------------------------------------

--
-- Table structure for table `kitchen`
--

CREATE TABLE `kitchen` (
  `id` int(5) NOT NULL,
  `id_transaksi` varchar(11) NOT NULL,
  `id_detail_transaksi` varchar(30) NOT NULL,
  `status_pesanan` varchar(20) NOT NULL,
  `is_addon` tinyint(1) DEFAULT 0,
  `jam_terima_psn` time NOT NULL,
  `jam_selesai_psn` time NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `id_batch` varchar(40) NOT NULL COMMENT 'utk pengelompokan di kitchen. misalkan dalam 1 waktu, konsumen mesan 3 item yg sama. maka dia didalam 1 id batch'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `kitchen`
--

INSERT INTO `kitchen` (`id`, `id_transaksi`, `id_detail_transaksi`, `status_pesanan`, `is_addon`, `jam_terima_psn`, `jam_selesai_psn`, `created_at`, `id_batch`) VALUES
(1, 'TF0005', 'DT964a69b4b7be4043', 'pending', 0, '00:00:00', '00:00:00', '2025-05-29 08:46:30', 'BA0001748508390514'),
(2, 'TF0006', 'DTe6eebc4dd4a64455', 'pending', 1, '00:00:00', '00:00:00', '2025-05-30 16:45:53', 'BA0001748623553810'),
(3, 'TF0007', 'DT186336dfa3f849c6', 'pending', 1, '00:00:00', '00:00:00', '2025-05-31 04:50:02', 'BA0001748667002158');

-- --------------------------------------------------------

--
-- Table structure for table `komisi`
--

CREATE TABLE `komisi` (
  `id` int(11) NOT NULL,
  `id_karyawan` int(11) NOT NULL,
  `id_transaksi` int(11) NOT NULL,
  `nominal_komisi` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `komisi`
--

INSERT INTO `komisi` (`id`, `id_karyawan`, `id_transaksi`, `nominal_komisi`, `created_at`) VALUES
(1, 0, 0, 1612000, '2025-05-30 16:45:58'),
(2, 0, 0, 1400000, '2025-05-31 04:50:09');

-- --------------------------------------------------------

--
-- Table structure for table `laporan_ob`
--

CREATE TABLE `laporan_ob` (
  `id_laporan` int(11) NOT NULL,
  `id_ruangan` int(2) NOT NULL,
  `id_karyawan` varchar(20) NOT NULL,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `laporan` text NOT NULL,
  `foto_laporan` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_solved` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = not solved, 1 = solved',
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `laporan_ob`
--

INSERT INTO `laporan_ob` (`id_laporan`, `id_ruangan`, `id_karyawan`, `jam_mulai`, `jam_selesai`, `laporan`, `foto_laporan`, `created_at`, `is_solved`, `updated_at`) VALUES
(1, 1, 'OB001', '20:01:44', '00:00:00', 'Ada masalah di shower kamar mandi, krannya tidak berfungsi dan mengeluarkan cairan asam yang melelehkan segala barang didekatnya', '', '2025-05-03 13:01:45', 0, NULL),
(3, 3, 'OB001', '16:56:00', '17:56:00', 'Ada masalah di shower kamar mandi, krannya tidak berfungsi dan mengeluarkan cairan asam yang melelehkan segala barang didekatnya', '', '2025-05-04 09:59:10', 0, NULL),
(5, 1, 'O001', '13:48:08', '13:48:54', 'gagaga', '[\"6a125679-3781-4541-a219-1f44b7567379.jpg\", \"f7bc964a-1fe5-4720-b4aa-7fefd72e822f.jpg\"]', '2025-05-07 06:48:09', 0, '2025-05-07 06:48:57'),
(6, 1, 'O001', '14:32:23', '14:33:02', 'jhhnhngng', '[\"992a491f-842c-4287-b246-602760eb9dff.jpg\"]', '2025-05-07 07:32:24', 0, '2025-05-07 07:33:03');

-- --------------------------------------------------------

--
-- Table structure for table `main_transaksi`
--

CREATE TABLE `main_transaksi` (
  `id_transaksi` varchar(6) NOT NULL,
  `no_loker` int(2) NOT NULL,
  `jenis_transaksi` varchar(50) NOT NULL COMMENT 'fnb, fasilitas, paket',
  `jenis_tamu` varchar(6) NOT NULL,
  `id_member` varchar(6) NOT NULL,
  `no_hp` int(4) NOT NULL,
  `nama_tamu` varchar(50) NOT NULL,
  `id_ruangan` int(2) NOT NULL COMMENT 'pk ruangan',
  `id_resepsionis` varchar(10) NOT NULL,
  `id_terapis` varchar(10) NOT NULL,
  `id_gro` varchar(10) NOT NULL,
  `total_harga` int(9) NOT NULL,
  `disc` double NOT NULL,
  `grand_total` int(10) NOT NULL,
  `total_addon` int(10) NOT NULL DEFAULT 0 COMMENT 'sum harga addon dari detail',
  `jenis_pembayaran` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 awal, 1 akhir',
  `metode_pembayaran` varchar(10) NOT NULL COMMENT 'cash, debit, qris',
  `nama_akun` varchar(20) DEFAULT NULL COMMENT 'nama akun bank cust',
  `no_rek` varchar(20) DEFAULT NULL COMMENT 'no rek cust',
  `nama_bank` varchar(20) DEFAULT NULL COMMENT 'bca mandiri dll',
  `jumlah_bayar` int(9) NOT NULL,
  `jumlah_kembalian` int(9) NOT NULL,
  `is_cancel` tinyint(1) NOT NULL DEFAULT 0,
  `is_delete` tinyint(1) NOT NULL DEFAULT 0,
  `sedang_dikerjakan` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'utk select dikamar terapis',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL,
  `status` enum('draft','unpaid','paid','done','done-unpaid-addon','done-unpaid') NOT NULL COMMENT '(draft, paid, unpaid, done). ini buat pas pilih jenis transaksi utk generate id_trans'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `main_transaksi`
--

INSERT INTO `main_transaksi` (`id_transaksi`, `no_loker`, `jenis_transaksi`, `jenis_tamu`, `id_member`, `no_hp`, `nama_tamu`, `id_ruangan`, `id_resepsionis`, `id_terapis`, `id_gro`, `total_harga`, `disc`, `grand_total`, `total_addon`, `jenis_pembayaran`, `metode_pembayaran`, `nama_akun`, `no_rek`, `nama_bank`, `jumlah_bayar`, `jumlah_kembalian`, `is_cancel`, `is_delete`, `sedang_dikerjakan`, `created_at`, `updated_at`, `status`) VALUES
('TF0001', 8, 'massage', 'Umum', '', 212, 'Ricardo', 1, 'R001', 'T001', 'G001', 810000, 0.2, 648000, 0, 0, 'cash', NULL, NULL, NULL, 648000, 0, 0, 0, 0, '2025-05-24 10:24:50', NULL, 'done'),
('TF0002', 13, 'massage', 'Umum', '', 1231, 'Ricardo', 2, 'R001', 'T002', 'G001', 560000, 0, 680000, 0, 0, 'cash', NULL, NULL, NULL, 680000, 0, 0, 0, 0, '2025-05-24 13:28:01', NULL, 'done'),
('TF0003', 7, 'massage', 'Umum', '', 1212, 'Ricardo', 4, 'R001', 'T003', 'G002', 810000, 0.2, 648000, 0, 1, '-', NULL, NULL, NULL, 648000, 0, 0, 0, 0, '2025-05-25 13:58:23', NULL, 'done'),
('TF0004', 12, 'fasilitas', 'Umum', '', 0, '', 0, 'R001', '', '', 12300, 0, 12300, 0, 0, 'cash', NULL, NULL, NULL, 15000, 2700, 0, 0, 0, '2025-05-25 11:28:21', NULL, 'paid'),
('TF0005', -1, 'fnb', 'Member', '', 1212, 'Ricardo', 0, 'R001', '', '', 30000, 0.15, 25500, 0, 0, 'cash', NULL, NULL, NULL, 30000, 4500, 0, 0, 0, '2025-05-29 08:46:08', NULL, 'paid'),
('TF0006', 14, 'massage', 'Umum', '', 1212, 'Ricardo', 2, 'R001', 'T002', 'G001', 1090000, 0.2, 1892000, 0, 0, 'cash', NULL, NULL, NULL, 1892000, 0, 0, 0, 0, '2025-05-30 16:44:28', NULL, 'done'),
('TF0007', 15, 'massage', 'Member', '', 212, 'Ricard', 2, 'R001', 'T002', 'G001', 1450000, 0.2, 1576000, 0, 1, '-', NULL, NULL, NULL, 1576000, 0, 0, 0, 0, '2025-05-31 04:48:54', NULL, 'done'),
('TF0008', 11, 'massage', 'Umum', '', 1212, 'Ricardo', 1, 'R001', 'T002', 'G001', 1090000, 0.2, 872000, 0, 0, 'cash', NULL, NULL, NULL, 900000, 28000, 0, 0, 0, '2025-06-01 06:25:57', NULL, 'paid');

-- --------------------------------------------------------

--
-- Table structure for table `member`
--

CREATE TABLE `member` (
  `id_member` varchar(6) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `no_hp` int(4) NOT NULL,
  `status` varchar(10) NOT NULL,
  `id_sidikjari` text NOT NULL,
  `id_gelang` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `member`
--

INSERT INTO `member` (`id_member`, `nama`, `no_hp`, `status`, `id_sidikjari`, `id_gelang`, `created_at`, `updated_at`) VALUES
('R001', 'Ricardo', 4673, 'Member', '', '', '2025-04-25 05:51:09', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `menu_fnb`
--

CREATE TABLE `menu_fnb` (
  `id_fnb` varchar(6) NOT NULL,
  `id_kategori` varchar(6) NOT NULL,
  `nama_fnb` varchar(50) NOT NULL,
  `harga_fnb` int(8) NOT NULL,
  `status_fnb` varchar(20) NOT NULL COMMENT 'unavailable dan available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_fnb`
--

INSERT INTO `menu_fnb` (`id_fnb`, `id_kategori`, `nama_fnb`, `harga_fnb`, `status_fnb`) VALUES
('F002', 'M016', 'Keju panaskalicok', 10000, 'Available'),
('F003', 'M023', 'Keju', 10000, 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `menu_produk`
--

CREATE TABLE `menu_produk` (
  `id_produk` varchar(6) NOT NULL,
  `nama_produk` varchar(50) NOT NULL,
  `harga_produk` int(8) NOT NULL,
  `durasi` int(3) NOT NULL,
  `tipe_komisi` tinyint(4) NOT NULL DEFAULT 0 COMMENT 'o=persen, 1=nominal',
  `nominal_komisi` int(10) NOT NULL,
  `tipe_komisi_gro` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1=nominal. 0=persenan',
  `nominal_komisi_gro` int(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_produk`
--

INSERT INTO `menu_produk` (`id_produk`, `nama_produk`, `harga_produk`, `durasi`, `tipe_komisi`, `nominal_komisi`, `tipe_komisi_gro`, `nominal_komisi_gro`, `created_at`, `updated_at`) VALUES
('P001', 'Lilinaka', 60000, 20, 1, 20000, 0, 0, '2025-04-26 14:11:49', '2025-04-26 14:11:49'),
('P002', 'blabala', 1010101, 12, 0, 0, 0, 0, '2025-04-26 14:37:56', '2025-04-26 14:37:56'),
('P003', 'lamaona', 90000, 30, 1, 12000, 0, 0, '2025-04-28 05:47:29', '2025-04-28 05:47:29'),
('P004', 'manaka', 95000, 40, 0, 10, 0, 0, '2025-04-28 05:47:41', '2025-04-28 05:47:41'),
('P006', 'alaman', 15000, 40, 0, 40, 0, 0, '2025-04-28 08:21:58', '2025-04-28 08:21:58'),
('P007', 'malikan', 160000, 30, 1, 30, 0, 0, '2025-04-28 08:23:53', '2025-04-28 08:23:53'),
('P008', 'Jimanaka', 450000, 20, 1, 200000, 0, 20, '2025-05-25 08:27:53', '2025-05-25 08:27:53'),
('P009', 'Jimbolon', 550000, 30, 1, 25000, 1, 45000, '2025-05-25 08:28:31', '2025-05-25 08:28:31'),
('P010', 'Pelinama', 450000, 50, 1, 34000, 0, 10, '2025-05-25 08:30:19', '2025-05-25 08:30:19'),
('P011', 'Kalimana', 500000, 30, 0, 30, 2, 15000, '2025-05-25 08:31:36', '2025-05-25 08:31:36'),
('P012', 'Jaliman', 340000, 20, 0, 36000, 1, 15000, '2025-05-25 08:33:37', '2025-05-25 08:33:37'),
('P013', 'Kalomandan', 60000, 50, 1, 5000, 1, 3000, '2025-05-25 08:35:28', '2025-05-25 08:35:28'),
('P014', 'Mindalakan', 755000, 60, 1, 650000, 1, 20000, '2025-05-25 08:35:59', '2025-05-25 08:35:59');

-- --------------------------------------------------------

--
-- Table structure for table `paket_fasilitas`
--

CREATE TABLE `paket_fasilitas` (
  `id_fasilitas` varchar(5) NOT NULL,
  `nama_fasilitas` varchar(50) NOT NULL,
  `harga_fasilitas` int(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paket_fasilitas`
--

INSERT INTO `paket_fasilitas` (`id_fasilitas`, `nama_fasilitas`, `harga_fasilitas`) VALUES
('F001', 'Platinum Health Facilities', 200000),
('F002', 'kalomanin', 15000),
('F003', 'lapoman', 12300),
('F004', 'lapomin', 150000),
('F005', 'monakalaom', 300000),
('F006', 'asadfa', 13455),
('F007', 'asdad', 2123);

-- --------------------------------------------------------

--
-- Table structure for table `paket_massage`
--

CREATE TABLE `paket_massage` (
  `id_paket_msg` varchar(6) NOT NULL,
  `nama_paket_msg` varchar(50) NOT NULL,
  `harga_paket_msg` int(8) NOT NULL,
  `durasi` int(3) NOT NULL,
  `tipe_komisi` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0=persen, 1=nominal, Tipe Komisi Terapis',
  `nominal_komisi` int(10) NOT NULL COMMENT 'Nominal Komisi Terapis',
  `tipe_komisi_gro` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = persenan, 1 = nominal',
  `nominal_komisi_gro` int(10) NOT NULL,
  `detail_paket` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paket_massage`
--

INSERT INTO `paket_massage` (`id_paket_msg`, `nama_paket_msg`, `harga_paket_msg`, `durasi`, `tipe_komisi`, `nominal_komisi`, `tipe_komisi_gro`, `nominal_komisi_gro`, `detail_paket`) VALUES
('M001', 'paket holiday', 150000025, 60, 0, 50, 0, 0, 'Include Facilities'),
('M002', 'Paket Sejahteramana', 500000, 60, 1, 400000, 0, 0, 'Include all facility'),
('M003', 'kalomania', 500000, 60, 0, 45, 0, 0, 'paket kalungian'),
('M004', 'paket bajinurakaloman', 4000000, 60, 1, 400000, 0, 0, 'paket alamanaka'),
('M005', 'paket doakdkawdkal', 15000000, 30, 1, 15000, 0, 0, 'emdwkodkewkkd'),
('M006', 'paket lontong', 6550000, 30, 1, 150000, 0, 0, 'okeodkweodowek'),
('M007', 'pasoaodkaosdoak', 150000000, 30, 1, 1500000, 0, 0, 'weifowkowfkwoefow'),
('M008', 'lasmladamaldk', 5000000, 40, 1, 150000, 0, 0, 'eeeodwkowkokdeo'),
('M009', 'asokdpakdoaodoak', 6000000, 60, 1, 1500000, 0, 0, 'eidwkodeowfowefokwe'),
('M010', 'as,daldmsaldml', 200003000, 80, 1, 2147483647, 0, 0, 'dodskpkpodkopfwekpewf'),
('M011', 'aksdjqwjwqji', 650000, 60, 1, 1450000, 0, 0, 'ieediwkdwedekwok'),
('M012', 'poliaamam', 6500000, 30, 1, 75000, 0, 0, 'ejfjwifwjeifwjofj'),
('M013', 'Paket Haji', 55000000, 90, 1, 125000, 1, 45000, 'kosefiodjofjsioefj'),
('M014', 'askmlsaald', 76797987, 45, 1, 135000, 1, 25000, 'idiwjifwiejfiwjiwej'),
('M015', 'Pijat plus plus', 700000, 60, 1, 100000, 0, 10, 'nsisjis'),
('M016', 'Paket Labina', 500000, 60, 1, 200000, 0, 20, 'Paket Berkualitas'),
('M017', 'Paket Nimbolom', 50000000, 60, 0, 20, 0, 15, 'Paket Mantap'),
('M018', 'Paket Oloman', 550000, 60, 0, 25, 1, 150000, 'Paket Lomanan'),
('M019', 'Paket Jamail', 350000, 60, 1, 150000, 0, 20, 'Paket Berkualitas Tinggi');

-- --------------------------------------------------------

--
-- Table structure for table `promo`
--

CREATE TABLE `promo` (
  `kode_promo` varchar(6) NOT NULL,
  `nama_promo` varchar(50) NOT NULL,
  `kode_detail_promo` varchar(6) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `promo`
--

INSERT INTO `promo` (`kode_promo`, `nama_promo`, `kode_detail_promo`, `created_at`, `updated_at`) VALUES
('12345t', 'paket tahunan keren', 'DT005', '2025-05-03 13:28:32', NULL),
('123Pak', 'paket keren', 'DK006', '2025-05-03 13:27:15', NULL),
('b1t001', 'happy deals c', 'DP004', '2025-04-29 13:23:22', NULL),
('b2001', 'promo kunjungan kesayangan', 'DK001', '2025-04-30 05:31:10', '2025-05-07 06:42:35'),
('b4001', 'wodkaokdoak', 'DK002', '2025-04-30 05:45:02', NULL),
('b40012', 'wodkaokdoak', 'DK003', '2025-04-30 05:45:15', NULL),
('bc00', 'adaksd', 'DT002', '2025-04-30 06:13:18', NULL),
('bc003', 'adaksd', 'DT001', '2025-04-30 06:12:49', NULL),
('bk001', 'adaksd', 'DT004', '2025-04-30 06:18:10', '2025-05-07 06:43:30'),
('bl003', 'adaksd', 'DT003', '2025-04-30 06:17:27', NULL),
('C001', 'happy deals aa', 'DP006', '2025-04-29 13:25:18', NULL),
('K001', 'happy deals aa', 'DP005', '2025-04-29 13:24:04', NULL),
('K010', 'Paket Promo Happy Hour', 'DP011', '2025-05-08 12:19:21', '2025-05-08 12:20:19'),
('lasdka', 'dksafskjfsd', 'DP008', '2025-04-30 05:18:17', NULL),
('P001', 'Happy Hour Deal', 'DP002', '2025-04-29 07:38:27', NULL),
('P002', 'Happy Hour Deala', 'DP003', '2025-04-29 07:39:48', NULL),
('P003', 'Happy Hour Deal Goodjob', 'DP003', '2025-04-29 07:56:15', NULL),
('PK001', 'Promo makima', 'DT006', '2025-05-07 06:02:05', NULL),
('PL002', 'Promo Lakina', 'DP010', '2025-05-07 05:58:28', NULL),
('Promo1', 'promo keren', 'DP009', '2025-05-03 13:26:21', NULL),
('PT001', 'Promo kalima', 'DK007', '2025-05-07 06:01:26', NULL),
('v0001', 'happy happy deal', 'DP007', '2025-04-29 13:28:37', NULL),
('wewe00', 'promo tahunan 1', 'DK005', '2025-04-30 06:07:40', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `ruangan`
--

CREATE TABLE `ruangan` (
  `id_ruangan` int(2) NOT NULL,
  `id_karyawan` varchar(20) NOT NULL COMMENT 'ini relasi ke tabel users',
  `nama_ruangan` varchar(20) NOT NULL,
  `lantai` int(2) NOT NULL,
  `jenis_ruangan` varchar(12) NOT NULL,
  `status` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ruangan`
--

INSERT INTO `ruangan` (`id_ruangan`, `id_karyawan`, `nama_ruangan`, `lantai`, `jenis_ruangan`, `status`) VALUES
(1, 'KT001', 'Reg-01', 1, 'Reguler', 'occupied'),
(2, 'KT002', 'Reg-02', 1, 'Reguler', 'maintenanc'),
(3, 'KT003', 'Vip-01', 2, 'VIP', 'aktif'),
(4, 'KT004', 'Reg-03', 1, 'Reguler', 'aktif');

-- --------------------------------------------------------

--
-- Table structure for table `ruang_tunggu`
--

CREATE TABLE `ruang_tunggu` (
  `id` int(11) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_terapis` varchar(10) NOT NULL,
  `nama_terapis` varchar(50) NOT NULL,
  `nama_ruangan` varchar(20) NOT NULL,
  `jam_terima` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ruang_tunggu`
--

INSERT INTO `ruang_tunggu` (`id`, `id_transaksi`, `id_terapis`, `nama_terapis`, `nama_ruangan`, `jam_terima`) VALUES
(1, 'tf001', 'T004', 'yuni', 'TEG-00', '2025-05-11 09:24:19'),
(2, 'TF0033', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 09:26:59'),
(3, 'TF0035', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 10:52:33'),
(4, 'TF0036', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 11:16:37'),
(5, 'TF0037', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 11:29:31'),
(6, 'TF0038', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 12:02:17'),
(7, 'TF0039', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 13:00:05'),
(8, 'TF0040', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 13:02:55'),
(9, 'TF0041', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 13:06:07'),
(10, 'TF0042', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 13:12:49'),
(11, 'TF0043', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 13:19:46'),
(12, 'TF0044', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 13:26:02'),
(13, 'TF0045', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 13:32:53'),
(14, 'TF0046', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 13:51:43'),
(15, 'TF0047', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 13:53:52'),
(16, 'TF0048', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 13:55:56'),
(17, 'TF0049', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 13:58:44'),
(18, 'TF0050', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:06:00'),
(19, 'TF0051', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:08:18'),
(20, 'TF0052', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:09:45'),
(21, 'TF0054', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 14:14:06'),
(22, 'TF0055', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:14:53'),
(23, 'TF0056', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:20:53'),
(24, 'TF0057', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 14:22:35'),
(25, 'TF0058', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:25:50'),
(26, 'TF0059', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 14:26:29'),
(27, 'TF0060', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:27:44'),
(28, 'TF0061', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:29:04'),
(29, 'TF0062', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 14:32:36'),
(30, 'TF0063', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:35:08'),
(31, 'TF0064', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:36:22'),
(32, 'TF0065', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:40:10'),
(33, 'TF0066', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 14:46:06'),
(34, 'TF0067', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 14:47:29'),
(35, 'TF0068', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 14:50:26'),
(36, '', '', '', '', '2025-05-11 14:55:45'),
(37, 'TF0071', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 15:02:10'),
(38, 'TF0072', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 15:04:59'),
(39, 'TF0073', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 15:06:59'),
(40, 'TF0074', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 15:17:18'),
(41, 'TF0075', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 15:19:09'),
(42, 'TF0076', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 15:20:31'),
(43, 'TF0077', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 15:21:22'),
(44, 'TF0078', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 15:24:26'),
(45, 'TF0079', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 15:26:19'),
(46, 'TF0080', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 15:30:21'),
(47, 'TF0081', 'T002', 'GERINA', 'Room Reg-01', '2025-05-11 15:38:18'),
(48, 'TF0083', 'T001', 'Yuni', 'Room Reg-01', '2025-05-11 15:43:30'),
(49, 'TF0084', 'T003', 'naruto', 'Room Reg-01', '2025-05-11 15:44:09'),
(50, 'TF0086', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 05:48:54'),
(51, 'TF0087', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 06:54:53'),
(52, 'TF0088', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 06:56:20'),
(53, 'TF0089', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 06:57:41'),
(54, 'TF0090', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 06:59:25'),
(55, 'TF0091', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:03:37'),
(56, 'TF0092', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:05:15'),
(57, 'TF0093', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:08:41'),
(58, 'TF0094', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:13:16'),
(59, 'TF0095', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:14:54'),
(60, 'TF0096', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:17:04'),
(61, 'TF0097', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:18:59'),
(62, 'TF0098', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:20:01'),
(63, 'TF0099', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:26:43'),
(64, 'TF0100', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:27:46'),
(65, 'TF0101', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:30:06'),
(66, 'TF0102', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:32:15'),
(67, 'TF0103', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:35:28'),
(68, 'TF0104', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:36:23'),
(69, 'TF0105', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:44:24'),
(70, 'TF0106', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:45:13'),
(71, 'TF0107', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:46:13'),
(72, 'TF0108', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:47:32'),
(73, 'TF0109', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 07:49:08'),
(74, 'TF0110', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 07:49:33'),
(75, 'TF0111', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:52:11'),
(76, 'TF0112', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 07:53:51'),
(77, 'TF0113', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 08:00:17'),
(78, 'TF0114', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 08:01:05'),
(79, 'TF0115', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 08:02:31'),
(80, 'TF0116', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 08:03:05'),
(81, 'TF0117', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 08:03:32'),
(82, 'TF0118', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 08:49:05'),
(83, 'TF0119', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 08:49:43'),
(84, 'TF0120', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 08:56:17'),
(85, 'TF0121', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 08:59:39'),
(86, 'TF0122', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 09:01:41'),
(87, 'TF0123', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 09:15:23'),
(88, 'TF0124', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 09:23:45'),
(89, 'TF0125', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 09:24:24'),
(90, 'TF0126', 'T003', 'naruto', 'Room Reg-01', '2025-05-12 09:25:26'),
(91, 'TF0127', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 09:37:12'),
(92, 'TF0128', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 09:42:30'),
(93, 'TF0129', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 09:43:09'),
(94, 'TF0140', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:03:51'),
(95, 'TF0141', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:04:53'),
(96, 'TF0142', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:08:53'),
(97, 'TF0143', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:09:19'),
(98, 'TF0144', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:12:10'),
(99, 'TF0145', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:13:39'),
(100, 'TF0147', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 11:18:13'),
(101, 'TF0148', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:22:10'),
(102, 'TF0149', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:22:41'),
(103, 'TF0150', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:24:48'),
(104, 'TF0151', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:27:08'),
(105, 'TF0152', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:27:29'),
(106, 'TF0153', 'T002', 'GERINA', 'Room Reg-01', '2025-05-12 11:28:01'),
(107, 'TF0154', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:28:49'),
(108, 'TF0155', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:46:32'),
(109, 'TF0156', 'T001', 'Yuni', 'Room Reg-01', '2025-05-12 11:48:17');

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

-- --------------------------------------------------------

--
-- Table structure for table `terapis_kerja`
--

CREATE TABLE `terapis_kerja` (
  `id` int(11) NOT NULL,
  `id_transaksi` varchar(6) NOT NULL,
  `id_terapis` varchar(6) NOT NULL,
  `jam_datang` time NOT NULL,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `alasan` text DEFAULT NULL COMMENT 'diisi klo selesai lebih cepat',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `is_tunda` tinyint(1) NOT NULL DEFAULT 0,
  `is_cancel` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `terapis_kerja`
--

INSERT INTO `terapis_kerja` (`id`, `id_transaksi`, `id_terapis`, `jam_datang`, `jam_mulai`, `jam_selesai`, `alasan`, `created_at`, `is_tunda`, `is_cancel`) VALUES
(3, 'TF0001', 'T001', '13:53:06', '14:25:37', '00:00:00', NULL, '2025-05-24 06:53:09', 1, 0),
(4, 'TF0002', 'T002', '20:29:53', '20:29:53', '00:00:00', NULL, '2025-05-24 13:29:54', 1, 0),
(5, 'TF0003', 'T003', '20:59:27', '20:59:28', '00:00:00', NULL, '2025-05-24 13:59:28', 1, 0),
(6, 'TF0006', 'T002', '23:19:53', '23:19:54', '23:45:59', 'Atas_Permintaan_Tamu', '2025-05-30 16:45:16', 0, 0),
(7, 'TF0007', 'T002', '11:49:43', '11:49:44', '11:50:10', 'Atas_Permintaan_Tamu', '2025-05-31 04:49:46', 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id_karyawan` varchar(20) NOT NULL,
  `passwd` varchar(50) NOT NULL,
  `hak_akses` varchar(20) NOT NULL COMMENT 'hak akses ori utk tembak ke UI.\r\nini isinya id dr tbl hak akses',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id_karyawan`, `passwd`, `hak_akses`, `created_at`, `updated_at`) VALUES
('A001', '123', '1', '2025-04-23 10:36:50', NULL),
('G003', '1234', '8', '2025-05-08 12:22:50', NULL),
('K001', '1212', '4', '2025-05-06 15:10:06', NULL),
('KT001', '1234', '7', '2025-05-08 10:56:36', NULL),
('KT002', '1234', '7', '2025-05-08 11:00:13', NULL),
('KT003', '1234', '7', '2025-05-08 11:00:13', NULL),
('KT004', '1234', '7', '2025-05-08 11:00:13', NULL),
('O001', '1234', '9', '2025-05-07 06:47:11', NULL),
('OW001', '1234', '2', '2025-05-08 10:52:50', NULL),
('R001', '1234', '3', '2025-05-06 13:40:48', NULL),
('S002', '1234', '5', '2025-05-10 09:02:29', NULL),
('T001', '1234', '8', '2025-05-08 10:52:40', NULL),
('T002', '1234', '8', '2025-05-08 10:52:50', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `waiting_room_terapis`
--

CREATE TABLE `waiting_room_terapis` (
  `id` int(11) NOT NULL,
  `id_transaksi` int(11) NOT NULL,
  `jam_konfirmasi` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `data_loker`
--
ALTER TABLE `data_loker`
  ADD PRIMARY KEY (`id_loker`);

--
-- Indexes for table `detail_promo_happyhour`
--
ALTER TABLE `detail_promo_happyhour`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `detail_promo_kunjungan`
--
ALTER TABLE `detail_promo_kunjungan`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `detail_promo_tahunan`
--
ALTER TABLE `detail_promo_tahunan`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `detail_transaksi_fnb`
--
ALTER TABLE `detail_transaksi_fnb`
  ADD PRIMARY KEY (`id_detail_transaksi`);

--
-- Indexes for table `detail_transaksi_paket`
--
ALTER TABLE `detail_transaksi_paket`
  ADD PRIMARY KEY (`id_detail_transaksi`);

--
-- Indexes for table `detail_transaksi_produk`
--
ALTER TABLE `detail_transaksi_produk`
  ADD PRIMARY KEY (`id_detail_transaksi`);

--
-- Indexes for table `durasi_kerja_sementara`
--
ALTER TABLE `durasi_kerja_sementara`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hak_akses`
--
ALTER TABLE `hak_akses`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hari_kerja_ob`
--
ALTER TABLE `hari_kerja_ob`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `hari_kerja_terapis`
--
ALTER TABLE `hari_kerja_terapis`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `karyawan`
--
ALTER TABLE `karyawan`
  ADD PRIMARY KEY (`id_karyawan`);

--
-- Indexes for table `karyawan_hakakses_tambahan`
--
ALTER TABLE `karyawan_hakakses_tambahan`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `kategori_fnb`
--
ALTER TABLE `kategori_fnb`
  ADD PRIMARY KEY (`id_kategori`);

--
-- Indexes for table `kategori_produk`
--
ALTER TABLE `kategori_produk`
  ADD PRIMARY KEY (`id_kategori`);

--
-- Indexes for table `kitchen`
--
ALTER TABLE `kitchen`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `komisi`
--
ALTER TABLE `komisi`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `laporan_ob`
--
ALTER TABLE `laporan_ob`
  ADD PRIMARY KEY (`id_laporan`);

--
-- Indexes for table `main_transaksi`
--
ALTER TABLE `main_transaksi`
  ADD PRIMARY KEY (`id_transaksi`,`no_loker`);

--
-- Indexes for table `member`
--
ALTER TABLE `member`
  ADD PRIMARY KEY (`id_member`);

--
-- Indexes for table `menu_fnb`
--
ALTER TABLE `menu_fnb`
  ADD PRIMARY KEY (`id_fnb`);

--
-- Indexes for table `menu_produk`
--
ALTER TABLE `menu_produk`
  ADD PRIMARY KEY (`id_produk`);

--
-- Indexes for table `paket_fasilitas`
--
ALTER TABLE `paket_fasilitas`
  ADD PRIMARY KEY (`id_fasilitas`);

--
-- Indexes for table `paket_massage`
--
ALTER TABLE `paket_massage`
  ADD PRIMARY KEY (`id_paket_msg`);

--
-- Indexes for table `promo`
--
ALTER TABLE `promo`
  ADD PRIMARY KEY (`kode_promo`);

--
-- Indexes for table `ruangan`
--
ALTER TABLE `ruangan`
  ADD PRIMARY KEY (`id_ruangan`);

--
-- Indexes for table `ruang_tunggu`
--
ALTER TABLE `ruang_tunggu`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `table_test`
--
ALTER TABLE `table_test`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `terapis_kerja`
--
ALTER TABLE `terapis_kerja`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_karyawan`);

--
-- Indexes for table `waiting_room_terapis`
--
ALTER TABLE `waiting_room_terapis`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `data_loker`
--
ALTER TABLE `data_loker`
  MODIFY `id_loker` int(2) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=90;

--
-- AUTO_INCREMENT for table `detail_promo_happyhour`
--
ALTER TABLE `detail_promo_happyhour`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `detail_promo_kunjungan`
--
ALTER TABLE `detail_promo_kunjungan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `detail_promo_tahunan`
--
ALTER TABLE `detail_promo_tahunan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `durasi_kerja_sementara`
--
ALTER TABLE `durasi_kerja_sementara`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `hak_akses`
--
ALTER TABLE `hak_akses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `hari_kerja_ob`
--
ALTER TABLE `hari_kerja_ob`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `hari_kerja_terapis`
--
ALTER TABLE `hari_kerja_terapis`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `karyawan_hakakses_tambahan`
--
ALTER TABLE `karyawan_hakakses_tambahan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `kitchen`
--
ALTER TABLE `kitchen`
  MODIFY `id` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `komisi`
--
ALTER TABLE `komisi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `laporan_ob`
--
ALTER TABLE `laporan_ob`
  MODIFY `id_laporan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `ruangan`
--
ALTER TABLE `ruangan`
  MODIFY `id_ruangan` int(2) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `ruang_tunggu`
--
ALTER TABLE `ruang_tunggu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=110;

--
-- AUTO_INCREMENT for table `table_test`
--
ALTER TABLE `table_test`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `terapis_kerja`
--
ALTER TABLE `terapis_kerja`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `waiting_room_terapis`
--
ALTER TABLE `waiting_room_terapis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
