import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
def initialize_firebase():
    cred = credentials.Certificate("serviceAccounts/quickfix.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://quickfix-cc5a1-default-rtdb.firebaseio.com" # Replace with your database URL
    })
