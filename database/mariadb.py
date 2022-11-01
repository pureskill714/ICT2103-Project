import os
import sys

import mariadb
from database.models import BloodDonation, BloodRequest, Branch, Donor, User

TABLE_DONOR = 'Donor'
TABLE_BLOODTYPE = 'BloodType'
TABLE_BLOODDONATION = 'BloodDonation'
TABLE_LABTEST = 'LabTest'
TABLE_BLOODREQUEST = 'BloodRequest'
TABLE_USER = 'User'
TABLE_BRANCH = 'Branch'

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

    def getUserById(self, id):
        '''Query user by username'''
        self._cursor.execute(f'SELECT * FROM {TABLE_USER} WHERE id=?', (id,))
        res = self._cursor.fetchone()
        if res is None:
            return None
        return User.fromTuple(res)

    def login(self, username, password):
        '''User authentication. Return the user if successful or None'''
        self._cursor.execute(f'SELECT * FROM {TABLE_USER} WHERE username=? AND password=?', (username, password))
        res = self._cursor.fetchone()
        if res is None:
            return None
        return User.fromTuple(res)

    def getAllDonors(self):
        '''Query list of all donors'''
        statement = f'''
            SELECT d.nric, d.name, d.dateOfBirth, d.contactNo, bt.type, d.registrationDate FROM {TABLE_DONOR} d
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.BloodTypeId=bt.id
            ORDER BY d.nric
        '''
        self._cursor.execute(statement)
        return [Donor.fromTuple(d) for d in self._cursor.fetchall()]

    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        statement = f'''
            SELECT d.nric, d.name, d.dateOfBirth, d.contactNo, bt.type, d.registrationDate FROM {TABLE_DONOR} d
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.BloodTypeId=bt.id
            WHERE nric=?
        '''
        self._cursor.execute(statement, (nric,))
        res = self._cursor.fetchone()
        if res is None:
            return None
        return Donor.fromTuple(res)

    def getDonorDonations(self, nric: str):
        '''Query one donor's donation records'''
        self._cursor.execute(f'SELECT * FROM {TABLE_BLOODDONATION} WHERE nric=?', (nric,))
        return [BloodDonation.fromTuple(d) for d in self._cursor.fetchall()]

    def insertDonor(self, donor: Donor):
        bloodTypeId = self.getBloodTypeId(donor.bloodType)
        statement = f'''
            INSERT INTO {TABLE_DONOR} (nric, name, dateOfBirth, contactNo, bloodTypeId, registrationDate)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        data = donor.toTuple(bloodTypeId)
        assert(len(data) == 6)
        try:
            self._cursor.execute(statement, data)
        except mariadb.Error as e:
            print(f"Error inserting new donor: {e}")

    def updateDonor(self, donor: Donor):
        bloodTypeId = self.getBloodTypeId(donor.bloodType)
        statement = f'''
            UPDATE {TABLE_DONOR}
            SET name=?, dateOfBirth=?, contactNo=?, bloodTypeId=?
            WHERE nric=?
        '''
        self._cursor.execute(statement, (donor.name, donor.dateOfBirth, donor.contactNo, bloodTypeId, donor.nric))

    def deleteDonorByNRIC(self, nric: str):
        '''Delete donor by NRIC'''
        statement = f'DELETE FROM {TABLE_DONOR} WHERE nric=?'
        self._cursor.execute(statement, (nric,))

    def getAllBloodDonations(self):
        '''Query list of all blood donations'''
        statement = f'''
            SELECT d.*, b.name, u.username FROM {TABLE_BLOODDONATION} d
            INNER JOIN {TABLE_BRANCH} b ON d.branchId=b.id
            INNER JOIN {TABLE_USER} u ON d.recordedBy=u.id
            ORDER BY d.date DESC, d.id
        '''
        self._cursor.execute(statement)
        return [BloodDonation.fromTuple(bd) for bd in self._cursor.fetchall()]

    def insertDonation(self, donation: BloodDonation):
        statement = f'''
            INSERT INTO {TABLE_BLOODDONATION} (id, nric, quantity, date, branchId, recordedBy, usedBy)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        data = donation.toTuple()
        assert(len(data) == 7)
        try:
            self._cursor.execute(statement, data)
        except mariadb.Error as e:
            print(f"Error inserting new donation: {e}")

    def getAllBloodRequests(self):
        '''Query list of all blood requests'''
        self._cursor.execute(f'''
            SELECT br.*, u.username, bt.type FROM {TABLE_BLOODREQUEST} br
                INNER JOIN {TABLE_BLOODTYPE} bt ON br.bloodTypeId=bt.id
                INNER JOIN {TABLE_USER} u ON br.requesterId=u.id
        ''')
        return [BloodRequest.fromTuple(br) for br in self._cursor.fetchall()]

    def getAllBranches(self):
        '''Query list of all blood bank branches'''
        self._cursor.execute(f'SELECT * FROM {TABLE_BRANCH}')
        return [Branch.fromTuple(br) for br in self._cursor.fetchall()]

    def getBloodTypeId(self, bloodType):
        '''Query the id of a blood type (e.g. A+)'''
        self._cursor.execute(f'SELECT id FROM {TABLE_BLOODTYPE} WHERE type=?', (bloodType,))
        res = self._cursor.fetchone()
        return res[0] if res is not None else None

    def getDashboardStats(self):
        '''Query data to show on the dashboard
        Returns: tuple(donor count, available blood, pending requests)
        '''
        self._cursor.execute(f'''
            SELECT d.*, b.*, r.* FROM
                (SELECT COUNT(nric) AS donorCount FROM {TABLE_DONOR}) as d,
                (SELECT SUM(quantity) AS totalBlood FROM {TABLE_BLOODDONATION}) as b,
                (SELECT COUNT(id) AS pendingCount FROM {TABLE_BLOODREQUEST} WHERE fulfilled=0) as r;
        ''')
        res = self._cursor.fetchone()
        return res
    