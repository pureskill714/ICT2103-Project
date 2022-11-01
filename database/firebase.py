
import google.cloud.firestore_v1 as gcloudfirestore
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodInventory, BloodRequest, Branch, Donor, User
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
    def bloodrequest_ref(self):
        return self.db.collection('bloodrequest')

    
    @property
    def branch_ref(self):
        return self.db.collection('branch')
    
    @property
    def bloodtypes_ref(self):
        return self.db.collection('bloodtype')

    @property
    def role_ref(self):
        return self.db.collection('role')

    def login(self, username, password):
        '''User authentication. Return the user if successful or None'''
        userDocs = self.users_ref.where('username', '==', username).where('password', '==', password).get()
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
            # Convert Date string to date format
            donorDict["dateOfBirth"] = datetime.strptime(donorDict["dateOfBirth"], '%Y-%m-%d').date()
            donorList.append(Donor.fromDict(donorDict))
            
        return donorList
                 
    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        donorsDocs = self.donors_ref.where('nric', '==', nric).get()
        if len(donorsDocs) == 1:
            donorDict = donorsDocs[0].to_dict()
            return  Donor.fromDict(donorDict)
        return None

       

    def getDonorDonations(self, nric: str):
        '''Query one donor's donation records'''
        donorDocs = self.donors_ref.where('nric', '==', nric)
        donationDocs = donorDocs.collection(u'blooddonations').get()
        donationDict = donationDocs[0].to_dict()
        return Donor.fromDict(donationDict)
    
   
       
    def insertDonor(self, donor: Donor):
        data = {
            'nric':donor.nric,
            'name':donor.name,
            'dateOfBirth':donor.dateOfBirth,
            'contactNo':donor.contactNo,
            'bloodType':donor.bloodType,
            'registrationDate':donor.registrationDate} 
        self.donors_ref.add(data)
        
        
    def updateDonor(self, donor: Donor):
        #get donor id
        donorDocs = self.donors_ref.where('nric', '==', donor.nric).get()
        donorDict = donorDocs[0].to_dict()
        donorDict["id"] = donorDocs[0].id
        #Update Query
        data={
            'nric':donor.nric,
            'name':donor.name,
            'dateOfBirth':donor.dateOfBirth,
            'contactNo':donor.contactNo,
            'bloodType':donor.bloodType}
        self.donors_ref.document(donorDict['id']).update(data)
       

    def deleteDonorByNRIC(self, nric: str):
        #get donor id
        donorDocs = self.donors_ref.where('nric', '==', nric).get()
        if donorDocs[0].exists:
            self.donors_ref.document(donorDocs[0].id).delete()   


    def getAllBloodDonations(self):
        donationList = []
        donationDocs = self.db.collection_group(u'blooddonations').get()
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
        #get donor id
        donorDocs = self.donors_ref.where('nric', '==', donation.nric).get()
        donorDict = donorDocs[0].to_dict()
        donorDict["id"] = donorDocs[0].id
        #Insert Query
        data={
            'nric':donation.nric,
            'branchId':donation.branchId,
            'date':donation.date,
            'quantity':donation.quantity,
            'recordedBy':donation.recordedBy } 
        self.donors_ref.document(donorDict['id']).collection('blooddonations').add(data)
     
       
    def getAllBloodRequests(self):
        '''Query list of all blood requests'''
        bloodRequestList = []
        bloodRequestDocs = self.bloodrequest_ref.stream()
        for doc in bloodRequestDocs:
            bloodRequestDict = doc.to_dict()
            bloodRequestDict["id"] = doc.id
            #Retrieve matching bloodtype name 
            bloodTypeDoc = self.bloodtypes_ref.document(str(bloodRequestDict["bloodTypeId"])).get()
            bloodTypeDict = bloodTypeDoc.to_dict()
            bloodRequestDict["bloodType"] = bloodTypeDict["type"]
            #Retrieve matching branch username 
            userDoc = self.users_ref.document(str(bloodRequestDict["requesterId"])).get()
            userDict = userDoc.to_dict()
            bloodRequestDict["requestorUsername"] = userDict["username"]
            bloodRequestList.append(bloodRequestDict)
        return bloodRequestList

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
        return btDict['id'] if btDict is not None else None
      

    def getDashboardStats(self):
        # to fixed total avail blood
        donorDocs = self.donors_ref.get()
        requestDocs =self.bloodrequest_ref.where('fulfilled', '==', 0).get()
       # donationDocs = self.db.collection_group(u'blooddonations').get()
        res = (len(donorDocs),20,len(requestDocs))
        return res
        
    def getBloodInventoryByBranchId(self, branchId):
        '''Query blood inventory data
        Returns: BloodInventory
        '''
        inventory = BloodInventory(branchId)
        inventory.storage['A+'] = 100
        return inventory