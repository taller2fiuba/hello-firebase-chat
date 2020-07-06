# Mini cliente-servidor de chat utilizando Firebase RTDB y REST.

Código de ejemplo sobre cómo utilizar la Realtime DB de Firebase para implementar un pequeño chat.

## Configuración

Se debe crear un archivo `config.py` copiando `config-ejemplo.py` y editando los valores que 
correspondan. Particularmente es necesario editar `ARCHIVO_CREDENTIALS` con la ruta al archivo
JSON de credenciales de Firebase (que puede obtenerse desde la consola de Firebase).

## Funcionamiento

Cada persona que quiere utilizar el chat tiene asignado un ID numérico. Cada chat se realiza únicamente entre dos personas. Cuando la persona con ID 1 quiere enviar un mensaje a la persona con ID 2, debe realizar una solicitud POST al servidor de chat.

El servidor de chat recibirá la solicitud que tiene el siguiente formato:

```
POST /

body: {
    "mensaje": texto del mensaje,
    "remitente": quien envio el mensaje,
    "destinatario": quien recibira el mensaje
}
```

Recibida la solicitud, el servidor de chat almacenará el mensaje recibido en la base de datos de tiempo real de Firebase (función `enviar_mensaje`). Ver definición de la estructura en `servidor.py`.

