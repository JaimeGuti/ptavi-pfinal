#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    AUDIO = sys.argv[3]
except:
    sys.exit("Usage: python uaserver.py config")


class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):

        line = self.rfile.read().decode('utf-8').split()[0]
        print("El cliente nos manda " + line)
        diferente = (line != "INVITE") or (line != "BYE") or (line != "ACK")

        if line == "INVITE":
            self.wfile.write(b"SIP/2.0 100 Trying")
            self.wfile.write(b" SIP/2.0 180 Ring")
            self.wfile.write(b" SIP/2.0 200 OK")

        elif line == "ACK":
            aEjecutar = "./mp32rtp -i " + receptor_IP + " -p "
            aEjecutar += receptor_Puerto + " < " + AUDIO
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)

        elif line == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK")

#        elif line == ""
            #Usuario se intenta registrar sin autenticarse
#            self.wfile.write(b"SIP/2.0 401 Unauthorized")

#        elif line == ""
            #Usuario no encontrado en el servidor de registro
#            self.wfile.write(b"SIP/2.0 404 User Not Found")

        elif diferente:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed")

        else:
            self.wfile.write(b"SIP/2.0 400 Bad Request")

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Servidor apagado")
