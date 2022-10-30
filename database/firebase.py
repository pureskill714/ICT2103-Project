
import google.cloud.firestore as gcloudfirestore
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodRequest, Branch, Donor, User
from datetime import datetime

class FirebaseBackend:
    def __init__(self):
        self.creds = credentials.Certificate('database/serviceAccountKey.json')
        self.app = initialize_app(self.creds) 
        self.db: gcloudfirestore.Client = firestore.client()
        super().__init__()

    def commit(self):
        pass

    @property
    def users_ref(self):
        return self.db.collection('users')

    @property
    def donors_ref(self):
        return self.db.collection('donors')

    @property
    def donation_ref(self):
        return self.db.collection('donations')
    
    @property
    def branch_ref(self):
        return self.db.collection('branch')
    
    @property
    def bloodtypes_ref(self):
        return self.db.collection('bloodtype')

    @property
    def role_ref(self):
        return self.db.collection('role')

    def getUserByUsername(self, username):
        userDocs = self.users_ref.where('username', '==', username).get()
        if len(userDocs) == 1:
            doc = userDocs[0].to_dict()
            return User.fromDict(doc)
        return None

    def getUserById(self, id):
        # The document uid can be used as the user ID
        userDocs = self.users_ref.document(id).get()
        return User.fromDict(userDocs.to_dict())

    def getAllDonors(self):
        '''Query list of all donors''' 
        donorList = []
        donorDocs = self.donors_ref.stream()
        for doc in donorDocs:
            donorDict = doc.to_dict()
            donorDict["id"] = doc.id
            #Convert Date string to date format
            date_str = str(donorDict["dateOfBirth"])
            date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
            donorDict["dateOfBirth"] = date_object
            #Retrieve matching donor bloodtype
            btDocs = self.bloodtypes_ref.document(str(donorDict["bloodTypeId"])).get()
            btDict = btDocs.to_dict()
            donorDict["bloodType"] = btDict["type"]
            donorList.append(donorDict)
        return donorList
                 
    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        donorsDocs = self.donors_ref.where('nric', '==', nric).get()
        donorDict = donorsDocs[0].to_dict()
        return Donor.fromDict(donorDict)
       

    def getDonorDonations(self, nric: str):
        '''Query one donor's donation records'''
        donationDocs = self.donation_ref.where('nric', '==', nric).get()
        donationDict = donationDocs[0].to_dict()
        return Donor.fromDict(donationDict)

        

    def insertDonor(self, donor: Donor):
        data={'nric':donor.nric,'name':donor.name,'dateOfBirth':donor.dateOfBirth,'contactNo':donor.contactNo,'bloodTypeId':donor.bloodTypeId,'registrationDate':donor.registrationDate} 
        self.donors_ref.add(data)
        
        
       

    def updateDonor(self, donor: Donor):
        #to be implemneted
        pass
       

    def deleteDonorByNRIC(self, nric: str):
        #to be implemneted
        pass
      

    def getAllBloodDonations(self):
        donationList = []
        donationDocs = self.donation_ref.stream()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            donationDict["id"] = doc.id
            #Retrieve matching branch name 
            branchDoc = self.branch_ref.document(str(donationDict["branchId"])).get()
            branchDict = branchDoc.to_dict()
            donationDict["branchName"] = branchDict["name"]
            #Retrieve matching branch username 
            userDoc = self.users_ref.document(str(donationDict["recordedBy"])).get()
            userDict = userDoc.to_dict()
            donationDict["staffUsername"] = userDict["username"]
            donationList.append(donationDict)
        return donationList


    def insertDonation(self, donation: BloodDonation):
        #to be implemneted
        pass
       

    def getAllBranches(self):
        branchList = []
        branchDocs = self.branch_ref.stream()
        for doc in branchDocs:
            branchDict = doc.to_dict()
            branchDict["id"] = doc.id
            branchList.append(branchDict)
        return branchList


    def getBloodTypeId(self, bloodType):
        btDocs = self.bloodtypes_ref.where('type', '==', bloodType).get()
        btDict = btDocs[0].to_dict()
        return btDict['id']


    def getDashboardStats(self):
        #to be implemneted
        res = (20,20,20)
        return res
        
        