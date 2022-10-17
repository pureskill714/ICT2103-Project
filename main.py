from datetime import date, datetime
from database.mariadb import MariaDBBackend
from database.models import Donor

def main():
    db = MariaDBBackend()
    print(db.getDonors())
    print(db.getDonorByNRIC('S9991111A'))

    db.deleteDonorByNRIC('S9991111B')
    db.commit()

    donorA = Donor('S9991111B', 'Test Insert', date.today(), '90000001', 1, datetime.utcnow())
    db.insertDonor(donorA)
    db.commit()

    donorA.bloodTypeId = '4'
    donorA.contactNo = '99990001'
    db.updateDonor(donorA)
    db.commit()
main()