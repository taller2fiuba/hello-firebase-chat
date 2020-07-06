#!/usr/bin/env python3

'''
Cliente de prueba para el Chat via Firebase Realtime DB.

Este cliente es una prueba conceptual del uso de Firebase RTDB y sólo permite
tener una única conversación entre dos UID pasados por línea de comandos.

Uso: cliente <mi_uid> <otro_uid>
'''

import sys
import requests

import firebase_admin
from firebase_admin import credentials, db

from config import *

def enviar_mensaje(mensaje, remitente, destinatario):
    response = requests.post(URL_SERVIDOR, json={
        'mensaje': mensaje,
        'remitente': int(remitente),
        'destinatario': int(destinatario)
    })

    return 200 <= response.status_code < 300

def configurar_chat(mi_uid, otro_uid, cola_mensajes):
    cred = credentials.Certificate(ARCHIVO_CREDENTIALS)
    firebase_admin.initialize_app(cred, {'databaseURL': URL_DB})
    db_ref = db.reference(f'/hello-firebase/{RECURSO_DB_MENSAJES}')

    nombre = f'{mi_uid}-{otro_uid}'
    if mi_uid > otro_uid:
        nombre = f'{otro_uid}-{mi_uid}'
    
    chat_ref = db_ref.child(nombre)
    return chat_ref.listen(lambda e: chat_listener(mi_uid, cola_mensajes, e))

def chat_listener(mi_uid, cola_mensajes, event: db.Event):
    '''
    Listener de la RTDB. Esta función es llamada automáticamente por Firebase
    cuando se detectan cambios en la RTDB o al conectarse por primera vez.

    En la primer conexión se recibe un evento con path "/" que trae todo el
    contenido de la RTDB.
    Los siguientes cambios a la RTDB (tanto los realizados desde este cliente
    como los realizados por otros clientes) produciran un evento con path igual
    a /<id de mensaje> y el mensaje en los datos.
    '''
    if not event.data:
        return
    
    if event.path == '/':
        mensajes = event.data.values()
    else:
        mensajes = [ event.data ]
    
    for mensaje in mensajes:
        if mensaje['enviadoPor'] != mi_uid:
            cola_mensajes.append(mensaje['mensaje'])

def main():
    if len(sys.argv) != 3:
        print('Uso: cliente <mi_uid> <otro_uid>', file=sys.stderr)
        return
    
    remitente, destinatario = int(sys.argv[1]), int(sys.argv[2])
    cola_mensajes = []
    listener = configurar_chat(remitente, destinatario, cola_mensajes)

    print('Ingrese un mensaje y pulse enter para enviarlo.')
    print('Si pulsa enter sin ingresar ningún mensaje se revisará si hay ')
    print('mensajes nuevos pendientes de ser recibidos.')
    while True:
        mensaje = input('<< [* para salir]: ')
        while cola_mensajes:
            print('>>', cola_mensajes.pop(0))

        if not mensaje:
            continue
    
        if mensaje == '*':
            break
        
        enviar_mensaje(mensaje, remitente, destinatario)
        print('<<', mensaje)
    
    print('Por favor espere, cerrando conexiones')
    listener.close()

main()
