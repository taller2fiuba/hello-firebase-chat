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

# Credenciales del SDK de Firebase
ARCHIVO_CREDENTIALS = 'obtener-desde-consola-de-firebase.json'

# Identificador de la base de datos a utilizar
URL_DB = 'https://chotuve-a8587.firebaseio.com/'

# Recurso dentro de la base de datos donde se almacenaran los chats
RECURSO_DB = 'chats'

# URL del servidor de chat
URL_SERVIDOR = 'http://localhost:8080'

def enviar_mensaje(mensaje, remitente, destinatario):
    response = requests.post(URL_SERVIDOR, json={
        'mensaje': mensaje,
        'remitente': int(remitente),
        'destinatario': int(destinatario)
    })

    return 200 <= response.status_code < 300

def configurar_chat(mi_uid, otro_uid):
    cred = credentials.Certificate(ARCHIVO_CREDENTIALS)
    firebase_admin.initialize_app(cred, {'databaseURL': URL_DB})
    db_ref = db.reference(f'/hello-firebase/{RECURSO_DB}')

    nombre = f'{mi_uid}-{otro_uid}'
    if mi_uid > otro_uid:
        nombre = f'{otro_uid}-{mi_uid}'
    
    chat_ref = db_ref.child(nombre)
    return chat_ref.listen(chat_listener)

def chat_listener(event: db.Event):
    '''
    Listener de la RTDB. Esta función es llamada automáticamente por Firebase
    cuando se detectan cambios en la RTDB o al conectarse por primera vez.

    En la primer conexión se recibe un evento con path "/" que trae todo el
    contenido de la RTDB.
    Los siguientes cambios a la RTDB (tanto los realizados desde este cliente
    como los realizados por otros clientes) produciran un evento con path igual
    a /<id de mensaje> y el mensaje en los datos.
    '''
    if event.path == '/':
        return # Ignorar los mensajes viejos de la conv.
    
    print('>>', event.data['mensaje'])

def main():
    if len(sys.argv) != 3:
        print('Uso: cliente <mi_uid> <otro_uid>', file=sys.stderr)
        return
    
    remitente, destinatario = int(sys.argv[1]), int(sys.argv[2])
    listener = configurar_chat(remitente, destinatario)

    print('Ingrese un mensaje y pulse enter para enviar')
    while True:
        mensaje = input()
        if not mensaje:
            break
        enviar_mensaje(mensaje, remitente, destinatario)
    
    print('Por favor espere, cerrando conexiones')
    listener.close()

main()
