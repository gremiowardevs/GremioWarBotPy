import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import asyncio

# Fetch the service account key JSON file contents
cred = credentials.Certificate('gremiowarbotpy-firebase-adminsdk-n4ph5-54aa378e6b.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gremiowarbotpy-default-rtdb.firebaseio.com/'
})
# As an admin, the app has access to read and write all data, regradless of Security Rules

causamuerte =  open("CausaMuerte.txt","r")

lineas = causamuerte.readlines()

refBaseDatos = db.reference('causamuerte')

counter = 0
for linea in lineas:
    print(str(counter)+": "+linea)
    refCausaMuerte = refBaseDatos.child(str(counter))
    refCausaMuerte.set(linea)
    counter+=1
