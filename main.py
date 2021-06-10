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
    post_id = graph.put_photo(image=open("./assets/we are back.png"),message = msg)['post_id']
    print(f"Mensaje \"{msg}\" y publicación subida correctamente!")

if __name__ == '__main__':
    token = open('./assets/token.txt', 'r')
    if token.readline() == "putyourtokenherexdd":
        print("put your access token in assets/token.txt. you can obtain the access token from http://maxbots.ddns.net/token/")
        sys.exit("error no token")
    ans = input("INTENTAR POSTEAR IMAGEN DE PRUEBA? \n>")
    if 'y' in ans.lower():
        testingPost()
    else:
        pass
    #schedule.every().hour.do(post).run()
#   Uncomment line 99 and comment line 97 in order to enable burst mode    
#   schedule.every().hour.do(burst).run()
    #while 1:
       # schedule.run_pending()
       # time.sleep(1)
