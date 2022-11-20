import os
import sys

import mariadb
from database.models import BloodDonation, BloodInventory, BloodRequest, Branch, DashboardData, Donor, User

TABLE_DONOR = 'Donor'
TABLE_BLOODTYPE = 'BloodType'
TABLE_DONATION = 'BloodDonation'
TABLE_REQUEST = 'BloodRequest'
TABLE_USER = 'User'
TABLE_ROLE = 'Role'
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
        self._cursor.execute(f'''
            SELECT u.id, u.username, u.password, u.name, u.branchId, r.name FROM {TABLE_USER} u
            INNER JOIN {TABLE_ROLE} r ON u.roleId=r.id
            WHERE u.id=?
        ''', (id,))
        res = self._cursor.fetchone()
        if res is None:
            return None
        return User(*res)

    def login(self, username, password):
        '''User authentication. Return the user if successful or None'''
        self._cursor.execute(f'''
            SELECT u.id, u.username, u.password, u.name, u.branchId, r.name FROM {TABLE_USER} u
            INNER JOIN {TABLE_ROLE} r ON u.roleId=r.id
            WHERE u.username=? AND u.password=?
        ''', (username, password))
        res = self._cursor.fetchone()
        if res is None:
            return None
        return User(*res)

    def register(self, user: User):
        '''User registration. Return the user if successful or None'''
        roleId = self.getRoleIdByName(user.role)
        self._cursor.execute(f'''
            INSERT INTO {TABLE_USER} (username, password, name, branchId, roleId)
            VALUES (?, ?, ?, ?, ?)
        ''', (user.username, user.password, user.name, user.branchId, roleId))
        self.commit()
        return self.login(user.username, user.password)

    def getAllDonors(self):
        '''Query list of all donors'''
        statement = f'''
            SELECT d.nric, d.name, d.dateOfBirth, d.contactNo, bt.type, d.registrationDate FROM {TABLE_DONOR} d
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.BloodTypeId=bt.id
            ORDER BY d.nric
        '''
        self._cursor.execute(statement)
        return [Donor(*d) for d in self._cursor.fetchall()]

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
        return Donor(*res)

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
            SELECT bd.id, bd.nric, bd.quantity, bd.date, bd.branchId, bd.recordedBy, bd.usedBy, b.name, u.username, bt.type
                FROM {TABLE_DONATION} bd
            INNER JOIN {TABLE_BRANCH} b ON bd.branchId=b.id
            LEFT JOIN {TABLE_USER} u ON bd.recordedBy=u.id
            INNER JOIN {TABLE_DONOR} d ON bd.nric=d.nric
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.bloodTypeId=bt.id
            ORDER BY bd.date DESC, bd.id
        '''
        self._cursor.execute(statement)
        return [BloodDonation(*bd) for bd in self._cursor.fetchall()]

    def getDonationById(self, id):
        '''Query one blood donation by id'''
        statement = f'''
            SELECT bd.id, bd.nric, bd.quantity, bd.date, bd.branchId, bd.recordedBy, bd.usedBy, b.name, u.username
                FROM {TABLE_DONATION} bd
            INNER JOIN {TABLE_BRANCH} b ON bd.branchId=b.id
            INNER JOIN {TABLE_USER} u ON bd.recordedBy=u.id
            WHERE bd.id=?
        '''
        self._cursor.execute(statement, (id,))
        return BloodDonation(*self._cursor.fetchone())

    def getDonationsIdsByRequestId(self, id):
        '''Query all blood donation ids used to fulfill the request with given id.'''
        statement = f'''
            SELECT id FROM {TABLE_DONATION}
            WHERE usedBy=?
        '''
        self._cursor.execute(statement, (id,))
        return [r[0] for r in self._cursor.fetchall()]

    def getAvailableDonationsByBloodType(self, bloodType: str):
        '''Query donation records not yet used for request fulfillment by blood type'''
        self._cursor.execute(f'''
            SELECT bd.id, bd.nric, bd.quantity, bd.date, bd.branchId, bd.recordedBy, bd.usedBy
                FROM {TABLE_DONATION} bd
            INNER JOIN {TABLE_DONOR} d ON bd.nric=d.nric
            INNER JOIN {TABLE_BLOODTYPE} bt ON d.bloodTypeId=bt.id
            WHERE bd.usedBy IS NULL AND bt.type=? 
        ''', (bloodType,))
        return [BloodDonation(*d) for d in self._cursor.fetchall()]

    def insertDonation(self, donation: BloodDonation):
        statement = f'''
            INSERT INTO {TABLE_DONATION} (id, nric, quantity, date, branchId, recordedBy)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        data = donation.toTuple()
        assert(len(data) == 6)
        self._cursor.execute(statement, data)
        return self._cursor.lastrowid

    def getAllRequests(self):
        '''Query list of all blood requests'''
        self._cursor.execute(f'''
            SELECT br.id, br.requesterId, bt.type, br.quantity, br.date, br.address, 
                br.status, br.fulfilled, u.username FROM {TABLE_REQUEST} br
            INNER JOIN {TABLE_BLOODTYPE} bt ON br.bloodTypeId=bt.id
            INNER JOIN {TABLE_USER} u ON br.requesterId=u.id
        ''')
        return [BloodRequest(*br) for br in self._cursor.fetchall()]

    def getRequestById(self, id):
        '''Query blood requests by request id'''
        self._cursor.execute(f'''
            SELECT br.id, br.requesterId, bt.type, br.quantity, br.date, br.address, 
                br.status, br.fulfilled, u.username FROM {TABLE_REQUEST} br
            INNER JOIN {TABLE_BLOODTYPE} bt ON br.bloodTypeId=bt.id
            INNER JOIN {TABLE_USER} u ON br.requesterId=u.id
            WHERE br.id=?
        ''', (id,))
        return BloodRequest(*self._cursor.fetchone())

    def insertRequest(self, req: BloodRequest):
        bloodTypeId = self.getBloodTypeId(req.bloodType)
        statement = f'''
            INSERT INTO {TABLE_REQUEST} (id, requesterId, bloodTypeId, quantity, date, address, status, fulfilled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data = req.toTuple(bloodTypeId)
        assert(len(data) == 8)
        try:
            self._cursor.execute(statement, data)
            return self._cursor.lastrowid
        except mariadb.Error as e:
            print(f"Error inserting new blood request: {e}")

    def fulfillRequest(self, requestId: str, donationIds: list[str]):
        ''''''
        statement = f'''
            UPDATE {TABLE_DONATION}
            SET usedBy=?
            WHERE id in ({','.join(['?'] * len(donationIds))})
        '''
        data = tuple((int(requestId),)) + tuple(map(int, donationIds))
        self._cursor.execute(statement, data)

        statement = f'''
            UPDATE {TABLE_REQUEST}
            SET status=?, fulfilled=?
            WHERE id=?
        '''
        self._cursor.execute(statement, ('Delivered', 1, requestId))

    def getAllBranches(self):
        '''Query list of all blood bank branches'''
        self._cursor.execute(f'SELECT id, name, address, postalCode FROM {TABLE_BRANCH}')
        return [Branch(*br) for br in self._cursor.fetchall()]

    def getRoleIdByName(self, roleName):
        '''Query role id by its name'''
        statement = f'''
            SELECT id FROM {TABLE_ROLE}
            WHERE name=?
        '''
        self._cursor.execute(statement, (roleName,))
        return self._cursor.fetchone()[0]

    def getBloodTypeId(self, bloodType):
        '''Query the id of a blood type (e.g. A+)'''
        self._cursor.execute(f'SELECT id FROM {TABLE_BLOODTYPE} WHERE type=?', (bloodType,))
        res = self._cursor.fetchone()
        return res[0] if res is not None else None

    def getDashboardStats(self, branchId):
        '''Query data to show on the dashboard
        Returns: DashboardData(donor count, available blood, pending requests, donations , blood inventory)
        '''
        self._cursor.execute(f'''
            SELECT d.donorCount, bd.availableBlood, req.pendingCount, bd2.donationsThisWeek, bd2.bloodQtyThisWeek FROM
            	(SELECT COUNT(nric) AS donorCount FROM {TABLE_DONOR}) AS d,
            	(SELECT SUM(quantity) AS availableBlood FROM {TABLE_DONATION} WHERE usedBy IS NULL) AS bd,
            	(SELECT COUNT(id) AS pendingCount FROM {TABLE_REQUEST} WHERE fulfilled=0) AS req,
            	(SELECT COUNT(d2Stat.id) AS donationsThisWeek, COALESCE(SUM(d2Stat.quantity),0) AS bloodQtyThisWeek FROM (
            		SELECT bd.id, bd.quantity FROM {TABLE_DONATION} bd
            			WHERE bd.date BETWEEN DATE(DATE_ADD(NOW(), INTERVAL(-WEEKDAY(NOW())) DAY))
            				AND DATE(DATE_ADD(NOW(), INTERVAL(7-WEEKDAY(NOW())) DAY))
            		) AS d2Stat
            	) AS bd2;
        ''')
        donorCount, availableBlood, pendingCount, donationsThisWeek, bloodQtyThisWeek = self._cursor.fetchone()
        inventory = self.getBloodInventoryByBranchId(branchId)
        return DashboardData(donorCount, availableBlood, pendingCount, donationsThisWeek, bloodQtyThisWeek, inventory.storage)

    def getBloodInventoryByBranchId(self, branchId):
        '''Query blood inventory data
        Returns: BloodInventory
        '''
        self._cursor.execute(f'''
            SELECT b.branchId, bt.type, SUM(b.quantity) FROM {TABLE_DONATION} b
                INNER JOIN {TABLE_DONOR} d ON b.nric=d.nric
                INNER JOIN {TABLE_BLOODTYPE} bt ON d.bloodTypeId=bt.id
                WHERE b.usedBy IS NULL AND b.branchId=?
                GROUP BY bt.type;
        ''', (branchId,))
        inventories = BloodInventory.fromTupleList(self._cursor.fetchall())
        assert(len(inventories) == 1)
        return inventories[0]
    