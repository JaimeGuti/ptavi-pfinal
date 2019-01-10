#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler
import time
from uaclient import log_fich

try:
    CONFIG = sys.argv[1]
except:
    sys.exit("Usage: python uaserver.py config")


class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):

        line = self.rfile.read().decode('utf-8').split()[0]
        print("El cliente nos manda " + line)
        diferente = (line != "INVITE") or (line != "BYE") or (line != "ACK")

        if line == "INVITE":
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY+ ": "
            evento += line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            self.wfile.write(b"SIP/2.0 100 Trying\r\n")
            self.wfile.write(b" SIP/2.0 180 Ring\r\n")
            self.wfile.write(b" SIP/2.0 200 OK\r\n")

            session = "Content-Type: application/sdp\r\n\r\n" + "v=0\r\n"
            session += "o=" + USER + " " + IP_SERVER + "\r\n"
            session += "s=misesion\r\n" + "t=0\r\n" + "m=audio "
            session += PORT_RTPAUDIO + " RTP\r\n"
            self.wfile.write(bytes(session, 'utf-8'))

        elif line == "ACK":
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY+ ": "
            evento += line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = "./mp32rtp -i " + IP_REGPROXY + " -p "
            aEjecutar += PORT_RTPAUDIO + " < " + AUDIO
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)

        elif line == "BYE":
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY+ ": "
            evento += line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            self.wfile.write(b"SIP/2.0 200 OK")

        elif diferente:
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY+ ": "
            evento += line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            # Petición de otro método diferente a los descritos
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed")

        else:
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY+ ": "
            evento += line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            # Si la petición está mal formada
            self.wfile.write(b"SIP/2.0 400 Bad Request")

if __name__ == "__main__":

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

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', int(PORT_SERVER)), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Servidor apagado")
        evento = "Servidor apagado\r\n"
        fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        log_fich(LOGFICH, fecha, evento)
