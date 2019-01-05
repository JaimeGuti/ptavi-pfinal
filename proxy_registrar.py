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

    serv = socketserver.UDPServer(('', int(SERVER_PORT)), EchoHandler)
    print("Server MiServidorBigBang listening at port 5555...")
