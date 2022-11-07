from datetime import date, datetime

from flask_login import UserMixin

# Inheriting from UserMixin required for flask login
class User(UserMixin):
    def __init__(self, id, username, password, name, branchId, roleId):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.branchId = branchId
        self.roleId = roleId

    @staticmethod
    def fromTuple(data):
        return User(*data) # Unpack tuple

    def fromDict(data):
        return User(data["id"], data["username"], data["password"], data["name"], data["branchId"], data["roleId"])

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
    def fromTuple(data):
        '''Converts from relational DB format'''
        return Donor(*data) # Unpack tuple

    def serialize(self):
        return {
            'nric': self.nric,
            'name': self.name,
            'dateOfBirth': self.dateOfBirth,
            'contactNo': self.contactNo,
            'bloodType': self.bloodType,
            'registrationDate': self.registrationDate,
        }

    def deserialize(self, data):
        self.nric = data['nric']
        self.name = data['name']
        self.dateOfBirth = data['dateOfBirth']
        self.contactNo = data['contactNo']
        self.bloodType = data['registrationDate']
        self.registrationDate = data['bloodType']

class BloodDonation:
    def __init__(self, id, nric, quantity, date, branchId, recordedBy, usedBy, branchName = None, staffUsername = None):
        self.id = id
        self.nric = nric
        self.quantity = quantity
        self.date = date
        self.branchId = branchId
        self.recordedBy = recordedBy
        self.usedBy = usedBy

        self.branchName = branchName
        self.staffUsername = staffUsername

    def toTuple(self):
        return (self.id, self.nric, self.quantity, self.date, self.branchId, self.recordedBy)

    @staticmethod
    def fromTuple(data):
        return BloodDonation(*data) # Unpack tuple

    def serialize(self):
        return {
            'id': self.id,
            'nric': self.nric,
            'quantity': self.quantity,
            'date': self.date,
            'branchId': self.branchId,
            'recordedBy': self.recordedBy,
            'usedBy': self.usedBy,
        }

    def deserialize(self, data):
        self.id = data['id']
        self.nric = data['nric']
        self.quantity = data['quantity']
        self.date = data['date']
        self.branchId = data['branchId']
        self.recordedBy = data['recordedBy']
        self.usedBy = data['usedBy']

class BloodRequest:
    def __init__(self, id, requesterId, bloodTypeId, quantity, date, address, status, fulfilled, requester = None, bloodType = None):
        self.id = id
        self.requesterId = requesterId
        self.bloodTypeId = bloodTypeId
        self.quantity = quantity
        self.date = date
        self.address = address
        self.status = status
        self.fulfilled = fulfilled

        self.requester = requester
        self.bloodType = bloodType

    def toTuple(self):
        return (self.id, self.requesterId, self.bloodTypeId, self.quantity, self.date, self.address, self.status, self.fulfilled)

    @staticmethod
    def fromTuple(data):
        return BloodRequest(*data) # Unpack tuple

    def serialize(self):
        return {
            'id': self.id,
            'requesterId': self.requesterId,
            'bloodTypeId': self.bloodTypeId,
            'quantity': self.quantity,
            'date': self.date,
            'address': self.address,
            'status': self.status,
            'fulfilled': self.fulfilled,
            'requester': self.requester,
            'bloodType': self.bloodType,
        }

    def deserialize(self, data):
        self.id = data['id']
        self.requesterId = data['requesterId']
        self.bloodTypeId = data['bloodTypeId']
        self.quantity = data['quantity']
        self.date = data['date']
        self.address = data['address']
        self.status = data['status']
        self.fulfilled = data['fulfilled']
        self.requester = data['requester']
        self.bloodType = data['bloodType']

class Branch:
    def __init__(self, id, name, address, postalCode):
        self.id = id
        self.name = name
        self.address = address
        self.postalCode = postalCode

    def toTuple(self):
        return (self.id, self.name, self.address, self.postalCode)

    @staticmethod
    def fromTuple(data):
        return Branch(*data) # Unpack tuple

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