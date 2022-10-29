
from firebase_admin import credentials, firestore, initialize_app

from database.models import BloodDonation, BloodRequest, Branch, Donor, User

class FirebaseBackend:
    def __init__(self):
        self.creds = credentials.Certificate('.\database\serviceAccountKey.json')
        self.app = initialize_app(self.creds) 
        self.db = firestore.client()
        super().__init__()

    @property
    def users_ref(self):
        return self.db.collection('users')

    @property
    def donors_ref(self):
        return self.db.collection('donors')

    @property
    def role_ref(self):
        return self.db.collection('role')

    def getUserByUsername(self, username):
            docs = self.users_ref.where('username', '==', username).stream()
            for doc in docs:
                result = doc.to_dict()
                return result


            
        