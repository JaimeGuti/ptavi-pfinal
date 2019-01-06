#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler
import time
from uaclient import log_fich


class PxReg_XMLHandler(ContentHandler):

    def __init__(self):

        self.attrs = []
        self.tags = {}

    def startElement(self, name, attrs):

        if name == 'server':

            srv = {}
            srv['name'] = attrs.get('name', "")
            srv['ip'] = attrs.get('ip', "")
            srv['puerto'] = attrs.get('puerto', "")

            self.tags['server'] = srv

        elif name == 'database':

            dtbs = {}
            dtbs['path'] = attrs.get('path', "")
            dtbs['passwdpath'] = attrs.get('passwdpath', "")

            self.tags['database'] = dtbs

        elif name == 'log':

            lg = {}
            lg['path'] = attrs.get('path', "")

            self.tags['log'] = lg

    def get_tags(self):

        return self.tags


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class, extraído de la práctica 4
    """
    clients = {}

    def handle(self):

        self.json2registered()
        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        line = self.rfile.read()
        time_exp = float(line.decode('utf-8').split()[-1])
        total_time = time.localtime(time.time() + time_exp)
        tm = time.strftime('%Y-%m-%d %H:%M:%S', total_time)
        info = {"address": self.client_address[0], "expires": tm}
        if line.decode('utf-8').split(' ')[0] == 'REGISTER':
            name_client = line.decode('utf-8').split(' ')[1][4:]
            self.clients[name_client] = info
            self.register2json()
            if line.decode('utf-8').split(' ')[3][-1] == 'Expires':
                expires = int(line.decode('utf-8').split(' ')[-1])
                if str(expires) == '0':
                    del self.clients[name_client]
                    print(b"SIP/2.0 200 OK\r\n\r\n")
        print(line.decode('utf-8'))
        print(self.clients)

    def register2json(self):
        # Creación del fichero .json
        json_file = open('registered.json', 'w')
        json.dump(self.clients, json_file)

    def json2registered(self):
        # Comprobación del fichero .json
        try:
            json_file = open('registered.json')
            self.clients = json.load(json_file)
        except:
            self.register2json()


if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]
    except(IndexError, ValueError):
        sys.exit("Usage: python proxy_registrar.py config")

    parser = make_parser()
    cHandler = PxReg_XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG))
    config_xml_proxy = cHandler.get_tags()

    SERVER_NAME = config_xml_proxy['server']['name']
    SERVER_IP = config_xml_proxy['server']['ip']
    SERVER_PORT = config_xml_proxy['server']['puerto']
    DATABASE_PATH = config_xml_proxy['database']['path']
    DATABASE_PASSWD = config_xml_proxy['database']['passwdpath']
    LOG_PATH = config_xml_proxy['log']['path']

    serv = socketserver.UDPServer(('', int(SERVER_PORT)), SIPRegisterHandler)
    print("Server MiServidorBigBang listening at port 5555...")

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Servidor Proxy/Registrar apagado")
        evento = "Servidor Proxy/Registrar apagado\r\n"
        fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        log_fich(LOG_PATH, fecha, evento)
