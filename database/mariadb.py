import os
import sys

import mariadb
from database.models import BloodDonation, BloodInventory, BloodRequest, Branch, DashboardData, Donor, User

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

    def getAllDonations(self):
        '''Query list of all blood donations'''
        statement = f'''
            SELECT bd.*, b.name, u.username FROM {TABLE_BLOODDONATION} bd
            INNER JOIN {TABLE_BRANCH} b ON bd.branchId=b.id
            INNER JOIN {TABLE_USER} u ON bd.recordedBy=u.id
            ORDER BY bd.date DESC, bd.id
        '''
        self._cursor.execute(statement)
        return [BloodDonation.fromTuple(bd) for bd in self._cursor.fetchall()]

    def getAvailableDonationsByBloodType(self, bloodType: str):
        '''Query donation records not yet used for request fulfillment by blood type'''
        self._cursor.execute(f'''
            SELECT bd.* FROM {TABLE_BLOODDONATION} bd
            INNER JOIN {TABLE_DONOR} d ON bd.nric=d.nric
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.bloodTypeId=bt.id
            WHERE bd.usedBy IS NULL AND bt.type=? 
        ''', (bloodType,))
        return [BloodDonation.fromTuple(d) for d in self._cursor.fetchall()]

    def insertDonation(self, donation: BloodDonation):
        statement = f'''
            INSERT INTO {TABLE_BLOODDONATION} (id, nric, quantity, date, branchId, recordedBy)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        data = donation.toTuple()
        assert(len(data) == 6)
        try:
            self._cursor.execute(statement, data)
            return self._cursor.lastrowid
        except mariadb.Error as e:
            print(f"Error inserting new donation: {e}")

    def getAllRequests(self):
        '''Query list of all blood requests'''
        self._cursor.execute(f'''
            SELECT br.*, u.username, bt.type FROM {TABLE_BLOODREQUEST} br
            INNER JOIN {TABLE_BLOODTYPE} bt ON br.bloodTypeId=bt.id
            INNER JOIN {TABLE_USER} u ON br.requesterId=u.id
        ''')
        return [BloodRequest.fromTuple(br) for br in self._cursor.fetchall()]

    def getRequestById(self, id):
        '''Query blood requests by request id'''
        self._cursor.execute(f'''
            SELECT br.*, u.username, bt.type FROM {TABLE_BLOODREQUEST} br
            INNER JOIN {TABLE_BLOODTYPE} bt ON br.bloodTypeId=bt.id
            INNER JOIN {TABLE_USER} u ON br.requesterId=u.id
            WHERE br.id=?
        ''', (id,))
        return BloodRequest.fromTuple(self._cursor.fetchone())

    def getAllBranches(self):
        '''Query list of all blood bank branches'''
        self._cursor.execute(f'SELECT * FROM {TABLE_BRANCH}')
        return [Branch.fromTuple(br) for br in self._cursor.fetchall()]

    def getBloodTypeId(self, bloodType):
        '''Query the id of a blood type (e.g. A+)'''
        self._cursor.execute(f'SELECT id FROM {TABLE_BLOODTYPE} WHERE type=?', (bloodType,))
        res = self._cursor.fetchone()
        return res[0] if res is not None else None

    def getDashboardStats(self, branchId):
        '''Query data to show on the dashboard
        Returns: DashboardData(donor count, available blood, pending requests, blood inventory)
        '''
        self._cursor.execute(f'''
            SELECT d.*, b.*, r.* FROM
                (SELECT COUNT(nric) AS donorCount FROM {TABLE_DONOR}) as d,
                (SELECT SUM(quantity) AS availableBlood FROM {TABLE_BLOODDONATION} WHERE usedBy IS NULL) as b,
                (SELECT COUNT(id) AS pendingCount FROM {TABLE_BLOODREQUEST} WHERE fulfilled=0) as r;
        ''')
        donorCount, availableBlood, pendingCount = self._cursor.fetchone()
        inventory = self.getBloodInventoryByBranchId(branchId)
        return DashboardData(donorCount, availableBlood, pendingCount, inventory.storage)

    def getBloodInventoryByBranchId(self, branchId):
        '''Query blood inventory data
        Returns: BloodInventory
        '''
        self._cursor.execute(f'''
            SELECT b.branchId, bt.type, SUM(b.quantity) FROM {TABLE_BLOODDONATION} b
                INNER JOIN {TABLE_DONOR} d ON b.nric=d.nric
                INNER JOIN {TABLE_BLOODTYPE} bt ON d.bloodTypeId=bt.id
                WHERE b.usedBy IS NULL AND b.branchId=?
                GROUP BY bt.type;
        ''', (branchId,))
        inventories = BloodInventory.fromTupleList(self._cursor.fetchall())
        assert(len(inventories) == 1)
        return inventories[0]
    