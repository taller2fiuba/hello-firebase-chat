#!/usr/bin/env python3

'''
Servidor de chat usando Firebase Realtime DB

Este servidor recibe los mensajes que envía cada uno de los usuarios
conectados y los almacena la base de datos de tiempo real de Firebase.

Cada usuario recibe los mensajes de chat directamente desde Firebase.

La base de datos se estructurará de la siguiente manera:
 - chats/
   - <uid_a>
     - <uid_b>
       - timestamp: <segundos enteros desde la época Unix con signo negativo>
       - ultimoMensaje: <str>
   - <uid_b>
     - <uid_a>
       - timestamp: <segundos enteros desde la época Unix con signo negativo>
       - ultimoMensaje: <str>

 - mensajes/
   - <uid_a>-<uid_b>/
      - <mensaje>
        - enviadoPor: <uid_a>|<uid_b>
        - mensaje: <str>
        - timestamp: <segundos enteros desde la época Unix>
      - <mensaje>
      - <mensaje>

Donde <uid_a> y <uid_b> representan los identificadores de usuario de dos
usuarios con uid_a < uid_b y uid_a != uid_b.

Al iniciar el servidor se abrirá un puerto donde se esperarán solicitudes 
HTTP de tipo POST a /. Cada solicitud tendrá un cuerpo en formato JSON con
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

from config import *

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
db_chats_ref = db.reference(f'/hello-firebase/{RECURSO_DB_CHATS}')
db_mensajes_ref = db.reference(f'/hello-firebase/{RECURSO_DB_MENSAJES}')

def enviar_mensaje(mensaje, remitente: int, destinatario: int):
    print(f'{remitente} > {destinatario}: {mensaje}')

    nombre_chat = f'{remitente}-{destinatario}'
    if remitente > destinatario:
        nombre_chat = f'{destinatario}-{remitente}'
    
    # Construir el mensaje
    mensaje_db_data = {
        'enviadoPor': remitente,
        'mensaje': mensaje,
        'timestamp': int(datetime.datetime.now().timestamp())
    }

    # Y su metainformación
    chat_db_data = {
        'timestamp': -mensaje_db_data['timestamp'],
        'ultimoMensaje': mensaje_db_data['mensaje']
    }

    # Agregar el mensaje al chat
    db_mensajes_ref.child(nombre_chat).push(mensaje_db_data)

    # Actualizar metainformación d -> r; y r -> d.
    db_chats_ref.child(str(remitente)).child(str(destinatario)).set(chat_db_data)
    db_chats_ref.child(str(destinatario)).child(str(remitente)).set(chat_db_data)

try:
    with HTTPServer(('localhost', PUERTO_HTTP), ChatServer) as httpd:
        print(f'Escuchando en localhost:{PUERTO_HTTP}', file=sys.stderr)
        httpd.serve_forever()
except KeyboardInterrupt:
    pass

