
import google.cloud.firestore_v1 as gcloudfirestore
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodInventory, BloodRequest, Branch, DashboardData, Donor, User
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


    def getAllDonations(self):
        donationList = []
        donationDocs = self.db.collection_group(u'blooddonations').get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            donationDict["id"] = doc.id
            #Retrieve matching branch name
            branchDoc = self.db.collection_group(u'branch').where('branchId', '==' , int(donationDict['branchId'])).get()
            for docs in branchDoc:
                branchDict = docs.to_dict()
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
     
       
    def getAllRequests(self):
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
        branchDocs = self.db.collection_group(u'branch').get()
        for doc in branchDocs:
            branchDict = doc.to_dict()
            branchDict["id"] = doc.id
            branchList.append(branchDict)
        return branchList


    def getBloodTypeId(self, bloodType):
        btDocs = self.bloodtypes_ref.where('type', '==', bloodType).get()
        btDict = btDocs[0].to_dict()
        btDict['id'] = btDocs[0].id
        return btDict['id'] if btDict is not None else None
      

    def getDashboardStats(self, branchId):
        donorDocs = self.donors_ref.get()
        requestDocs =self.bloodrequest_ref.where('fulfilled', '==', 0).get()
        #Get total blood donation quantity
        bloodQuantityList = []
        donationDocs = self.db.collection_group(u'blooddonations').get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            bloodQuantity = int(donationDict["quantity"])
            bloodQuantityList.append(bloodQuantity)
            totalQuantity= sum(bloodQuantityList)
        inventory = self.getBloodInventoryByBranchId(branchId)
        res = DashboardData(len(donorDocs),totalQuantity,len(requestDocs), inventory.storage)
        return res
        
    def getBloodInventoryByBranchId(self, branchId):
        '''Query blood inventory data
        Returns: BloodInventory
        '''
        APtotalQuantity = 0
        AMtotalQuantity = 0
        BPtotalQuantity = 0
        BMtotalQuantity = 0
        ABPtotalQuantity = 0
        ABMtotalQuantity = 0
        OPtotalQuantity = 0
        OMtotalQuantity = 0

        APbloodQuantityList = []
        AMbloodQuantityList = []
        BPbloodQuantityList = []
        BMbloodQuantityList = []
        ABPbloodQuantityList = []
        ABMbloodQuantityList = []
        OPbloodQuantityList = []
        OMbloodQuantityList = []

        donationDocs = self.db.collection_group(u'blooddonations').where('branchId','==',str(branchId)).get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            parentRef = doc.reference.parent.parent.get()
            parentDict = parentRef.to_dict()
            if parentDict['bloodType'] == 'A+':
                APbloodQuantity = int(donationDict["quantity"])
                APbloodQuantityList.append(APbloodQuantity)
                APtotalQuantity= sum(APbloodQuantityList)
            elif parentDict['bloodType'] == 'A-':
                AMbloodQuantity = int(donationDict["quantity"])
                AMbloodQuantityList.append(AMbloodQuantity)
                AMtotalQuantity= sum(AMbloodQuantityList)
            elif parentDict['bloodType'] == 'B+':
                BPbloodQuantity = int(donationDict["quantity"])
                BPbloodQuantityList.append(BPbloodQuantity)
                BPtotalQuantity= sum(BPbloodQuantityList)
            elif parentDict['bloodType'] == 'B-':
                BMbloodQuantity = int(donationDict["quantity"])
                BMbloodQuantityList.append(BMbloodQuantity)
                BMtotalQuantity= sum(BMbloodQuantityList)
            elif parentDict['bloodType'] == 'AB+':
                ABPbloodQuantity = int(donationDict["quantity"])
                ABPbloodQuantityList.append(ABPbloodQuantity)
                ABPtotalQuantity= sum(ABPbloodQuantityList)
            elif parentDict['bloodType'] == 'AB-':
                ABMbloodQuantity = int(donationDict["quantity"])
                ABMbloodQuantityList.append(ABMbloodQuantity)
                ABMtotalQuantity= sum(ABMbloodQuantityList)
            elif parentDict['bloodType'] == 'O+':
                OPbloodQuantity = int(donationDict["quantity"])
                OPbloodQuantityList.append(OPbloodQuantity)
                OPtotalQuantity= sum(OPbloodQuantityList)
            elif parentDict['bloodType'] == 'O-':
                OMbloodQuantity = int(donationDict["quantity"])
                OMbloodQuantityList.append(OMbloodQuantity)
                OMtotalQuantity= sum(OMbloodQuantityList)

        inventory = BloodInventory(branchId)
        inventory.storage['A+'] = APtotalQuantity
        inventory.storage['A-'] = AMtotalQuantity
        inventory.storage['B+'] = BPtotalQuantity
        inventory.storage['B-'] = BMtotalQuantity
        inventory.storage['AB+'] = ABPtotalQuantity
        inventory.storage['AB-'] = ABMtotalQuantity
        inventory.storage['O+'] = OPtotalQuantity
        inventory.storage['O-'] = OMtotalQuantity
        return inventory

        
