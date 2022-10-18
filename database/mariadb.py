import os
import sys

import mariadb
from database.models import Donor

TABLE_DONOR = 'Donor'
TABLE_BLOODTYPE = 'BloodType'
TABLE_BLOODDONATION = 'BloodDonation'
TABLE_LABTEST = 'LabTest'
TABLE_BLOODREQUEST = 'BloodRequest'
TABLE_USER = 'User'

class MariaDBBackend:
    def __init__(self):
        self.connect()
        super().__init__()

    def connect(self):
        # Connect to MariaDB
        user = os.getenv('BLOODMGT_MARIADB_USER')
        pwd = os.getenv('BLOODMGT_MARIADB_PASS')
        if user is None or pwd is None:
            raise ValueError('Please set your MariaDB user/password environment variables.')

        try:
            conn = mariadb.connect(
                user=user,
                password=pwd,
                host='localhost',
                port=3306,
                database='bloodmanagementsystem'
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        self._connection: mariadb.Connection = conn
        self._cursor: mariadb.Cursor = conn.cursor()
        return conn

    def commit(self):
        self._connection.commit()

    def getUser(self, username):
        '''Query user by username'''
        self._cursor.execute(f'SELECT * FROM {TABLE_USER} WHERE username=?', (username,))
        return self._cursor.fetchone()

    def getDonors(self):
        '''Query list of all donors'''
        self._cursor.execute(f'SELECT * FROM {TABLE_DONOR}')
        return self._cursor.fetchall()

    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        self._cursor.execute(f'SELECT * FROM {TABLE_DONOR} WHERE nric=?', (nric,))
        return self._cursor.fetchone()

    def getDonorDonations(self, nric: str):
        '''Query one donor's donation records'''
        self._cursor.execute(f'SELECT * FROM {TABLE_BLOODDONATION} WHERE nric=?', (nric,))
        return self._cursor.fetchall()

    def insertDonor(self, donor: Donor):
        statement = f'INSERT INTO {TABLE_DONOR} VALUES (?, ?, ?, ?, ?, ?)'
        data = donor.toTuple()
        assert(len(data) == 6)
        try:
            self._cursor.execute(statement, data)
        except mariadb.Error as e:
            print(f"Error inserting new donor: {e}")

    def updateDonor(self, donor: Donor):
        statement = f'UPDATE {TABLE_DONOR} SET name=?, dateOfBirth=?, contactNo=?, bloodTypeId=?, registrationDate=? WHERE nric=?'
        self._cursor.execute(statement, (donor.name, donor.dateOfBirth, donor.contactNo, donor.bloodTypeId, donor.registrationDate, donor.nric))

    def deleteDonorByNRIC(self, nric: str):
        '''Delete donor by NRIC'''
        statement = f'DELETE FROM {TABLE_DONOR} WHERE nric=?'
        self._cursor.execute(statement, (nric,))

    def getBloodTypeId(self, bloodType: str):
        '''Query the blood type id for a blood type (e.g. A+/AB-)'''
        self._cursor.execute(f'SELECT id FROM {TABLE_BLOODTYPE} WHERE bloodType=?', (bloodType,))
        return self._cursor.fetchone()
    