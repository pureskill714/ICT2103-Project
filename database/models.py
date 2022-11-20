from datetime import date, datetime

from flask_login import UserMixin

# Inheriting from UserMixin required for flask login
class User(UserMixin):
    def __init__(self, id, username, password, name, branchId, role):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.branchId = branchId
        self.role = role

    @staticmethod
    def fromDict(data: dict):
        id = data.get('id', None)
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        branchId = data.get('branchId')
        role = data.get('role')
        return User(id, username, password, name, branchId, role)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'branchId': self.branchId,
            'role': self.role,
        }

class Donor:
    def __init__(self, nric, name, dateOfBirth, contactNo, bloodType, registrationDate):
        self.nric = nric
        self.name = name
        self.dateOfBirth = dateOfBirth
        self.contactNo = contactNo
        self.bloodType = bloodType
        self.registrationDate = registrationDate

    def toTuple(self, bloodTypeId):
        '''Converts to relational DB format'''
        return (self.nric, self.name, self.dateOfBirth, self.contactNo, bloodTypeId, self.registrationDate)

    @staticmethod
    def fromDict(data: dict):
        nric = data.get('nric')
        name = data.get('name')
        dateOfBirth = data.get('dateOfBirth')
        contactNo = data.get('contactNo')
        bloodType = data.get('bloodType')
        registrationDate = data.get('registrationDate')
        return Donor(nric, name, dateOfBirth, contactNo, bloodType, registrationDate)

    def serialize(self):
        return {
            'nric': self.nric,
            'name': self.name,
            'dateOfBirth': self.dateOfBirth,
            'contactNo': self.contactNo,
            'bloodType': self.bloodType,
            'registrationDate': self.registrationDate,
        }

class BloodDonation:
    def __init__(self, id, nric, quantity, date, branchId, recordedBy, usedBy, branchName = None, staffUsername = None, bloodType = None):
        self.id = id
        self.nric = nric
        self.quantity = quantity
        self.date = date
        self.branchId = branchId
        self.recordedBy = recordedBy
        self.usedBy = usedBy

        self.branchName = branchName
        self.staffUsername = staffUsername
        self.bloodType = bloodType

    def toTuple(self):
        return (self.id, self.nric, self.quantity, self.date, self.branchId, self.recordedBy)
    
    @staticmethod
    def fromDict(data):
        id = data.get('id')
        nric = data.get('nric')
        quantity = data.get('quantity')
        date = data.get('date')
        branchId = data.get('branchId')
        recordedBy = data.get('recordedBy')
        usedBy = data.get('usedBy')
        branchName = data.get('branchName')
        staffUsername = data.get('staffUsername')
        bloodType = data.get('bloodType')
        return BloodDonation(id, nric, quantity, date, branchId, recordedBy, usedBy, branchName, staffUsername, bloodType)

    def serialize(self):
        return {
            'id': self.id,
            'nric': self.nric,
            'quantity': self.quantity,
            'date': self.date.isoformat(),
            'branchId': self.branchId,
            'recordedBy': self.recordedBy,
            'usedBy': self.usedBy,
            'branchName': self.branchName,
            'staffUsername': self.staffUsername,
            'bloodType': self.bloodType
        }

class BloodRequest:
    def __init__(self, id, requesterId, bloodType, quantity, date, address, status, fulfilled, requester = None):
        self.id = id
        self.requesterId = requesterId
        self.bloodType = bloodType
        self.quantity = quantity
        self.date = date
        self.address = address
        self.status = status
        self.fulfilled = fulfilled

        self.requester = requester

    def toTuple(self, bloodTypeId):
        return (self.id, self.requesterId, bloodTypeId, self.quantity, self.date, self.address, self.status, self.fulfilled)

    @staticmethod
    def fromDict(data: dict):
        return BloodRequest(
            data.get('id'), 
            data.get('requesterId'), 
            data.get('bloodType'),
            data.get('quantity'),
            data.get('date'), 
            data.get('address'), 
            data.get('status'), 
            data.get('fulfilled'), 
            data.get('requester'),
        )

    def serialize(self):
        return {
            'id': self.id,
            'requesterId': self.requesterId,
            'bloodType': self.bloodType,
            'quantity': self.quantity,
            'date': self.date.isoformat(),
            'address': self.address,
            'status': self.status,
            'fulfilled': self.fulfilled,
            'requester': self.requester,
        }

class Branch:
    def __init__(self, id, name, address, postalCode):
        self.id = id
        self.name = name
        self.address = address
        self.postalCode = postalCode

    @staticmethod
    def fromDict(data: dict):
        return Branch(
            data.get('id'), 
            data.get('name'), 
            data.get('address'),
            data.get('postalCode'),
        )

class DashboardData:
    def __init__(self, donorCount, availableBlood, pendingRequests, bloodInventoryMap):
        self.donorCount = donorCount
        self.availableBlood = availableBlood
        self.pendingRequests = pendingRequests
        self.bloodInventoryMap = bloodInventoryMap

class BloodInventory:
    def __init__(self, branchId):
        self.branchId = branchId
        self.storage = dict.fromkeys([
            'A+', 'A-', 'B+', 'B-',
            'AB+', 'AB-', 'O+', 'O-'], 0)

    @staticmethod
    def fromTupleList(data: list):
        '''Parse list of tuple(branchId, blood type, quantity)
        Returns: list of BloodInventory'''
        inventories: dict[str, BloodInventory] = {} # { branchId: BloodInventory }
        for t in data: # tuple(branchId, blood type, quantity)
            branchId, bloodType, quantity = t
            if branchId not in inventories.keys():
                inventories[branchId] = BloodInventory(branchId)
            inventories[branchId].storage[bloodType] += quantity
        return list(inventories.values()) # Unpack tuple