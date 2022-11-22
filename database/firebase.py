
import google.cloud.firestore_v1 as gcloudfirestore
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodInventory, BloodRequest, Branch, DashboardData, Donor, User
from datetime import datetime, timezone

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
    def branches_ref(self):
        return self.db.collection('branches')

    def login(self, username, password):
        '''User authentication. Return the user if successful or None'''
        userDocs = self.users_ref.where('username', '==', username).where('password', '==', password).get()
        if len(userDocs) == 1:
            doc = userDocs[0].to_dict()
            return User.fromDict(doc)
        return None

    def register(self, user: User):
        '''User registration. Return the user if successful or None'''
        self.users_ref.add(user.serialize())
        return self.login(user.username, user.password)

    def getUserById(self, id):
        # The document uid can be used as the user ID
        userDoc = self.users_ref.where('id', '==', int(id)).get()
        if len(userDoc) == 1:
            doc = userDoc[0].to_dict()
            return User.fromDict(doc)
        return None

    def getAllDonors(self):
        '''Query list of all donors''' 
        donorList = []
        donorDocs = self.donors_ref.stream()
        for doc in donorDocs:
            donorDict = doc.to_dict()
            donorList.append(Donor.fromDict(donorDict))
        return donorList
                 
    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        donorsDocs = self.donors_ref.where('nric', '==', nric).get()
        if len(donorsDocs) == 1:
            donorDict = donorsDocs[0].to_dict()
            return Donor.fromDict(donorDict)
        return None
    
    def insertDonor(self, donor: Donor):
        data = donor.serialize()
        data['dateOfBirth'] = donor.dateOfBirth # Don't serialize date
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
            # Retrieve matching blood type
            donorDoc = doc.reference.parent.parent.get()
            donationDict["bloodType"] = donorDoc.get("bloodType")
            # Retrieve matching branch name
            branchDoc = self.branches_ref.document(donationDict['branchId']).get()
            donationDict["branchName"] = branchDoc.get("name")
            # Retrieve matching branch username 
            userDoc = self.users_ref.where('id', '==', int(donationDict["recordedBy"])).get()
            donationDict["staffUsername"] = userDoc[0].get("username")
            donationList.append(BloodDonation.fromDict(donationDict))
            donationList.sort(key=lambda d: d.date, reverse=True)
        return donationList

    def getDonationsIdsByRequestId(self, id):
        '''Query all blood donation ids used to fulfill the request with given id.'''
        donationList = []
        donationDocs = self.db.collection_group(u'blooddonations').get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            donationDict["id"] = doc.id
            if donationList["id"] == id:
                donationList.append(donationList["id"])
        return donationList
       
                  
    def getAvailableDonationsByBloodType(self, bloodType: str):
        '''Query donation records not yet used for request fulfillment by blood type'''
        donationList = []
        donationDocs = self.db.collection_group(u'blooddonations').where('usedBy','==',None).get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            donationDict["id"] = doc.id
            branchDoc = self.branches_ref.document(donationDict['branchId']).get()
            branchDict = branchDoc.to_dict()
            donationDict["branchName"] = branchDict["name"]
            # Retrieve matching branch username 
            userDoc = self.users_ref.where('id', '==', int(donationDict["recordedBy"])).get()
            donationDict["staffUsername"] = userDoc[0].to_dict()["username"]
            #filter by bloodtype
            parentRef = doc.reference.parent.parent.get()
            parentDict = parentRef.to_dict()
            if parentDict['bloodType'] == bloodType:
                donationList.append(BloodDonation.fromDict(donationDict))
        return donationList
                
    def insertDonation(self, donation: BloodDonation):
        donation.date = datetime.utcnow() # Firestore assumes datetime in UTC
        # Get donor id
        donorDocs = self.donors_ref.where('nric', '==', donation.nric).get()
        # Insert donation
        data={
            'nric':donation.nric,
            'branchId':donation.branchId,
            'date':donation.date,
            'quantity':donation.quantity,
            'recordedBy':donation.recordedBy,
            'usedBy': None} 
        self.donors_ref.document(donorDocs[0].id).collection('blooddonations').add(data)
           
    def getAllRequests(self):
        '''Query list of all blood requests'''
        bloodRequestList = []
        bloodRequestDocs = self.bloodrequest_ref.stream()
        for doc in bloodRequestDocs:
            bloodRequestDict = doc.to_dict()
            bloodRequestDict["id"] = doc.id
            # Convert date string to datetime
            bloodRequestDict["date"] = datetime.fromisoformat(bloodRequestDict["date"])
            userDoc = self.users_ref.document(str(bloodRequestDict["requesterId"])).get()
            # Retrieve matching requester username 
            bloodRequestDict["requester"] = userDoc.get('username')
            bloodRequestList.append(BloodRequest.fromDict(bloodRequestDict))
        return bloodRequestList

    def getRequestById(self, id):
        '''Query blood requests by request id'''
        bloodRequestDocs = self.bloodrequest_ref.stream()
        for doc in bloodRequestDocs:
            bloodRequestDict = doc.to_dict()
            bloodRequestDict["id"] = doc.id
            if bloodRequestDict["id"] == id:
                # Convert date string to datetime
                bloodRequestDict["date"] = datetime.fromisoformat(bloodRequestDict["date"])
                #Retrieve matching branch username 
                userDoc = self.users_ref.document(str(bloodRequestDict["requesterId"])).get()
                userDict = userDoc.to_dict()
                bloodRequestDict["requester"] = userDict["username"]
                return BloodRequest.fromDict(bloodRequestDict)

    def insertRequest(self, req: BloodRequest):
        data = {
            'address':req.address,
            'bloodType':req.bloodType,
            'date': str(req.date),
            'fufilled':req.fulfilled,
            'quantity':req.quantity,
            'requesterId':req.requesterId,
            'status':req.status} 
        self.bloodrequest_ref.add(data)
        

    def fulfillRequest(self, requestId: str, donationIds: list[str]):

        donationDocs = self.db.collection_group(u'blooddonations').get()
        for doc in donationDocs:
            donationDict = doc.to_dict()
            donationDict["id"] = doc.id
            for ids in donationIds:
                if donationDict["id"] == ids:
                    parentRef = doc.reference.parent.parent.get()
                    parentDict = parentRef.to_dict()
                    parentDict['id'] = parentRef.id
                    self.donors_ref.document(parentDict['id']).collection('blooddonations').document(donationDict['id']).update({'usedBy': requestId})         
                
        self.bloodrequest_ref.document(requestId).update({'status':'Delivered','fulfilled':1})
    
    def getAllBranches(self):
        branchDocs = self.branches_ref.get()
        branches = []
        for doc in branchDocs:
            data = doc.to_dict()
            data['id'] = doc.id
            branches.append(Branch.fromDict(data))
        return branches
      
    def getDashboardStats(self, branchId):
        donorDocs = self.donors_ref.get()
        availableBlood = 0
        pendingRequestDocs =self.bloodrequest_ref.where('fulfilled', '==', 0).get()
        donationsThisWeek = 0
        bloodQtyThisWeek = 0
        
        donationDocs = self.db.collection_group(u'blooddonations').get()
        for doc in donationDocs:
            bloodQty = int(doc.get("quantity"))
            availableBlood += bloodQty # Calculate total blood available
            date = doc.get("date").astimezone(timezone.utc)
            dateIso = date.isocalendar()
            today = datetime.today()
            todayIso = today.isocalendar()
            if dateIso.week == todayIso.week and date.year == today.year:
                # The date is in the current week
                donationsThisWeek += 1
                bloodQtyThisWeek += bloodQty

        inventory = self.getBloodInventoryByBranchId(branchId)
        res = DashboardData(len(donorDocs), availableBlood, len(pendingRequestDocs), donationsThisWeek, bloodQtyThisWeek, inventory.storage)
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

        
