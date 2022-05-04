import firebase_admin
from firebase_admin import credentials
import json
import os


firebase_app = None

raw_cred = os.getenv("FIREBASE_CREDENTIAL")
if raw_cred:
    cred_json = json.loads(raw_cred)
    credential = credentials.Certificate(cred_json)
    firebase_app = firebase_admin.initialize_app(
        credential,
        { 
            "databaseURL": "https://minkomni-default-rtdb.firebaseio.com/"
        }
    )
