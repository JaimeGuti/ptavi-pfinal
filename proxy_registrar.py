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
    clients = []
    nonce_num = []

    def handle(self):
        self.json2registered()

        line = self.rfile.read()
        method = line.decode('utf-8').split(' ')[0]
        rand_num = str(randint(1, 999999999999999999999))
        diferente = (line != "REGISTER") or (line != "INVITE")
        diferente += (line != "BYE") or (line != "ACK")

        if method == "REGISTER":

            if len(line.decode('utf-8').split()) < 6:
                OPTION = line.decode('utf-8').split(' ')[3].split('\r')[0]
                exptm = time.localtime(time.time() + int(OPTION))
                total_exptm = time.strftime('%Y%m%d%H%M%S', exptm)
                auth = 'WWW Authenticate: '
                auth += 'Digest nonce="' + rand_num + '"'
                evento = " SIP/2.1 401 Unauthorized\r\n " + auth
                self.wfile.write(bytes((evento), 'utf-8'))
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)

            elif len(line.decode('utf-8').split()) >= 6:
                OPTION = line.decode('utf-8').split(' ')[3].split('\r')[0]
                exptm = time.localtime(time.time() + int(OPTION))
                total_exptm = time.strftime('%Y%m%d%H%M%S', exptm)
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
                            evento = reg_client + " is registered\r\n"
                            self.wfile.write(bytes((evento), 'utf-8'))
                            t = time.localtime(time.time())
                            fecha = time.strftime('%Y%m%d%H%M%S', t)
                            log_fich(LOG_PATH, fecha, evento)
                            exp = time.localtime(time.time() + int(OPTION))
                            exp_tm = time.strftime('%Y-%m-%d%H%M%S', exp)
                            ld = line.decode('utf-8')
                            client_name = ld.split(' ')[1][4:-6]
                            self.clients = [client_name,
                                            {"ip": self.client_address[0],
                                             "port": self.client_address[1],
                                             "expires": exp_tm,
                                             "register_time": fecha}]
                            self.register2json()
                # Borra el usuario si expires es igual a 0
                if int(line.decode('utf-8').split(' ')[3][:1]) == 0:
                    evento = "SIP/2.0 200 OK\r\n"
                    evento += "User " + reg_client
                    evento += " is removed"
                    self.wfile.write(bytes((evento), 'utf-8'))
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOG_PATH, fecha, evento)
                    print("User " + reg_client + " is removed")
                    for username in self.clients:
                        self.clients.remove(username)
                        self.clients = []
                        self.register2json()
                # Comprobar si el usuario está ya registrado
                if self.clients == []:
                    reg_client = line.decode('utf-8').split(':')[1]
                    for username in self.clients:
                        if username == reg_client:
                            self.wfile.write(b"SIP/2.0 200 OK\r\n")
                            evento = "SIP/2.0 200 OK\r\n"
                            evento += "User " + reg_client
                            evento += " is already registered"
                            t = time.localtime(time.time())
                            fecha = time.strftime('%Y%m%d%H%M%S', t)
                            log_fich(LOG_PATH, fecha, evento)
                            print("User " + reg_client + " already registered")

        elif method == "INVITE":
            self.json2registered()
            reg_client = line.decode('utf-8').split(':')[1].split(' ')[0]
            ip_client = self.clients[1]["ip"]
            port_client = self.clients[1]["port"]
            try:
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_DGRAM) as my_socket:
                    mess = line.decode('utf-8')
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip_client, int(port_client)))
                    my_socket.send(bytes(line.decode('utf-8'),
                                         'utf-8') + b'\r\n')
                    data = "SIP/2.0 100 Trying\r\n SIP/2.0 180 Ringing\r\n"
                    data = "SIP/2.0 200 OK\r\n"
                    evento = " Received from " + ip_client + ":"
                    evento = str(port_client) + ": " + mess
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOG_PATH, fecha, evento)
                    evento = " Sent to " + ip_client + ":"
                    evento = str(port_client) + ": " + data
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOG_PATH, fecha, evento)
                    self.wfile.write(bytes(data, 'utf-8'))
            except:
                evento = "SIP/2.0 404 User Not Found\r\n"
                self.wfile.write(bytes(evento, 'utf-8'))
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)

        elif method == "BYE":
            self.json2registered()
            ip_client = self.clients[1]["ip"]
            port_client = self.clients[1]["port"]
            try:
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_DGRAM) as my_socket:
                    mess = line.decode('utf-8')
                    evento = " Received from " + ip_client + ":"
                    evento = str(port_client) + ": " + mess
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOG_PATH, fecha, evento)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip_client, int(port_client)))
                    my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                    data = " SIP/2.0 200 OK"
                    self.wfile.write(bytes(data, 'utf-8'))
                    evento = "Sent to " + ip_client + ":" + str(port_client)
                    evento = ": " + data
                    t = time.localtime(time.time())
                    fecha = time.strftime('%Y%m%d%H%M%S', t)
                    log_fich(LOG_PATH, fecha, evento)
            except:
                evento = "SIP/2.0 404 User Not Found\r\n"
                self.wfile.write(bytes(data, 'utf-8'))
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)

        elif method == "ACK":
            self.json2registered()
            reg_client = line.decode('utf-8').split(':')[1].split(' ')[0]
            ip_client = self.clients[1]["ip"]
            port_client = self.clients[1]["port"]
            mess = line.decode('utf-8')
            evento = " Received from " + ip_client + ":"
            evento = str(port_client) + ": " + mess
            t = time.localtime(time.time())
            fecha = time.strftime('%Y%m%d%H%M%S', t)
            log_fich(LOG_PATH, fecha, evento)
            try:
                my_socket.setsockopt(socket.SOL_SOCKET,
                                     socket.SO_REUSEADDR, 1)
                my_socket.connect((ip_client, int(port_client)))
                my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                evento = "Sent to " + ip_client + ":" + str(port_client)
                evento = ": " + mess
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)
            except:
                evento = "SIP/2.0 404 User Not Found"
                self.wfile.write(bytes(data, 'utf-8'))
                t = time.localtime(time.time())
                fecha = time.strftime('%Y%m%d%H%M%S', t)
                log_fich(LOG_PATH, fecha, evento)

        elif diferente:
            line = self.rfile.read().decode('utf-8').split()[0]
            evento = "Received from " + IP_REGPROXY + ":" + PORT_REGPROXY
            evento += ": " + line + "\r\n\r\n"
            fecha = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            log_fich(LOGFICH, fecha, evento)

            # Petición de otro método diferente a los descritos
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n")

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
