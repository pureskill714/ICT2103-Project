DROP SCHEMA IF EXISTS bloodmanagementsystem;

CREATE SCHEMA bloodmanagementsystem;
USE bloodmanagementsystem;

CREATE TABLE `BloodType` (
  `id` INT PRIMARY KEY,
  `type` VARCHAR(3) NOT NULL
);
  
CREATE TABLE `Donor` (
  `nric` CHAR(10) PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `dateOfBirth` DATE NOT NULL,
  `contactNo` VARCHAR(20) NOT NULL,
  `bloodTypeId` INT UNSIGNED NOT NULL,
  `registrationDate` DATETIME NOT NULL DEFAULT NOW(),
  CONSTRAINT FK_Donor_BloodType_id
    FOREIGN KEY (bloodTypeId) REFERENCES `BloodType`(`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE `Branch` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `address` VARCHAR(200) NOT NULL,
  `postalCode` CHAR(6) NOT NULL
);

CREATE TABLE `Role` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL
);

CREATE TABLE `User` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(64) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `branchId` INT UNSIGNED NULL,
  `roleId` INT UNSIGNED NOT NULL,
  CONSTRAINT `FK_User_Branch_id`
    FOREIGN KEY (`branchId`) REFERENCES `Branch`(`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `FK_User_Role_id`
    FOREIGN KEY (`roleId`) REFERENCES `Role`(`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE `BloodRequest` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `requesterId` INT UNSIGNED NOT NULL,
  `bloodTypeId` INT UNSIGNED NOT NULL,
  `quantity` INT NOT NULL,
  `date` DATE NOT NULL,
  `address` VARCHAR(200) NOT NULL,
  `status` VARCHAR(100) NOT NULL,
  `fulfilled` TINYINT NOT NULL DEFAULT 0,
  CONSTRAINT `FK_BloodRequest_BloodType_id`
    FOREIGN KEY (`bloodTypeId`) REFERENCES `BloodType`(`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodRequest_User_id`
    FOREIGN KEY (`requesterId`) REFERENCES `User`(`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE `BloodDonation` (
  `id` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `nric` CHAR(10) NOT NULL,
  `quantity` INT UNSIGNED NOT NULL,
  `date` DATETIME NOT NULL,
  `branchId` INT UNSIGNED NOT NULL,
  `recordedBy` INT UNSIGNED NULL,
  `usedBy` INT UNSIGNED NULL,
  CONSTRAINT `FK_BloodDonation_Donor_nric`
    FOREIGN KEY (`nric`) REFERENCES `Donor`(`nric`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_Branch_id`
    FOREIGN KEY (`branchId`) REFERENCES `Branch`(`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_User_id`
    FOREIGN KEY (`recordedBy`) REFERENCES `User`(`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_BloodRequest_id`
    FOREIGN KEY (`usedBy`) REFERENCES `BloodRequest`(`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

