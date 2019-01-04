#!/usr/bin/python3
# -*- coding: utf-8 -*-

if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]
    except:
        sys.exit("Usage: python proxy_registrar.py config")

    serv = socketserver.UDPServer(('', int(PORT_SERVER)), EchoHandler)
    print("Server MiServidorBigBang listening at port 5555...")
