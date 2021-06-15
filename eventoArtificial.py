# Codigo original de Posteo escrito po  Boidushya Bhattacharya y Gustav Wallström (github/sudoxd) on Monday, 26 November 2019 at 20:27 p.m.
# Codigo de bot de lucha creado por Carlos Ardila (github/carlosardilap)
#Facebook: https://facebook.com/Charles145
#Twitter: https://twitter.com/ArdilaVene
import facebook
import functools
import schedule
import time
import sys
from random import seed,randint,shuffle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
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


def testGenerarImagen():
    listaParticipantes = db.reference("primerEvento/participantes").get()
    listaParticipantesOrdenada =  sorted(listaParticipantes, key = lambda i: i['nombre'])
    canvas = Image.new('RGB', (1410,760), 'black')
    img_draw = ImageDraw.Draw(canvas)

    #Tipos de Fuente
    fnt = ImageFont.truetype("BOOKOS.TTF", 20)
    
    #Variables auxiliares de iteración de pintado de la Imagen
    iterateParticipante = 0
    anchoAux=20
    
    for i  in range(0,4):
        largoauxiliar = 15
        for j in range(0,27):
            if(iterateParticipante < len(listaParticipantesOrdenada)):
                #Participante vivo blanco/ muerto rojo
                participante = listaParticipantesOrdenada[iterateParticipante]
                if(participante['vivo']):
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'],font=fnt, fill='white')
                else:
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'], font=fnt, fill='red')
                largoauxiliar+=25
                iterateParticipante+=1
            else:
                break
        anchoAux+=350
    canvas.save('./images/testingBot.png')

##Intentar realizar una lucha
def realizarLucha():


    #VERIFICACION SI EL EVENTO ESTÁ FUNCIONANDO
    if(not(db.reference("primerEvento/estado").get())):
        print("¡No quedan suficientes participantes vivos!")
        exit()
    
    print("Creación de lucha artificial")

    idVencedor = input("ID DEL VENCEDOR\n")
    idDerrotado = input("ID DERROTADO\n")
    idCausaMuerte = input("ID causa muerte\n")

    #Seed para generar un numero pseudo random (Se utiliza la hora para generarlo)

    #Se obtiene un tipo de muerte al azar
    causa_muerte =  db.reference("causamuerte/"+str(idCausaMuerte)).get()

    #Se obtiene la lista de participantes
    vencedor = db.reference("primerEvento/participantes/"+str(idVencedor)).get()
    derrotado = db.reference("primerEvento/participantes/"+str(idDerrotado)).get()
    listaParticipantes = db.reference("primerEvento/participantes/").get()

    listaVivos = []

    topKiller = listaParticipantes[0] #Se inicializa el topkiller para buscarlo
    #Se recorre la lista de participantes y se agregan los participantes vivos a una lista auxiliar
    tamano_lista_vivos = 0
    for participante in listaParticipantes:
        if(participante['killcount']>topKiller['killcount']):
            topKiller = participante
        if participante['vivo']:
            tamano_lista_vivos+=1

    

    #Se genera el id de un evento con este formato "ddmmaaaa-hhmmss-IDVENCEDORvsIDDERROTADO
    id_evento= datetime.datetime.now().strftime("%d%m%Y-%H%M%S")+"-"+str(vencedor['id'])+"vs"+str(derrotado['id'])
    #En la base de datos se le asigna falso al estado de vivo del usuario derrotado

    db.reference("primerEvento/participantes/"+str(derrotado['id'])+"/vivo").set(False)
    (listaParticipantes[derrotado['id']])['vivo'] = False

    #Se aumenta el killcount del vencedor
    db.reference("primerEvento/participantes/"+str(vencedor['id'])+"/killcount").set(vencedor['killcount']+1)
    vencedor['killcount']+=1
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

    tamano_lista_vivos-=1

    #Se crean los mensajes para postear
    msg_batalla = vencedor['nombre']+" "+causa_muerte+" "+derrotado['nombre']+".\n"
    msg_killcount_vencedor = vencedor['nombre']+" lleva un killcount de: "+str(vencedor['killcount'])+".\n"
    msg_restantes = "Quedan "+str(tamano_lista_vivos)+" participantes vivos.\n"
    msg_top_killer = "Topkiller hasta el momento: "+topKiller['nombre']+" con un total de "+str(topKiller['killcount'])+" contrincantes vencidos.\n"
    
    #Se crea la imagen
    canvas = Image.new('RGB', (1410,760), 'black')
    img_draw = ImageDraw.Draw(canvas)

    #Tipos de Fuente
    fnt = ImageFont.truetype("BOOKOS.TTF", 20)
    fnt2 = ImageFont.truetype("BOOKOS.TTF", 15)

    #Variables auxiliares de iteración de pintado de la Imagen
    iterateParticipante = 0
    anchoAux=20
    listaParticipantesOrdenada =  sorted(listaParticipantes, key = lambda i: i['nombre'])
    for i  in range(0,4):
        largoauxiliar = 15
        for j in range(0,27):
            if(iterateParticipante < len(listaParticipantesOrdenada)):
                #Participante vivo blanco/ muerto rojo
                participante = listaParticipantesOrdenada[iterateParticipante]
                if(participante['vivo']):
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'],font=fnt, fill='white')
                else:
                    img_draw.text((anchoAux, largoauxiliar), participante['nombre'], font=fnt, fill='red')
                largoauxiliar+=25
                iterateParticipante+=1
            else:
                break
        anchoAux+=350

    #Lista ordenada por killcount de manera descendiente
    listaTopKillers = sorted(listaParticipantes, key = lambda i: i['killcount'],reverse=True)

    #Se pintan los primeros 3 topkillers
    largoauxiliar = 25+(25*25)
    largoauxiliarViejo = largoauxiliar
    img_draw.text((50,largoauxiliar),"TOP 3 Killers:",font=fnt2, fill='white')
    largoauxiliar+=20
    if listaTopKillers[0]!=None:
        img_draw.text((100,largoauxiliar),"1. "+(listaTopKillers[0])['nombre']+" : "+str((listaTopKillers[0])['killcount']),font=fnt2, fill='white')
        largoauxiliar+=20

    if listaTopKillers[1]!=None:
        img_draw.text((100,largoauxiliar),"2. "+(listaTopKillers[1])['nombre']+" : "+str((listaTopKillers[1])['killcount']),font=fnt2, fill='white')
        largoauxiliar+=20

    if listaTopKillers[2]!=None:
        img_draw.text((100,largoauxiliar),"3. "+(listaTopKillers[2])['nombre']+" : "+str((listaTopKillers[2])['killcount']),font=fnt2, fill='white')
        
    #Se pinta la fecha del evento y el acto o "accion" del evento

    img_draw.text((500,largoauxiliarViejo),"Fecha Evento: "+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),font=fnt2, fill='white')
    img_draw.text((500,largoauxiliarViejo+20),msg_batalla,font=fnt2, fill='white')
    img_draw.text((500,largoauxiliarViejo+40),msg_restantes,font=fnt2, fill='white')

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
        # posteo normal
        #fbpost(msg_post,rutaImagen)




def reiniciarEvento():
    filetexto =  open("./listas/Participantes.txt","r", encoding="utf-8")
    lineas = filetexto.read().splitlines()

    db.reference("primerEvento/estado").set(True)
    db.reference("primerEvento/lucha").delete()
    db.reference("primerEvento/resultados").delete()
    db.reference("primerEvento/participantes").delete()
    
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

#realizarLucha()
testGenerarImagen()
    
