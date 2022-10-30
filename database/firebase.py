
import google.cloud.firestore as gcloudfirestore
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodRequest, Branch, Donor, User

class FirebaseBackend:
    def __init__(self):
        self.creds = credentials.Certificate('database/serviceAccountKey.json')
        self.app = initialize_app(self.creds) 
        self.db: gcloudfirestore.Client = firestore.client()
        super().__init__()

    @property
    def users_ref(self) -> gcloudfirestore.CollectionReference:
        return self.db.collection('users')

    @property
    def donors_ref(self) -> gcloudfirestore.CollectionReference:
        return self.db.collection('donors')
    
    @property
    def bloodtypes_ref(self) -> gcloudfirestore.CollectionReference:
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
        doc = self.users_ref.document(id).get()
        return User.fromDict(doc.to_dict())

    def getAllDonors(self):
        '''Query list of all donors'''  
    
        #to be fixed currently diplaying only one result
        for doc in self.donors_ref.stream():
            docs = doc.to_dict()
            result = [Donor(docs["nric"],docs["name"],docs["dob"],docs["contact"],docs["bloodtypeID"],docs["regdate"])]
            return result
            

    def getDonorByNRIC(self, nric: str):
        '''Query one donor by NRIC'''
        query_ref = self.donors_ref.where('nric', '==', nric).get()
        docs = query_ref[0].to_dict()
        return Donor(docs["nric"],docs["name"],docs["dob"],docs["contact"],docs["bloodtypeID"],docs["regdate"])
       

    def getDonorDonations(self, nric: str):
        '''Query one donor's donation records'''
        #to be implemneted
        pass
        

    def insertDonor(self, donor: Donor):
        #to be implemneted
        pass
       

    def updateDonor(self, donor: Donor):
        #to be implemneted
        pass
       

    def deleteDonorByNRIC(self, nric: str):
        #to be implemneted
        pass
      

    def getAllBloodDonations(self):
       #to be implemneted
        pass

    def insertDonation(self, donation: BloodDonation):
        #to be implemneted
        pass
       

    def getAllBranches(self):
        #to be implemneted
        pass

    def getBloodTypeId(self, bloodType):
        #to be implemneted
        pass

    def getDashboardStats(self):
        #to be implemneted
        res = (20,20,20)
        return res
        
        