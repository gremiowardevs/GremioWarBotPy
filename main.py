# Codigo original de Posteo escrito po  Boidushya Bhattacharya y Gustav Wallström (github/sudoxd) on Monday, 26 November 2019 at 20:27 p.m.
# Codigo de bot de lucha creado por Carlos Ardila (github/carlosardilap)
#Facebook: https://facebook.com/Charles145
#Twitter: https://twitter.com/ArdilaVene
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
cred = credentials.Certificate('./assets/gremiowarbotpy-firebase-adminsdk-n4ph5-54aa378e6b.json')

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
##Posteo en Facebook de un mensaje con imagen
def fbpost(msg,imgpath):
    with open('./assets/token.txt','r') as token:
        accesstoken = token.readline()
    graph = facebook.GraphAPI(accesstoken)
    post_id = graph.put_photo(image=open(imgpath,"rb"),message = msg)['post_id']
    print(f"Mensaje \"{msg}\" y publicación subida correctamente!")


##Intentar realizar una lucha
def realizarLucha():

    #VERIFICACION SI EL EVENTO ESTÁ FUNCIONANDO
    if(not(db.reference("primerEvento/estado").get())):
        print("¡No quedan suficientes participantes vivos!")
        exit()
    
    print("OCURRIÓ UNA LUCHA")

    #Seed para generar un numero pseudo random (Se utiliza la hora para generarlo)
    seed(calendar.timegm(time.gmtime()))

    #Se obtiene un tipo de muerte al azar
    lista_tipo_muerte =  db.reference("causamuerte/").get()
    causa_muerte = lista_tipo_muerte[randint(0, len(lista_tipo_muerte)-1)]

    #Se obtiene la lista de participantes
    listaParticipantes = db.reference("primerEvento/participantes").get()
    listaVivos = []

    topKiller = listaParticipantes[0] #Se inicializa el topkiller para buscarlo

    #Se recorre la lista de participantes y se agregan los participantes vivos a una lista auxiliar
    for participante in listaParticipantes:
        if(participante['killcount']>topKiller['killcount']):
            topKiller = participante

        if(participante['vivo']):
            listaVivos.append(participante)


    #Se obtiene el tamano de la lista vivos
    tamano_lista_vivos = len(listaVivos)
    
    #Se obtiene un id random de un vencedor y un derrotado
    id_vencedor_listavivos = randint(0, tamano_lista_vivos-1)
    id_derrotado_listavivos = randint(0,tamano_lista_vivos-1)

    #Si el id del vencedor se repite, se busca otro numero random para el derrotado
    while(id_vencedor_listavivos == id_derrotado_listavivos):
        id_derrotado_listavivos = randint(0,tamano_lista_vivos-1)

    #Se obtienen el vencedor y el derrotado con sus respectivos id
    vencedor = listaVivos[id_vencedor_listavivos]
    derrotado = listaVivos[id_derrotado_listavivos]

    #Se genera el id de un evento con este formato "ddmmaaaa-hhmmss-IDVENCEDORvsIDDERROTADO
    id_evento= datetime.datetime.now().strftime("%d%m%Y-%H%M%S")+"-"+str(vencedor['id'])+"vs"+str(derrotado['id'])

    #En la base de datos se le asigna falso al estado de vivo del usuario derrotado
    db.reference("primerEvento/participantes/"+str(derrotado['id'])+"/vivo").set(False)

    #Se aumenta el killcount del vencedor
    db.reference("primerEvento/participantes/"+str(vencedor['id'])+"/killcount").set(vencedor['killcount']+1)
    vencedor['killcount']+=1
    (listaParticipantes[derrotado['id']])['vivo'] = False
    (listaParticipantes[vencedor['id']])['killcount'] += 1

    #Si el vencedor supera en killcount al topkiller se convierte en el nuevo topkiller
    if(vencedor['killcount']>topKiller['killcount']):
        topKiller = vencedor

    #Se crea un evento en la base de datos con el nombre del vencedor, el nombre del derrotado y la causa de la muerte.
    db.reference("primerEvento/lucha/"+id_evento).set({
        'vencedor':vencedor['nombre'],
        'derrotado':derrotado['nombre'],
        'causamuerte':causa_muerte
    })

    #Se actualiza internamente la cantidad de participantes que quedan vivos
    tamano_lista_vivos-=1

    #Se crean los mensajes para postear
    msg_batalla = vencedor['nombre']+" "+causa_muerte+" "+derrotado['nombre']+".\n"
    msg_killcount_vencedor = vencedor['nombre']+" lleva un killcount de: "+str(vencedor['killcount'])+".\n"
    msg_restantes = "Quedan "+str(tamano_lista_vivos)+" vivos.\n"
    msg_top_killer = "Topkiller hasta el momento: "+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" contrincantes vencidos.\n"
    
    canvas = Image.new('RGB', (1410,745), 'black')
    img_draw = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype("BOOKOS.TTF", 20)
    fnt2 = ImageFont.truetype("BOOKOS.TTF", 15)
    iterateParticipante = 0
    anchoAux=20
    
    for i  in range(0,4):
        largoauxiliar = 15
        for j in range(0,25):
            if(iterateParticipante < len(listaParticipantes)):
                participante = listaParticipantes[iterateParticipante]
                if(participante['vivo']):
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'],font=fnt, fill='white')
                else:
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'], font=fnt, fill='red')
                largoauxiliar+=25
                iterateParticipante+=1
            else:
                break
        anchoAux+=345

    listaTopKillers = sorted(listaParticipantes, key = lambda i: i['killcount'],reverse=True)

    img_draw.text((10,largoauxiliar+15),"TOP 3 Killers:",font=fnt, fill='white')

    if listaTopKillers[0]!=None:
        img_draw.text((35,largoauxiliar+35),"1. "+(listaTopKillers[0])['nombre']+" : "+str((listaTopKillers[0])['killcount']),font=fnt, fill='white')
    if listaTopKillers[1]!=None:
        img_draw.text((35,largoauxiliar+55),"2. "+(listaTopKillers[1])['nombre']+" : "+str((listaTopKillers[1])['killcount']),font=fnt, fill='white')
    if listaTopKillers[2]!=None:
        img_draw.text((35,largoauxiliar+75),"3. "+(listaTopKillers[2])['nombre']+" : "+str((listaTopKillers[2])['killcount']),font=fnt, fill='white')

    img_draw.text((500,largoauxiliar+15),"Fecha Evento: "+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),font=fnt, fill='white')
    img_draw.text((500,largoauxiliar+35),msg_batalla,font=fnt, fill='white')

    #Se guarda la imagen y la ruta de la misma
    canvas.save('./images/'+id_evento+".png")
    rutaImagen =  './images/'+id_evento+".png"

    #Si solamente queda vivo un participante
    if(tamano_lista_vivos == 1):
        #Se guarda en la base de datos el vencedor y su killcount
        db.reference("primerEvento/resultados/ganador/nombre").set(vencedor['nombre'])
        db.reference("primerEvento/resultados/ganador/killcount").set(vencedor['killcount'])

        #Variables de mensaje de vencedor final
        msg_ganador_final = "¡"+vencedor['nombre']+" HA SIDO EL VENCEDOR DE LA PRIMERA TEMPORADA DE VENEZUELA GREMIOMEMEROWARBOT!\n"
        msg_ganador_killcount = vencedor['nombre']+" venció un total de "+str(vencedor['killcount'])+" para ser campeón total.\n"
        msg_top_killer_final =  "El topkiller fue "+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" contrincantes vencidos\n"

        #Se desactiva el torneo
        db.reference("primerEvento/estado").set(False)

        #Se guarda cual fue el topkiller
        db.reference("primerEvento/resultados/topkiller/nombre").set(topKiller['nombre'])
        db.reference("primerEvento/resultados/topkiller/killcount").set(topKiller['killcount'])
        msg_finalizacion_contienda = msg_batalla+msg_ganador_final+msg_ganador_killcount+msg_top_killer_final
        print(msg_finalizacion_contienda)

        #Posteo final
        #fbpost(msg_finalizacion_contienda,rutaImagen)

        #Se cierra el script
        exit()
    else:
        msg_post = msg_batalla+msg_killcount_vencedor+msg_restantes+msg_top_killer
        print(msg_post)
        #posteo normal
        #fbpost(msg_post,rutaImagen)

