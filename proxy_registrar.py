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
import hashlib


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
    nonce_num = []

    def handle(self):
        self.json2registered()

        line = self.rfile.read()
        method = line.decode('utf-8').split(' ')[0]
        OPTION = line.decode('utf-8').split(' ')[3].split('\r')[0]
        exptm = time.localtime(time.time() + int(OPTION))
        total_exptm = time.strftime('%Y%m%d%H%M%S', exptm)
        #print(line.decode('utf-8').split()) # Esto hay que quitarlo, es solo de comprobación
        rand_num = str(randint(1, 999999999999999999999))

        if method == "REGISTER" and len(line.decode('utf-8').split()) < 6:
            auth = 'WWW Authenticate: '
            auth += 'Digest nonce="' + rand_num + '"'
            evento = " SIP/2.1 401 Unauthorized " + auth
            self.wfile.write(bytes((evento), 'utf-8'))
            t = time.localtime(time.time())
            fecha = time.strftime('%Y%m%d%H%M%S', t)
            log_fich(LOG_PATH, fecha, evento)

        elif method == "REGISTER" and len(line.decode('utf-8').split()) >= 6:
            # Hay que comprobar la contraseña
            fich_passw = open(DATABASE_PASSWD, 'r')
            for line_pass in fich_passw.readlines():
                reg_client = line.decode('utf-8').split(':')[1]
                if len(reg_client) == len(line.split()[1][4:-6]):
                    passwd = line.decode('utf-8').split(' ')[1][-5:]
                    nonce_num = rand_num

                    correct_pass = hashlib.md5()
                    correct_pass.update(bytes(passwd, 'utf-8'))
                    correct_pass.update(bytes(nonce_num, 'utf-8'))
                    correct_pass = correct_pass.hexdigest()

                    #Registrar usuario si la contraseña es correcta
                    if correct_pass != line.decode('utf-8').split('=')[-1]:
                        self.clients = []
                        a = []
                        self.a = line.decode('utf-8').split()
                        self.clients.append(str(a))
                        self.clients.append(total_exptm)
                        #self.register2json()
                        evento = reg_client + "is registered"
                        self.wfile.write(bytes((evento), 'utf-8'))
                        t = time.localtime(time.time())
                        fecha = time.strftime('%Y%m%d%H%M%S', t)
                        log_fich(LOG_PATH, fecha, evento)
            self.register2json()
            # Borra el usuario si expires es igual a 0
            if int(line.decode('utf-8').split(' ')[3][:1]) == 0:
                self.wfile.write(b"SIP/2.0 200 OK\r\n")
                evento = "SIP/2.0 200 OK\r\n"
                evento += "User " + reg_client
                evento += " is removed"
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)
                print("User " + reg_client + " is removed")
                for username in self.clients:
                    self.clients.remove(username)
            self.register2json()

        elif method == "INVITE":
            print(method)

        elif method == "BYE":
            print(method)

        elif method == "ACK":
            print(method)

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
        line = self.rfile.read()
        OPTION = line.decode('utf-8').split(' ')[3].split('\r')[0]
        exp = time.localtime(time.time() + int(OPTION))
        exp_tm = time.strftime('%Y-%m-%d%H%M%S', exp)
        for user in self.clients:
            if self.clients[user] <= exp_tm:
               self.clients.remove(user)


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
