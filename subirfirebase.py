from typing import Counter
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
from dotenv import load_dotenv
load_dotenv()

# Fetch the service account key JSON file contents
cred = credentials.Certificate('./assets/gremiowarbotpy-firebase-adminsdk-n4ph5-54aa378e6b.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
})
# As an admin, the app has access to read and write all data, regradless of Security Rules

causamuerte =  open("./listas/CausaMuerte.txt","r", encoding="utf-8")
lineas = causamuerte.read().splitlines()
refBaseDatos = db.reference("causamuerte")
counter = 0
for linea in lineas:
    if counter == 0:
        linea = linea[1:]
    print(str(counter)+": "+linea)
    refCausaMuerte = refBaseDatos.child(str(counter))
    refCausaMuerte.set(linea)
    counter+=1
