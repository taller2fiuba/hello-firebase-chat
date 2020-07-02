# Mini cliente-servidor de chat utilizando Firebase RTDB y REST.

Código de ejemplo sobre cómo utilizar la Realtime DB de Firebase para implementar un pequeño chat.

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

Recibida la solicitud, el servidor de chat almacenará el mensaje recibido en la base de datos de tiempo real de Firebase (función `enviar_mensaje`). Para esto deberá ubicar el nodo que representa el chat de la persona 1 con la persona 2 y agregarle un nuevo hijo con el mensaje recibido.

En la estructura planteada en este ejemplo, se le asigna un identificador a cada chat de la forma "ID1-ID2", donde siempre ID1 es menor que ID2; de modo que si la persona 1 quiere hablar con la 2, su identificador de chat es "1-2"; y si la persona 43 quiere hablar con la persona 37 su identificador de chat es "37-43". Que el ID1 sea menor que el ID2 sólamente elimina la ambigüedad de tener chats con identificador "37-43" y "43-37" según quién inició el chat.

Dentro de cada nodo de chat, los mensajes se almacenarán como un conjunto de tres valores: ID de quién lo envió, fecha y hora del mensaje en formato ISO, y texto del mensaje.

