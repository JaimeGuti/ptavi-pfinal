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
        self.tags = {}

    def startElement(self, name, attrs):

        if name == 'account':

            acc = {}
            acc['username'] = attrs.get('username', "")
            acc['passwd'] = attrs.get('passwd', "")

            self.tags['account'] = acc

        elif name == 'uaserver':

            uas = {}
            uas['ip'] = attrs.get('ip', "")
            uas['puerto'] = attrs.get('puerto', "")

            self.tags['uaserver'] = uas

        elif name == 'rtpaudio':

            rtp = {}
            rtp['puerto'] = attrs.get('puerto', "")

            self.tags['rtpaudio'] = rtp

        elif name == 'regproxy':

            regp = {}
            regp['ip'] = attrs.get('ip', "")
            regp['puerto'] = attrs.get('puerto', "")

            self.tags['regproxy'] = regp

        elif name == 'log':

            lg = {}
            lg['path'] = attrs.get('path', "")

            self.tags['log'] = lg

        elif name == 'audio':

            aud = {}
            aud['path'] = attrs.get('path', "")

            self.tags['audio'] = aud

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

parser = make_parser()
cHandler = XMLHandler()
parser.setContentHandler(cHandler)
parser.parse(open(CONFIG))
config_xml = cHandler.get_tags()

IP_REGPROXY = config_xml['regproxy']['ip']
PORT_REGPROXY = config_xml['regproxy']['puerto']

lfich = config_xml['log']['path']

print(IP_REGPROXY)
print(PORT_REGPROXY)
print(lfich)

# Contenido que vamos a enviar
# LINE = METODO + " sip:" + RECEPTOR + "@" + IP + " SIP/2.0\r\n\r\n"

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_REGPROXY, int(PORT_REGPROXY)))

    evento = "Starting..."
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
