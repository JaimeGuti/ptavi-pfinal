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
import json
from random import randint


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
        self.expired()

        line = self.rfile.read()
        method = line.decode('utf-8').split(' ')[0]
        OPTION = line.decode('utf-8').split(' ')[-1]
        reg_client = line.decode('utf-8').split(':')[1]
        print(reg_client)

        if method == "REGISTER":
            exptm = time.localtime(time.time() + int(OPTION))
            total_exptm = time.strftime('%Y%m%d%H%M%S', exptm)
            if len(self.clients) == 0 and total_exptm != 0:
                rand_num = str(randint(1, 999999999999999999999))
                auth = 'WWW Authenticate: '
                auth += 'Digest nonce="' + rand_num + '"'
                self.wfile.write(b"SIP/2.1 401 Unauthorized\r\n")
                evento = "SIP/2.1 401 Unauthorized" + auth
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)
                print("OK 1") # Esto hay que quitarlo, es solo de comprobación

            elif len(self.clients) != 0 and total_exptm != 0:
                reg_client = line.decode('utf-8').split(':')[1]
                for username in self.clients:
                    if username[0] != reg_client:
                        rand_num = str(randint(1, 999999999999999999999))
                        auth = 'WWW Authenticate: '
                        auth += 'Digest nonce="' + rand_num + '"'
                        self.wfile.write(b"SIP/2.1 401 Unauthorized\r\n")
                        evento = "SIP/2.1 401 Unauthorized" + auth
                        t = time.localtime(time.time())
                        fecha = time.strftime('%Y%m%d%H%M%S', t)
                        log_fich(LOG_PATH, fecha, evento)
                    elif username[0] != reg_client:
                        print("Ya está registrado") # COMPLETAR

                print("OK 2") # Esto hay que quitarlo, es solo de comprobación

            elif len(self.clients) != 0 and total_exptm == 0:
                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                self.clients.remove(reg_client)
                evento = reg_client + " eliminated"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)
                print("OK 3") # Esto hay que quitarlo, es solo de comprobación

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

    def expired(self):
        #line = self.rfile.read()
        #OPTION = line.decode('utf-8').split(' ')[-1]
        exp = time.localtime(time.time())
        exp_tm = time.strftime('%Y-%m-%d%H%M%S', exp)
        for clt in self.clients:
            if sel.clients[clt][1] <= tm:
                self.clients.remove(clt)


if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]
    except:
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
