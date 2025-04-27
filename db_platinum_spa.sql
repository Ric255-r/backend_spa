-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 26, 2025 at 04:39 PM
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
  `status` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = not occupied, 1 = occupied'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `detail_promo_happyhour`
--

CREATE TABLE `detail_promo_happyhour` (
  `id` int(11) NOT NULL,
  `detail_kode_promo` varchar(6) NOT NULL,
  `hari` text NOT NULL COMMENT 'khusus hari apa aj',
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `disc` double NOT NULL COMMENT 'potongan harga',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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

-- --------------------------------------------------------

--
-- Table structure for table `detail_promo_tahunan`
--

CREATE TABLE `detail_promo_tahunan` (
  `id` int(11) NOT NULL,
  `detail_kode_promo` varchar(6) NOT NULL,
  `tanggal_mulai` datetime NOT NULL,
  `tanggal_selesai` datetime NOT NULL,
  `harga_promo` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `kontrak_img` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `karyawan`
--

INSERT INTO `karyawan` (`id_karyawan`, `nik`, `nama_karyawan`, `alamat`, `umur`, `jk`, `no_hp`, `jabatan`, `kontrak_img`) VALUES
('A0001', '61718181818181', 'Rio', 'Jl Jeruju', 20, 'Laki-Laki', '08171717171', 'admin', 'img/kontrak.png'),
('R0001', '61718181818181', 'Alvin', 'Jl. Tanray', 20, 'Laki-Laki', '08171717171', 'resepsionis', 'img/kontrak.png');

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
('K001', 'Pewangi', '2025-04-26 14:07:58');

-- --------------------------------------------------------

--
-- Table structure for table `kitchen`
--

CREATE TABLE `kitchen` (
  `id` int(5) NOT NULL,
  `id_transaksi` int(11) NOT NULL,
  `status_pesanan` varchar(20) NOT NULL,
  `jam_terima_psn` time NOT NULL,
  `jam_selesai_psn` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `main_transaksi`
--

CREATE TABLE `main_transaksi` (
  `id_transaksi` varchar(6) NOT NULL,
  `id_loker` int(2) NOT NULL,
  `jenis_transaksi` varchar(50) NOT NULL COMMENT 'fnb, fasilitas, paket',
  `jenis_tamu` varchar(6) NOT NULL,
  `id_member` varchar(6) NOT NULL,
  `no_hp` int(4) NOT NULL,
  `nama_tamu` varchar(50) NOT NULL,
  `id_ruangan` int(2) NOT NULL,
  `id_resepsionis` varchar(10) NOT NULL,
  `id_terapis` varchar(10) NOT NULL,
  `id_gro` varchar(10) NOT NULL,
  `id_detail_transaksi` varchar(7) NOT NULL,
  `total_harga` int(9) NOT NULL,
  `disc` double NOT NULL,
  `grand_total` int(10) NOT NULL,
  `jenis_pembayaran` tinyint(1) NOT NULL DEFAULT 0,
  `metode_pembayaran` varchar(10) NOT NULL COMMENT '0 = awal, 1 = akhir',
  `jumlah_bayar` int(9) NOT NULL,
  `jumlah_kembalian` int(9) NOT NULL,
  `is_cancel` tinyint(1) DEFAULT 0,
  `is_delete` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `main_transaksi`
--

INSERT INTO `main_transaksi` (`id_transaksi`, `id_loker`, `jenis_transaksi`, `jenis_tamu`, `id_member`, `no_hp`, `nama_tamu`, `id_ruangan`, `id_resepsionis`, `id_terapis`, `id_gro`, `id_detail_transaksi`, `total_harga`, `disc`, `grand_total`, `jenis_pembayaran`, `metode_pembayaran`, `jumlah_bayar`, `jumlah_kembalian`, `is_cancel`, `is_delete`, `created_at`, `updated_at`) VALUES
('TF0001', 1, '', '', '', 0, '', 0, '', '', '', '', 0, 0, 0, 0, '', 0, 0, 0, 0, '2025-04-26 08:23:43', NULL);

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
  `kategori` varchar(20) NOT NULL,
  `nama_fnb` varchar(50) NOT NULL,
  `harga_fnb` int(8) NOT NULL,
  `status_fnb` varchar(20) NOT NULL COMMENT 'unavailable dan available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_fnb`
--

INSERT INTO `menu_fnb` (`id_fnb`, `kategori`, `nama_fnb`, `harga_fnb`, `status_fnb`) VALUES
('F001', 'Food', 'Burger', 50000, 'Available'),
('F002', 'Bir', 'Heineken', 70000, 'Available'),
('F003', 'Food', 'Burger2', 50000, 'Available'),
('F004', 'Bir', 'Heineken2', 70000, 'Available'),
('F005', 'Food', 'Burger', 50000, 'Available'),
('F006', 'Bir', 'Heineken', 70000, 'Available'),
('F007', 'Food', 'Burger2', 50000, 'Available'),
('F008', 'Bir', 'Heineken2', 70000, 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `menu_produk`
--

CREATE TABLE `menu_produk` (
  `id_produk` varchar(6) NOT NULL,
  `id_kategori` varchar(6) NOT NULL,
  `nama_produk` varchar(50) NOT NULL,
  `harga_produk` int(8) NOT NULL,
  `stok` int(3) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `menu_produk`
--

INSERT INTO `menu_produk` (`id_produk`, `id_kategori`, `nama_produk`, `harga_produk`, `stok`, `created_at`, `updated_at`) VALUES
('P001', 'K001', 'Lilin', 60000, 20, '2025-04-26 14:11:49', '2025-04-26 14:11:49'),
('P002', 'K001', 'blabala', 1010101, 12, '2025-04-26 14:37:56', '2025-04-26 14:37:56');

-- --------------------------------------------------------

--
-- Table structure for table `paket_fasilitas`
--

CREATE TABLE `paket_fasilitas` (
  `id_fasilitas` int(1) NOT NULL,
  `nama_fasilitas` varchar(50) NOT NULL,
  `harga_fasilitas` int(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paket_fasilitas`
--

INSERT INTO `paket_fasilitas` (`id_fasilitas`, `nama_fasilitas`, `harga_fasilitas`) VALUES
(1, 'Platinum Health Facilities', 200000);

-- --------------------------------------------------------

--
-- Table structure for table `paket_massage`
--

CREATE TABLE `paket_massage` (
  `id_paket_msg` varchar(6) NOT NULL,
  `nama_paket_msg` varchar(50) NOT NULL,
  `harga_paket_msg` int(8) NOT NULL,
  `durasi` int(3) NOT NULL,
  `id_komisi` int(3) NOT NULL,
  `tipe_komisi` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0=persen, 1=nominal',
  `detail_paket` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `paket_massage`
--

INSERT INTO `paket_massage` (`id_paket_msg`, `nama_paket_msg`, `harga_paket_msg`, `durasi`, `id_komisi`, `tipe_komisi`, `detail_paket`) VALUES
('M001', 'Platinum Treatment', 550000, 90, 1, 0, 'Include Facilities');

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

-- --------------------------------------------------------

--
-- Table structure for table `ruangan`
--

CREATE TABLE `ruangan` (
  `id_ruangan` int(2) NOT NULL,
  `nama_ruangan` varchar(20) NOT NULL,
  `lantai` int(2) NOT NULL,
  `jenis_ruangan` varchar(12) NOT NULL,
  `status` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ruangan`
--

INSERT INTO `ruangan` (`id_ruangan`, `nama_ruangan`, `lantai`, `jenis_ruangan`, `status`) VALUES
(1, 'Fasilitas', 1, 'Fasilitas', 'Ready'),
(2, 'Reg-01', 1, 'Reguler', 'Ready'),
(3, 'Vip-01', 1, 'Vip', 'Ready');

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
  `id_transaksi` int(11) NOT NULL,
  `jam_datang` time NOT NULL,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `alasan` text DEFAULT NULL COMMENT 'diisi klo selesai lebih cepat',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id_karyawan` varchar(20) NOT NULL,
  `passwd` varchar(50) NOT NULL,
  `hak_akses` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id_karyawan`, `passwd`, `hak_akses`, `created_at`, `updated_at`) VALUES
('A0001', '1234', 'admin', '2025-04-23 10:36:50', NULL),
('K0001', '1234', 'kitchen', '2025-04-23 10:36:50', NULL),
('O0001', '1234', 'owner', '2025-04-23 10:36:50', NULL),
('R0001', '1234', 'resepsionis', '2025-04-23 10:36:50', NULL);

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
  ADD PRIMARY KEY (`id_transaksi`,`id_loker`);

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
  MODIFY `id_loker` int(2) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `detail_promo_happyhour`
--
ALTER TABLE `detail_promo_happyhour`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `detail_promo_kunjungan`
--
ALTER TABLE `detail_promo_kunjungan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `detail_promo_tahunan`
--
ALTER TABLE `detail_promo_tahunan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hari_kerja_terapis`
--
ALTER TABLE `hari_kerja_terapis`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `kitchen`
--
ALTER TABLE `kitchen`
  MODIFY `id` int(5) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `komisi`
--
ALTER TABLE `komisi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `laporan_ob`
--
ALTER TABLE `laporan_ob`
  MODIFY `id_laporan` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ruangan`
--
ALTER TABLE `ruangan`
  MODIFY `id_ruangan` int(2) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `table_test`
--
ALTER TABLE `table_test`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `terapis_kerja`
--
ALTER TABLE `terapis_kerja`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `waiting_room_terapis`
--
ALTER TABLE `waiting_room_terapis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
