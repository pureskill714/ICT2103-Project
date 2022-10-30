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
    def __init__(self, nric, name, dateOfBirth, contactNo, bloodTypeId, registrationDate, bloodType = None):
        self.nric = nric
        self.name = name
        self.dateOfBirth = dateOfBirth
        self.contactNo = contactNo
        self.bloodTypeId = bloodTypeId
        self.registrationDate = registrationDate
        self.bloodType = bloodType

    def toTuple(self):
        return (self.nric, self.name, self.dateOfBirth, self.contactNo, self.bloodTypeId, self.registrationDate)

    @staticmethod
    def fromTuple(data):
        return Donor(*data) # Unpack tuple

class BloodDonation:
    def __init__(self, donationId, donorNRIC, quantity, date, branchId, recordedBy, branchName = None, staffUsername = None):
        self.id = donationId
        self.nric = donorNRIC
        self.quantity = quantity
        self.date = date
        self.branchId = branchId
        self.recordedBy = recordedBy

        self.branchName = branchName
        self.staffUsername = staffUsername

    def toTuple(self):
        return (self.id, self.nric, self.quantity, self.date, self.branchId, self.recordedBy)

    @staticmethod
    def fromTuple(data):
        return BloodDonation(*data) # Unpack tuple

class BloodRequest:
    def __init__(self, id, requesterId, bloodTypeId, quantity, date, address, status, fulfilled, requestorUsername = None, bloodType = None):
        self.id = id
        self.requesterId = requesterId
        self.bloodTypeId = bloodTypeId
        self.quantity = quantity
        self.date = date
        self.address = address
        self.status = status
        self.fulfilled = fulfilled

        self.requestorUsername = requestorUsername
        self.bloodType = bloodType

    def toTuple(self):
        return (self.id, self.requesterId, self.bloodTypeId, self.quantity, self.date, self.address, self.status, self.fulfilled)

    @staticmethod
    def fromTuple(data):
        return BloodRequest(*data) # Unpack tuple

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