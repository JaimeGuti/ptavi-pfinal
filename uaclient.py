#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import hashlib


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
    fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    evento = fecha + " " + evento
    fich.write(evento)
    fich.close()

if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2].upper()
        OPTION = sys.argv[3]
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

    USER = config_xml['account']['username']
    PASSWORD = config_xml['account']['passwd']
    IP_SERVER = config_xml['uaserver']['ip']
    PORT_SERVER = config_xml['uaserver']['puerto']
    PORT_RTPAUDIO = config_xml['rtpaudio']['puerto']
    IP_REGPROXY = config_xml['regproxy']['ip']
    PORT_REGPROXY = config_xml['regproxy']['puerto']
    LOGFICH = config_xml['log']['path']
    AUDIO = config_xml['audio']['path']

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_REGPROXY, int(PORT_REGPROXY)))

        try:
            if METHOD == "REGISTER":

                evento = "Starting..." + "\r\n\r\n"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                expire = "Expires: " + OPTION + "\r\n"
                LINE = METHOD + " sip:" + USER + ":" + PASSWORD
                LINE += " SIP/2.0\r\n"
                send_line = LINE + expire + "\r\n"
                my_socket.send(bytes(send_line, 'utf-8') + b'\r\n')
                data = my_socket.recv(1024)

                evento = "Sent to " + IP_REGPROXY + ":" + PORT_REGPROXY + ": "
                evento += send_line
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY
                evento += ": " + data.decode('utf-8') + "\r\n\r\n"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                if data.decode('utf-8').split()[1] == '401':
                    evento = "Received from " + IP_REGPROXY + ":"
                    evento += PORT_REGPROXY + data.decode('utf-8') + "\r\n"
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOGFICH, fecha, evento)
                    print(evento)

                    nonce_num = data.decode('utf-8').split('"')[1]

                    hash = hashlib.md5()
                    hash.update(bytes(PASSWORD, 'utf-8'))
                    hash.update(bytes(nonce_num, 'utf-8'))
                    hash = hash.hexdigest()
                    authorized = 'Authorization: Digest response="' + hash
                    authorized += '"'
                    send_line = LINE + expire + authorized + "\r\n"
                    my_socket.send(bytes(send_line, 'utf-8') + b'\r\n')
                    data = my_socket.recv(1024)

                    evento = "Sent to " + IP_REGPROXY + ":" + PORT_REGPROXY
                    evento += ": " + send_line
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOGFICH, fecha, evento)
                    print(evento)

            elif METHOD == "INVITE":

                LINE = METHOD + " " + USER + "\r\n\r\n"

                evento = "Sent to " + IP_REGPROXY + ":" + PORT_REGPROXY + ": "
                evento = LINE
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                session = METHOD + " sip:" + OPTION + " SIP/2.0\r\n"
                session += "Content-Type: application/sdp\r\n\r\n" + "v=0\r\n"
                session += "o=" + USER + " " + IP_SERVER + "\r\n"
                session += "s=misesion\r\n" + "t=0\r\n" + "m=audio "
                session += PORT_RTPAUDIO + " RTP\r\n"
                print(session)

                send_line = session + "\r\n"
                my_socket.send(bytes(session, 'utf-8') + b'\r\n')
                data = my_socket.recv(1024)
                my_socket.connect((IP_SERVER, int(PORT_SERVER)))

                resp = "SIP/2.0 100 Trying\r\n SIP/2.0 180 Ringing\r\n"
                resp += "SIP/2.0 200 OK\r\n"
                if data != resp:
                    LINE = "ACK sip:" + OPTION + " SIP/2.0\r\n"
                    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                    aEjecutar = "./mp32rtp -i " + IP_REGPROXY + " -p "
                    aEjecutar += PORT_RTPAUDIO + " < " + AUDIO
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)

            elif METHOD == "BYE":
                LINE = METHOD + "\r\n\r\n"
                send_line = METHOD + " sip:" + OPTION + " SIP/2.0\r\n"
                my_socket.send(bytes(send_line, 'utf-8') + b'\r\n')
                data = my_socket.recv(1024)

                evento = "Sent to " + IP_REGPROXY + ":" + PORT_REGPROXY + ": "
                evento += LINE
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY
                evento += ": " + data.decode('utf-8') + "\r\n\r\n"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)

                evento = "Finishing." + "\r\n\r\n"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOGFICH, fecha, evento)
        except:
            wrong_connection = IP_REGPROXY + " port " + PORT_REGPROXY
            sys.exit("Error: No server listening at " + wrong_connection)
            evento = "Error: No server listening at " + wrong_connection
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

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
