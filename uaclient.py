#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time

class XMLHandler(ContentHandler):

    def __init__(self):

        self.attrs = []
        self.tags = []

    def startElement(self, name, attrs):

        if name == 'account':

            acc = {}
            acc['username'] = attrs.get('username', "")
            acc['passwd'] = attrs.get('passwd', "")

            self.tags.append(['account', acc])

        elif name == 'uaserver':

            uas = {}
            uas['ip'] = attrs.get('ip', "")
            uas['puerto'] = attrs.get('puerto', "")

            self.tags.append(['uaserver', uas])

        elif name == 'rtpaudio':

            rtp = {}
            rtp['puerto'] = attrs.get('puerto', "")

            self.tags.append(['rtpaudio', rtp])

        elif name == 'regproxy':

            regp = {}
            regp['ip'] = attrs.get('ip', "")
            regp['puerto'] = attrs.get('puerto', "")

            self.tags.append(['regproxy', regp])

        elif name == 'log':

            lg = {}
            lg['path'] = attrs.get('path', "")

            self.tags.append(['log', lg])

        elif name == 'audio':

            aud = {}
            aud['path'] = attrs.get('path', "")

            self.tags.append(['audio', aud])

    def get_tags(self):

        return self.tags

def log_fich(lfich, fecha, evento):
    fich = open(lfich, 'a')
    fecha = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    evento = fecha + " " + evento
    fich.write(evento)
    fich.close()

try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2].upper()
    OPTION = int(sys.argv[3])
except:
    sys.exit("Usage: python uaclient.py config method option")

config_fich = open(CONFIG, 'r')
line = config_fich.readlines()
config_fich.close()

lfich = "ua1log.txt"

# Contenido que vamos a enviar
# LINE = METODO + " sip:" + RECEPTOR + "@" + IP + " SIP/2.0\r\n\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect(('localhost', 5555))

    evento = "Starting"
    fecha = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    log_fich(lfich,fecha,evento)
"""
    if METODO == "INVITE":
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)

    elif METODO == "BYE":
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)

    mens_ack = data.decode('utf-8')
    if mens_ack == "SIP/2.0 100 Trying SIP/2.0 180 Ringing SIP/2.0 200 OK":
        ack_line = 'ACK' + " sip:" + RECEPTOR + "@"
        ack_line += IP + " SIP/2.0\r\n\r\n"
        print(ack_line)
        my_socket.send(bytes(ack_line, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)

    print('Recibido -- ', data.decode('utf-8'))
    print("Terminando socket...")

print("Fin.")
"""
