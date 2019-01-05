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

            acc = {}
            acc['name'] = attrs.get('name', "")
            acc['ip'] = attrs.get('ip', "")
            acc['puerto'] = attrs.get('puerto', "")

            self.tags['account'] = acc

        elif name == 'database':

            uas = {}
            uas['path'] = attrs.get('path', "")
            uas['passwdpath'] = attrs.get('passwdpath', "")

            self.tags['uaserver'] = uas

        elif name == 'log':

            rtp = {}
            rtp['path'] = attrs.get('path', "")

            self.tags['rtpaudio'] = rtp

    def get_tags(self):

        return self.tags

if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]
    except:
        sys.exit("Usage: python proxy_registrar.py config")

    serv = socketserver.UDPServer(('', int(PORT_SERVER)), EchoHandler)
    print("Server MiServidorBigBang listening at port 5555...")
