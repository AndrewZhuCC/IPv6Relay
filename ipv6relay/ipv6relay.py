#!/usr/bin/env python
# encoding: utf-8

import SocketServer
import select
from optparse import OptionParser
import sys
import threading
import socket

class TCPSocketRelay(object):
    def __init__(self, a, b, maxbuf=65535):
        self.a = a
        self.b = b
        self.maxbuf = maxbuf
        self.atob = ""
        self.btoa = ""

    def handle(self):
        while True:
            rlist = []
            wlist = []
            xlist = [self.a, self.b]
            if self.atob:
                wlist.append(self.b)
            if self.btoa:
                wlist.append(self.a)
            if len(self.atob) < self.maxbuf:
                rlist.append(self.a)
            if len(self.btoa) < self.maxbuf:
                rlist.append(self.b)

            rlo, wlo, xlo = select.select(rlist, wlist, xlist)
            if xlo:
                return
            if self.a in wlo:
                n = self.a.send(self.btoa)
                self.btoa = self.btoa[n:]
                print "sending-------> TCP local:[%s]:%s sending (%d)bytes to remote:[%s]:%s" % (self.b.getsockname()[0], self.b.getsockname()[1], n, self.a.getsockname()[0], self.a.getsockname()[1])
            if self.b in wlo:
                n = self.b.send(self.atob)
                self.atob = self.atob[n:]
                print "sending-------> TCP remote:[%s]:%s sending (%d)bytes to local:[%s]:%s" % (self.a.getsockname()[0], self.a.getsockname()[1], n, self.b.getsockname()[0], self.b.getsockname()[1])
            if self.a in rlo:
                s = self.a.recv(self.maxbuf - len(self.atob))
                if not s:
                    print "closing-------> TCP remote:[%s]:%s local:[%s]:%s will close" % (self.a.getsockname()[0], self.a.getsockname()[1], self.b.getsockname()[0], self.b.getsockname()[1])
                    return
                print "recieving-----> TCP remote:[%s]:%s recieve (%d)bytes that will be sending to local:[%s]:%s" % (self.a.getsockname()[0], self.a.getsockname()[1], len(s), self.b.getsockname()[0], self.b.getsockname()[1])
                self.atob += s
            if self.b in rlo:
                s = self.b.recv(self.maxbuf - len(self.btoa))
                if not s:
                    print "closing-------> TCP remote:[%s]:%s local:[%s]:%s will close" % (self.a.getsockname()[0], self.a.getsockname()[1], self.b.getsockname()[0], self.b.getsockname()[1])
                    return
                print "recieving-----> TCP local:[%s]:%s recieve (%d)bytes that will be sending to remote:[%s]:%s" % (self.b.getsockname()[0], self.b.getsockname()[1], len(s), self.a.getsockname()[0], self.a.getsockname()[1])
                self.btoa += s

            #print "Relay iter: %8d atob, %8d btoa, lists: %r %r %r"%(len(self.atob), len(self.btoa), rlo, wlo, xlo)

class TCPRelay(SocketServer.BaseRequestHandler):
    def handle(self):
        print "TCP Incoming from %s:%d"%(self.client_address[0], self.client_address[1])
        dsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        lsock = self.request
        host = remoteHost
        port = int(remotePort)
        print "connecting----> TCP connect to [%s]:%d"%(host, port)
        dsock.connect((host, port))
        dsock.send(password)
        s = dsock.recv(self.server.bufsize * 1024)
        if s != '200ok':
            dsock.close()
            lsock.close()
            print 'Password error'
            return
        try:
            fwd = TCPSocketRelay(dsock, lsock, self.server.bufsize * 1024)
            fwd.handle()
        finally:
            dsock.close()
            lsock.close()
        print "closed--------> %s:%d Connection closed" % (self.client_address[0], self.client_address[1])

