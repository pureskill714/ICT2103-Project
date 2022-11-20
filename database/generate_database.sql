-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema bloodmanagementsystem
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `bloodmanagementsystem` ;

-- -----------------------------------------------------
-- Schema bloodmanagementsystem
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `bloodmanagementsystem` ;
USE `bloodmanagementsystem` ;

-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`BloodType`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`BloodType` (
  `id` INT UNSIGNED NOT NULL,
  `type` VARCHAR(3) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`Donor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`Donor` (
  `nric` CHAR(10) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `dateOfBirth` DATE NOT NULL,
  `contactNo` VARCHAR(20) NOT NULL,
  `bloodTypeId` INT UNSIGNED NOT NULL,
  `registrationDate` DATETIME NOT NULL DEFAULT CURRENT_DATE(),
  PRIMARY KEY (`nric`),
  CONSTRAINT `fk_Donor_BloodType_id`
    FOREIGN KEY (`bloodTypeId`)
    REFERENCES `bloodmanagementsystem`.`BloodType` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `IDX_Donor_bloodTypeId` ON `bloodmanagementsystem`.`Donor` (`bloodTypeId` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`Branch`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`Branch` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `address` VARCHAR(200) NOT NULL,
  `postalCode` CHAR(6) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`Role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`Role` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`User`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`User` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(64) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `branchId` INT UNSIGNED NULL,
  `roleId` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_User_Branch_id`
    FOREIGN KEY (`branchId`)
    REFERENCES `bloodmanagementsystem`.`Branch` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `FK_User_Role_id`
    FOREIGN KEY (`roleId`)
    REFERENCES `bloodmanagementsystem`.`Role` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `IDX_User_branchId` ON `bloodmanagementsystem`.`User` (`branchId` ASC) VISIBLE;

CREATE INDEX `IDX_User_roleId` ON `bloodmanagementsystem`.`User` (`roleId` ASC) VISIBLE;

CREATE INDEX `IDX_User_username_password` ON `bloodmanagementsystem`.`User` (`username` ASC, `password` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`BloodRequest`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`BloodRequest` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `requesterId` INT UNSIGNED NOT NULL,
  `bloodTypeId` INT UNSIGNED NOT NULL,
  `quantity` INT NOT NULL,
  `date` DATE NOT NULL,
  `address` VARCHAR(200) NOT NULL,
  `status` VARCHAR(100) NOT NULL,
  `fulfilled` TINYINT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_BloodRequest_BloodType_id`
    FOREIGN KEY (`bloodTypeId`)
    REFERENCES `bloodmanagementsystem`.`BloodType` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodRequest_User_id`
    FOREIGN KEY (`requesterId`)
    REFERENCES `bloodmanagementsystem`.`User` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `IDX_BloodRequest_bloodTypeId` ON `bloodmanagementsystem`.`BloodRequest` (`bloodTypeId` ASC) VISIBLE;

CREATE INDEX `IDX_BloodRequest_requesterId` ON `bloodmanagementsystem`.`BloodRequest` (`requesterId` ASC) VISIBLE;

CREATE INDEX `IDX_BloodRequest_fulfilled` ON `bloodmanagementsystem`.`BloodRequest` (`fulfilled` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `bloodmanagementsystem`.`BloodDonation`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bloodmanagementsystem`.`BloodDonation` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nric` CHAR(10) NOT NULL,
  `quantity` INT UNSIGNED NOT NULL,
  `date` DATETIME NOT NULL,
  `branchId` INT UNSIGNED NOT NULL,
  `recordedBy` INT UNSIGNED NULL,
  `usedBy` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK_BloodDonation_Donor_nric`
    FOREIGN KEY (`nric`)
    REFERENCES `bloodmanagementsystem`.`Donor` (`nric`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_Branch_id`
    FOREIGN KEY (`branchId`)
    REFERENCES `bloodmanagementsystem`.`Branch` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_User_id`
    FOREIGN KEY (`recordedBy`)
    REFERENCES `bloodmanagementsystem`.`User` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `FK_BloodDonation_BloodRequest_id`
    FOREIGN KEY (`usedBy`)
    REFERENCES `bloodmanagementsystem`.`BloodRequest` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE INDEX `IDX_BloodDonation_nric` ON `bloodmanagementsystem`.`BloodDonation` (`nric` ASC) VISIBLE;

CREATE INDEX `IDX_BloodDonation_branchId` ON `bloodmanagementsystem`.`BloodDonation` (`branchId` ASC) VISIBLE;

CREATE INDEX `IDX_BloodDonation_recordedBy` ON `bloodmanagementsystem`.`BloodDonation` (`recordedBy` ASC) VISIBLE;

CREATE INDEX `IDX_BloodDonation_usedBy` ON `bloodmanagementsystem`.`BloodDonation` (`usedBy` ASC) VISIBLE;

CREATE INDEX `IDX_BloodDonation_date` ON `bloodmanagementsystem`.`BloodDonation` (`date` DESC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`BloodType`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (1, 'A+');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (2, 'A-');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (3, 'B+');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (4, 'B-');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (5, 'O+');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (6, 'O-');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (7, 'AB+');
INSERT INTO `bloodmanagementsystem`.`BloodType` (`id`, `type`) VALUES (8, 'AB-');

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`Donor`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S9990000A', 'Donor A', '1999-01-01', '90000001', 1, '2020-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S9991111A', 'Donor B', '1999-06-01', '90000002', 2, '2021-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('T0000000B', 'Donor C', '2000-01-01', '90000003', 3, '2020-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('T0001111B', 'Donor D', '2000-06-01', '90000004', 4, '2021-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S8880000C', 'Donor E', '1988-01-01', '90000005', 5, '2020-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S8881111C', 'Donor F', '1988-06-01', '90000006', 6, '2021-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S7770000D', 'Donor G', '1977-01-01', '90000007', 7, '2020-01-01');
INSERT INTO `bloodmanagementsystem`.`Donor` (`nric`, `name`, `dateOfBirth`, `contactNo`, `bloodTypeId`, `registrationDate`) VALUES ('S7771111D', 'Donor H', '1977-06-01', '90000008', 8, '2021-01-01');

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`Branch`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`Branch` (`id`, `name`, `address`, `postalCode`) VALUES (10001, 'Woodlands Branch', 'Causeway Point', '777777');
INSERT INTO `bloodmanagementsystem`.`Branch` (`id`, `name`, `address`, `postalCode`) VALUES (10002, 'Jurong Branch', 'Westgate', '888888');
INSERT INTO `bloodmanagementsystem`.`Branch` (`id`, `name`, `address`, `postalCode`) VALUES (10003, 'Changi Branch', 'Changi Airport', '999999');
INSERT INTO `bloodmanagementsystem`.`Branch` (`id`, `name`, `address`, `postalCode`) VALUES (10004, 'Marina Branch', 'Marina Bay', '000000');

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`Role`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`Role` (`id`, `name`) VALUES (1, 'role.staff.bloodbank');
INSERT INTO `bloodmanagementsystem`.`Role` (`id`, `name`) VALUES (2, 'role.staff.healthcare');

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`User`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`User` (`id`, `username`, `password`, `name`, `branchId`, `roleId`) VALUES (1, 'user1', '1234', 'Staff @ Woodlands', 10001, 1);
INSERT INTO `bloodmanagementsystem`.`User` (`id`, `username`, `password`, `name`, `branchId`, `roleId`) VALUES (2, 'user2', '1234', 'Staff @ Jurong', 10002, 1);
INSERT INTO `bloodmanagementsystem`.`User` (`id`, `username`, `password`, `name`, `branchId`, `roleId`) VALUES (3, 'user3', '1234', 'Staff @ Changi', 10003, 1);
INSERT INTO `bloodmanagementsystem`.`User` (`id`, `username`, `password`, `name`, `branchId`, `roleId`) VALUES (4, 'user4', '1234', 'Staff @ Marina', 10004, 1);
INSERT INTO `bloodmanagementsystem`.`User` (`id`, `username`, `password`, `name`, `branchId`, `roleId`) VALUES (5, 'healthcare1', '1234', 'Healthcare Staff', NULL, 2);

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`BloodRequest`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (1, 5, 1, 100, '2022-02-01', 'TTSH', 'Delivered', 1);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (2, 5, 2, 200, '2022-03-01', 'TTSH', 'Delivered', 1);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (3, 5, 3, 300, '2022-04-01', 'KPTH', 'Pending', 0);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (4, 5, 4, 400, '2022-05-01', 'KPTH', 'Pending', 0);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (5, 5, 5, 500, '2022-06-01', 'NTFGH', 'Pending', 0);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (6, 5, 6, 600, '2022-07-01', 'NTFGH', 'Pending', 0);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (7, 5, 7, 700, '2022-08-01', 'KKWOMEN', 'Delivered', 1);
INSERT INTO `bloodmanagementsystem`.`BloodRequest` (`id`, `requesterId`, `bloodTypeId`, `quantity`, `date`, `address`, `status`, `fulfilled`) VALUES (8, 5, 8, 800, '2022-09-01', 'KKWOMEN', 'Delivered', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `bloodmanagementsystem`.`BloodDonation`
-- -----------------------------------------------------
START TRANSACTION;
USE `bloodmanagementsystem`;
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (1, 'S9990000A', 350, '2022-01-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (2, 'S9991111A', 450, '2022-01-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (3, 'T0000000B', 300, '2022-01-01', 10002, 2, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (4, 'T0001111B', 350, '2022-01-01', 10002, 2, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (5, 'S8880000C', 420, '2022-01-01', 10003, 3, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (6, 'S8881111C', 320, '2022-01-01', 10003, 3, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (7, 'S7770000D', 450, '2022-01-01', 10004, 4, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (8, 'S7771111D', 400, '2022-01-01', 10004, 4, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (9, 'S9990000A', 200, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (10, 'S9990000A', 150, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (11, 'S9991111A', 350, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (12, 'S9991111A', 400, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (13, 'S7770000D', 380, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (14, 'S7770000D', 420, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (15, 'S7771111D', 280, '2022-02-01', 10001, 1, NULL);
INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES (16, 'S7771111D', 300, '2022-02-01', 10001, 1, NULL);

COMMIT;

