#!/usr/bin/env python3

'''
Servidor de chat usando Firebase Realtime DB

Este servidor recibe los mensajes que envía cada uno de los usuarios
conectados y los almacena la base de datos de tiempo real de Firebase.

Cada usuario recibe los mensajes de chat directamente desde Firebase.

La base de datos se estructurará de la siguiente manera:
 - chats/
   - <uid_a>-<uid_b>/
      - <mensaje>
      - <mensaje>
      - <mensaje>
Donde <uid_a> y <uid_b> representan los identificadores de usuario de dos
usuarios con uid_a < uid_b y uid_a != uid_b.

Al iniciar el servidor se abrirá un puerto donde se esperarán solicitudes 
HTTP de tipo POST a /chat. Cada solicitud tendrá un cuerpo en formato JSON con
el siguiente contenido:
{
    "remitente": <uid>
    "destinatario": <uid>
    "mensaje": <mensaje>
}

No hay controles de autenticación en este ejemplo.
'''

import sys
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

import firebase_admin
from firebase_admin import credentials, db

# Credenciales del SDK de Firebase
ARCHIVO_CREDENTIALS = 'obtener-desde-consola-de-firebase.json'

# Identificador de la base de datos a utilizar
URL_DB = 'https://chotuve-a8587.firebaseio.com/'

# Recurso dentro de la base de datos donde se almacenaran los chats
RECURSO_DB = 'chats'

# Puerto a utilizar para recibir requests HTTP
PUERTO_HTTP = 8080

class ChatServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        data = json.loads(str(self.rfile.read(content_len), 'utf-8'))
        mensaje = data.get('mensaje')
        remitente = data.get('remitente', 0)
        destinatario = data.get('destinatario', 0)
        if not mensaje or not remitente or not destinatario:
            self.send_error(400)
            return
        
        enviar_mensaje(mensaje, remitente, destinatario)
        self.send_response(200)
        self.end_headers()

cred = credentials.Certificate(ARCHIVO_CREDENTIALS)
firebase_admin.initialize_app(cred, {'databaseURL': URL_DB})
db_ref = db.reference(f'/hello-firebase/{RECURSO_DB}')

def enviar_mensaje(mensaje, remitente: int, destinatario: int):
    print(f'{remitente} > {destinatario}: {mensaje}')
    nombre_chat = f'{remitente}-{destinatario}'
    if remitente > destinatario:
        nombre_chat = f'{destinatario}-{remitente}'
    
    child = db_ref.child(nombre_chat)
    child.push({
        'enviado_por': remitente, 
        'hora': datetime.datetime.now().isoformat(), 
        'mensaje': mensaje
    })

with HTTPServer(('localhost', PUERTO_HTTP), ChatServer) as httpd:
    print(f'Escuchando en localhost:{PUERTO_HTTP}', file=sys.stderr)
    httpd.serve_forever()