class UDPSocketRelay(object):
    def __init__(self, a, b, sb, btoa, maxbuf=65535): # b->local, a->remote
        self.a = a
        self.b = b
        self.sa = socket.socket(socket.AF_INET6, socket.SOCK_DRAM)
        self.sb = sb
        self.maxbuf = maxbuf
        self.atob = ""
        self.btoa = btoa

    def handle(self):
        while True:
            rlist = []
            wlist = []
            xlist = [self.sa, self.sb]
            if self.atob:
                wlist.append(self.sb)
            if self.btoa:
                wlist.append(self.sa)
            if len(self.atob) < self.maxbuf:
                rlist.append(self.sa)
            if len(self.btoa) < self.maxbuf:
                rlist.append(self.sb)

            rlo, wlo, xlo = select.select(rlist, wlist, xlist)
            if xlo:
                return
            if self.sa in wlo:
                n = self.sa.sendto(self.btoa, self.a)
                self.btoa = self.btoa[n:]
                print "UDP local:%s(%s) sending (%d)bytes to remote:%s (%s)" % (self.sb.getsockname()[0], self.sb.getsockname()[1], n, self.sa.getsockname()[0], self.sa.getsockname()[1])
            if self.sb in wlo:
                n = self.sb.sendto(self.atob, self.b)
                self.atob = self.atob[n:]
                print "UDP remote:%s(%s) sending (%d)bytes to local:%s (%s)" % (self.sa.getsockname()[0], self.sa.getsockname()[1], n, self.sb.getsockname()[0], self.sb.getsockname()[1])
            if self.sa in rlo:
                s = self.sa.recv(self.maxbuf - len(self.atob))
                if not s:
                    print "UDP remote:%s(%s) local:%s (%s) will close" % (self.sa.getsockname()[0], self.sa.getsockname()[1], self.sb.getsockname()[0], self.sb.getsockname()[1])
                    return
                print "UDP remote:%s(%s) recieve (%d)bytes that will be sending to local:%s (%s)" % (self.sa.getsockname()[0], self.sa.getsockname()[1], len(s), self.sb.getsockname()[0], self.sb.getsockname()[1])
                self.atob += s
            if self.sb in rlo:
                s = self.sb.recv(self.maxbuf - len(self.btoa))
                if not s:
                    print "UDP remote:%s(%s) local:%s (%s) will close" % (self.sa.getsockname()[0], self.sa.getsockname()[1], self.sb.getsockname()[0], self.sb.getsockname()[1])
                    return
                print "UDP local:%s(%s) recieve (%d)bytes that will be sending to remote:%s (%s)" % (self.sb.getsockname()[0], self.sb.getsockname()[1], len(s), self.sa.getsockname()[0], self.sa.getsockname()[1])
                self.btoa += s

            #print "Relay iter: %8d atob, %8d btoa, lists: %r %r %r"%(len(self.atob), len(self.btoa), rlo, wlo, xlo)

class UDPRelay(SocketServer.BaseRequestHandler):
    def handle(self):
        print "UDP Incoming from %s:%d"%(self.client_address[0], self.client_address[1])
        lsock = self.request[1]
        host = remoteHost
        port = int(remotePort)
        print "UDP connect to %s:%d"%(host, port)
        try:
            fwd = UDPSocketRelay((host, port), self.client_address, lsock, self.request[0], self.server.bufsize * 1024)
            fwd.handle()
        except:
            print "Connection closed"


class TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True
class ThreadedTCPServer(SocketServer.ThreadingMixIn, TCPServer):
    pass
class UDPServer(SocketServer.UDPServer):
    allow_reuse_address = True
class ThreadedUDPServer(SocketServer.ThreadingMixIn, UDPServer):
    pass

parser = OptionParser(usage="usage: %prog [OPTIONS] RemoteIP RemotePort Password")
options, args = parser.parse_args()

if len(args) != 3:
    parser.print_help()
    sys.exit(1)

remoteHost, remotePort, password = args

host = "localhost"

tcpserver = ThreadedTCPServer((host, 1080), TCPRelay)
udpserver = ThreadedUDPServer((host, 1080), UDPRelay)
tcpserver.bufsize = 128
udpserver.bufsize = 128
servers = [tcpserver, udpserver]

alive = True

print "start relay from localhost:1080 ----> [%s]:%s" % (remoteHost, remotePort)
while alive:
    try:
        rl, wl, xl = select.select(servers, [], [])
        for server in rl:
            server.handle_request()
    except:
        alive = False
