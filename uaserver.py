#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler

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
            self.wfile.write(b"SIP/2.0 100 Trying\r\n")
            self.wfile.write(b" SIP/2.0 180 Ring\r\n")
            self.wfile.write(b" SIP/2.0 200 OK\r\n")

        elif line == "ACK":
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            aEjecutar = "./mp32rtp -i " + IP_REGPROXY + " -p "
            aEjecutar += PORT_RTPAUDIO + " < " + AUDIO
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)

        elif line == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK\r\n")

#        elif line == ""
            # Usuario se intenta registrar sin autenticarse
#            self.wfile.write(b"SIP/2.0 401 Unauthorized")

#        elif line == ""
            # Usuario no encontrado en el servidor de registro
#            self.wfile.write(b"SIP/2.0 404 User Not Found")

        elif diferente:
            # Petición de otro método diferente a los descritos
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n")

        else:
            # Si la petición está mal formada
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n")

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Servidor apagado")