def testGenerarImagen():
    listaParticipantes = db.reference("primerEvento/participantes").get()
    canvas = Image.new('RGB', (1390,735), 'black')
    img_draw = ImageDraw.Draw(canvas)
    fnt = ImageFont.truetype("BOOKOS.TTF", 20)
    iterateParticipante = 0
    anchoAux=10

    for i  in range(0,4):
        largoauxiliar = 5
        for j in range(0,25):
            if(iterateParticipante < len(listaParticipantes)):
                participante = listaParticipantes[iterateParticipante]
                if(participante['vivo']):
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'],font=fnt, fill='white')
                else:
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'], font=fnt, fill='white')
                largoauxiliar+=25
                iterateParticipante+=1
            else:
                break
        anchoAux+=345
    
    canvas.save('./images/testingBot.png')


def reiniciarEvento():
    filetexto =  open("./listas/Participantes.txt","r", encoding="utf-8")
    db.reference("primerEvento/estado").set(True)
    lineas = filetexto.read().splitlines()
    refBaseDatos = db.reference("primerEvento/participantes")
    counter = 0
    for linea in lineas:
        if counter == 0:
            linea = linea[1:]
        print(str(counter)+": "+linea)
        refCausaMuerte = refBaseDatos.child(str(counter))
        refCausaMuerte.set({
            'id': counter,
            'nombre': linea,
            'vivo': True,
            'killcount' : 0,
        })
        counter+=1
    db.reference("primerEvento/lucha").delete()
    db.reference("primerEvento/resultados").delete()
    print("EVENTO REINICIADO SE EMPEZARÁ A REALIZAR")

if __name__ == '__main__':
    token = open('./assets/token.txt', 'r')
    if token.readline() == "putyourtokenherexdd":
        print("put your access token in assets/token.txt. you can obtain the access token from http://maxbots.ddns.net/token/")
        sys.exit("error no token")
    
    #VERIFICACION SI EL EVENTO ESTÁ FUNCIONANDO
    if(not(db.reference("primerEvento/estado").get())):
        print("¡No quedan suficientes participantes vivos!")
        ans = input("Reiniciar Evento?(y/n) \n>")
        if 'y' in ans.lower():
            reiniciarEvento()
        else:
            exit()
    
    schedule.every(5).seconds.do(realizarLucha) #USAR SOLO PARA TESTEOS CON FBPOST COMENTADO O ELIMINADO
    #schedule.every().hour.do(testrun).run()
    while True:
        schedule.run_pending()
        time.sleep(1)


    #OJO OJO OJO OJO OJO OJO OJO AL POSTEAR EN FB ES MINIMO 30 MINUTOS
    # NOS PUEDEN MATAR TODO NUESTROS FB SI EL SCRIPT FALLA Y EMPIEZA A SPAMEAR 
    
