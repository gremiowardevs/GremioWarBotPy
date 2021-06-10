#This code was written by Boidushya Bhattacharya and Gustav Wallström (github/sudoxd) on Monday, 26 November 2019 at 20:27 p.m.
#Reddit: https://reddit.com/u/Boidushya
#Facebook: https://facebook.com/soumyadipta.despacito

#import cv2
import os
import math
import facebook
import functools
import schedule
import time
import fnmatch
import sys
from random import seed
from random import randint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import asyncio
import calendar;
import time;

# Fetch the service account key JSON file contents
cred = credentials.Certificate('gremiowarbotpy-firebase-adminsdk-n4ph5-54aa378e6b.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {'databaseURL': 'https://gremiowarbotpy-default-rtdb.firebaseio.com/'})

def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator

# Uncomment the next 5 lines and refer to line 98 if you want the bot to post multiple images at a time
#
#@catch_exceptions()
#def burst():
#  for _ in range(5):
#    post()

@catch_exceptions()
def testingPost():
    msg = "Si estás viendoe esta publicación, significa que, después de dos años, facebook dejo de ponerse popi y el bot podrá funcionar."

    with open('./assets/token.txt','r') as token:
        accesstoken = token.readline()
    graph = facebook.GraphAPI(accesstoken)
    post_id = graph.put_photo(image=open("./assets/weareback.png","rb"),message = msg)['post_id']
    print(f"Mensaje \"{msg}\" y publicación subida correctamente!")

def testrun():
    print("OCURRIÓ UN EVENTO")

    seed(calendar.timegm(time.gmtime()))

    id_causa_muerte = randint(0, 37)
    causa_muerte = db.reference("causamuerte/"+str(id_causa_muerte)).get()
    listaParticipantes = db.reference("primerEvento/participantes").get()
    listaVivos = []

    print("TODOS LOS PARTICIPANTES:")
    for key in listaParticipantes:
        if(key['vivo']):
            print(str(key['id'])+": "+key['nombre']+" [vivo]")
            listaVivos.append(key)
        else:
            print(str(key['id'])+": "+key['nombre']+" [MUERTO]")


    tamano_lista_vivos = len(listaVivos)

    id_vencedor_listavivos = randint(0, tamano_lista_vivos-1)
    id_derrotado_listavivos = randint(0,tamano_lista_vivos-1)
    while(id_vencedor_listavivos == id_derrotado_listavivos):
        id_derrotado_listavivos = randint(0,tamano_lista_vivos)

    vencedor = listaVivos[id_vencedor_listavivos]
    derrotado = listaVivos[id_derrotado_listavivos]

    db.reference("primerEvento/participantes/"+str(derrotado['id'])+"/vivo").set(False)
    db.reference("primerEvento/participantes/"+str(vencedor['id'])+"/killcount").set(vencedor['killcount']+1)

    db.reference("primerEvento/lucha/"+str(vencedor['id'])+"vs"+str(derrotado['id'])).set({
        'vencedor':vencedor['nombre'],
        'derrotado':derrotado['nombre'],
        'causamuerte':causa_muerte
    })

    if(tamano_lista_vivos == 2):
        db.reference("primerEvento/resultados/ganador/nombre").set(vencedor['nombre'])
        db.reference("primerEvento/resultados/ganador/killcount").set(vencedor['killcount']+1)
        msg = "¡"+vencedor['nombre']+" HA SIDO EL VENCEDOR DE LA PRIMERA TEMPORADA DE VENEZUELA GREMIOMEMEROWARBOT!"
        print(msg)
        listaParticipantes = db.reference("primerEvento/participantes").get()
        topKiller = listaParticipantes[0]
        for key in listaParticipantes:
            if(key['killcount']>topKiller['killcount']):
                topKiller = key

        db.reference("primerEvento/resultados/topkiller/nombre").set(topKiller['nombre'])
        db.reference("primerEvento/resultados/topkiller/killcount").set(topKiller['killcount'])
        print("El mayor Killcount fue de: "+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" luchadores vencidos")
        exit()
    
    listaParticipantes = db.reference("primerEvento/participantes").get()
    topKiller = listaParticipantes[0]
    for key in listaParticipantes:
        if(key['killcount']>topKiller['killcount']):
            topKiller = key
    
    print("Evento creado")
    print(vencedor['nombre']+" "+causa_muerte+" "+derrotado['nombre'])
    print(vencedor['nombre']+" lleva un killcount de :"+str(vencedor['killcount']+1))
    print("Top Killer hasta el momento:"+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" luchadores vencidos")
           


if __name__ == '__main__':
    token = open('./assets/token.txt', 'r')
    if token.readline() == "putyourtokenherexdd":
        print("put your access token in assets/token.txt. you can obtain the access token from http://maxbots.ddns.net/token/")
        sys.exit("error no token")
    
    schedule.every(10).seconds.do(testrun)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    #schedule.every().hour.do(testrun).run()

#   Uncomment line 99 and comment line 97 in order to enable burst mode    
#   schedule.every().hour.do(burst).run()
    #while 1:
       # schedule.run_pending()
       # time.sleep(1)
