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
from PIL import Image, ImageDraw, ImageFont
import datetime

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
def fbpost(msg,imgpath):

    with open(imgpath,'r') as token:
        accesstoken = token.readline()
    graph = facebook.GraphAPI(accesstoken)
    post_id = graph.put_photo(image=open("./assets/weareback.png","rb"),message = msg)['post_id']
    print(f"Mensaje \"{msg}\" y publicación subida correctamente!")

def evento():
    print("OCURRIÓ UN EVENTO")

    seed(calendar.timegm(time.gmtime()))

    id_causa_muerte = randint(0, 37)
    causa_muerte = db.reference("causamuerte/"+str(id_causa_muerte)).get()
    listaParticipantes = db.reference("primerEvento/participantes").get()
    listaVivos = []

    for key in listaParticipantes:
        if(key['vivo']):
            listaVivos.append(key)


    tamano_lista_vivos = len(listaVivos)

    id_vencedor_listavivos = randint(0, tamano_lista_vivos-1)
    id_derrotado_listavivos = randint(0,tamano_lista_vivos-1)
    while(id_vencedor_listavivos == id_derrotado_listavivos):
        id_derrotado_listavivos = randint(0,tamano_lista_vivos-1)

    vencedor = listaVivos[id_vencedor_listavivos]
    derrotado = listaVivos[id_derrotado_listavivos]
    id_evento= datetime.datetime.now().strftime("%d%m%Y-%H%M%S")+"-"+str(vencedor['id'])+"vs"+str(derrotado['id'])

    db.reference("primerEvento/participantes/"+str(derrotado['id'])+"/vivo").set(False)
    db.reference("primerEvento/participantes/"+str(vencedor['id'])+"/killcount").set(vencedor['killcount']+1)

    db.reference("primerEvento/lucha/"+id_evento).set({
        'vencedor':vencedor['nombre'],
        'derrotado':derrotado['nombre'],
        'causamuerte':causa_muerte
    })
    
    listaParticipantes = db.reference("primerEvento/participantes").get()
    topKiller = listaParticipantes[0]
    for key in listaParticipantes:
        if(key['killcount']>topKiller['killcount']):
            topKiller = key
    
    msg_top_killer = "Topkiller hasta el momento:"+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" luchadores vencidos\n"
    msg_batalla = vencedor['nombre']+" "+causa_muerte+" "+derrotado['nombre']+"\n"
    msg_killcount_vencedor = vencedor['nombre']+" lleva un killcount de :"+str(vencedor['killcount']+1)+"\n"
    print("Evento creado")
    print(msg_batalla)
    print(msg_killcount_vencedor)
    print(msg_top_killer)
    
    canvas = Image.new('RGB', (1270,370), 'black')
    img_draw = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype("arial.ttf", 15)
    iterateParticipante = 0
    anchoAux=10
    i = 0
    for i  in range(4):
        largoauxiliar = 5
        j = 0
        for j in range(18):
            if(iterateParticipante < len(listaParticipantes)):
                participante = listaParticipantes[iterateParticipante]
                if(participante['vivo']):
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'],font=fnt, fill='green')
                else:
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'], font=fnt, fill='red')
                largoauxiliar+=20
                iterateParticipante+=1
            else:
                break
        anchoAux+=328
    
    canvas.save('./images/'+id_evento+".png")
    rutaImagen =  './images/'+id_evento+".png"

    if(tamano_lista_vivos == 2):
        db.reference("primerEvento/resultados/ganador/nombre").set(vencedor['nombre'])
        db.reference("primerEvento/resultados/ganador/killcount").set(vencedor['killcount']+1)
        msg_ganador_final = "¡"+vencedor['nombre']+" HA SIDO EL VENCEDOR DE LA PRIMERA TEMPORADA DE VENEZUELA GREMIOMEMEROWARBOT!\n"
        print(msg_ganador_final)
        msg_ganador_killcount = vencedor['nombre']+" venció un total de "+str(vencedor['killcount']+1)+" para ser campeón total.\n"

        listaParticipantes = db.reference("primerEvento/participantes").get()
        topKiller = listaParticipantes[0]

        for key in listaParticipantes:
            if(key['killcount']>topKiller['killcount']):
                topKiller = key

        msg_top_killer_final =  "El topkiller fue "+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" luchadores vencidos\n"
        db.reference("primerEvento/resultados/topkiller/nombre").set(topKiller['nombre'])
        db.reference("primerEvento/resultados/topkiller/killcount").set(topKiller['killcount'])
        print(msg_top_killer_final)

        msg_finalizacion_contienda = msg_batalla+msg_ganador_final+msg_ganador_killcount+msg_top_killer_final
        #Posteo final
        fbpost(msg_finalizacion_contienda,rutaImagen)
        exit()
    else:
        msg_post = msg_batalla+msg_killcount_vencedor+msg_top_killer
        #posteo normal
        fbpost(msg_post,rutaImagen)
           
if __name__ == '__main__':
    token = open('./assets/token.txt', 'r')
    if token.readline() == "putyourtokenherexdd":
        print("put your access token in assets/token.txt. you can obtain the access token from http://maxbots.ddns.net/token/")
        sys.exit("error no token")
    
    schedule.every(10).seconds.do(evento)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    #schedule.every().hour.do(testrun).run()

#   Uncomment line 99 and comment line 97 in order to enable burst mode    
#   schedule.every().hour.do(burst).run()
    #while 1:
       # schedule.run_pending()
       # time.sleep(1)
