from datetime import date, datetime

from flask_login import UserMixin

# Inheriting from UserMixin required for flask login
class User(UserMixin):
    def __init__(self, id, username, password, name, branchId):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.branchId = branchId

    @staticmethod
    def fromTuple(data):
        return User(*data) # Unpack tuple

class Donor:
    def __init__(self, nric: str, name: str, dateOfBirth: date, mobile: str, bloodTypeId: int, registrationDate: datetime):
        self.nric = nric
        self.name = name
        self.dateOfBirth = dateOfBirth
        self.contactNo = mobile
        self.bloodTypeId = bloodTypeId
        self.registrationDate = registrationDate

    def toTuple(self):
        return (self.nric, self.name, self.dateOfBirth, self.contactNo, self.bloodTypeId, self.registrationDate)

    @staticmethod
    def fromTuple(data):
        return Donor(*data) # Unpack tuple


class BloodDonation:
    def __init__(self, donationId: int, donorNRIC: str, quantity: float, date: datetime, time, branchId):
        self.id = donationId
        self.nric = donorNRIC
        self.quantity = quantity
        self.date = date
        self.time = time
        self.branchId = branchId

    def toTuple(self):
        return (self.id, self.nric, self.quantity, self.date, self.time, self.branchId)

    @staticmethod
    def fromTuple(data):
        return BloodDonation(*data) # Unpack tuple
