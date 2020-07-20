#!/usr/bin/env python3

import sys
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

import firebase_admin
from firebase_admin import credentials, db, messaging

from config import *

RECURSO_DB_NOTIFICACIONES='notificaciones'

cred = credentials.Certificate(ARCHIVO_CREDENTIALS)
fb = firebase_admin.initialize_app(cred, {'databaseURL': URL_DB}, name='chotuve-notificaciones')
db_notificaciones = db.reference(f'/app-server-dev/{RECURSO_DB_NOTIFICACIONES}', app=fb)

if not len(sys.argv) == 2:
    print('Uso: notificador <id de usuario>', file=sys.stderr)
    exit()

uid = int(sys.argv[1])
token = db_notificaciones.child(str(uid)).get()
print('Token: ', token)

if not token:
    print('No token :(')
    exit()

message = messaging.Message(
    notification=messaging.Notification(
        title='$GOOG up 1.43% on the day',
        body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
    ),
    token=token
)

# Send a message to devices subscribed to the combination of topics
# specified by the provided condition.
response = messaging.send(message, app=fb)

print(response)
print(repr(response))
