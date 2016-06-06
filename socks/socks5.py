#!/usr/bin/env python
# encoding: utf-8

import socket, sys, select, SocketServer, struct, time, signal

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass
class Socks5Server(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        print "local: " + sock.getsockname()[0] + " " + str(sock.getsockname()[1])
        print "remote: " + remote.getsockname()[0] + " " + str(remote.getsockname()[1])
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                #print 'relay from local to remote'
                if remote.send(sock.recv(4096)) <= 0: break
            if remote in r:
                #print 'relay from remote to local'
                if sock.send(remote.recv(4096)) <= 0: break
    def handle(self):
        try:
            sock = self.connection
            print "connection from %s %d" %(self.client_address[0], self.client_address[1])

            pwddata = sock.recv(1024)
            if pwddata == password:
                sock.send('200ok')
            else:
                sock.send('403')
                print 'Password Error'
                return

            sock.recv(262)
            sock.send('\x05\x00')

            data = self.rfile.read(4)
            mode = ord(data[1])
            addrtype = ord(data[3])
            if addrtype == 1:
                addr = socket.inet_ntoa(self.rfile.read(4))
            elif addrtype == 3:
                addr = self.rfile.read(ord(sock.recv(1)[0]))
            port = struct.unpack('>H', self.rfile.read(2))
            reply = "\x05\x00\x00\x01"
            try:
                if mode == 1:
                    #socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8087)
                    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote.connect((addr, port[0]))
                else:
                    reply = "\x05\x07\x00\x01"
                local = remote.getsockname()
                reply += socket.inet_aton(local[0]) + struct.pack(">H", local[1])
            except socket.error:
                reply = '\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00'
            sock.send(reply)
            sreply = ''.join([str(ord(c)) for c in reply])
            print 'send reply %s' % sreply
            if reply[1] == '\x00':
                if mode == 1:
                    self.handle_tcp(sock, remote)
        except socket.error:
            print "socket error"
        except IndexError:
            print "index error"

filename = sys.argv[0]
if len(sys.argv) < 4:
    print 'usage: ' + filename + ' IPaddress port password'
    sys.exit()
sock_address = sys.argv[1]
sock_port = int(sys.argv[2])
password = sys.argv[3]
serverclass = ThreadingTCPServer
serverclass.address_family = socket.AF_INET6
server = serverclass((sock_address, sock_port), Socks5Server)
print 'bind address: %s port: %d' % (sock_address, sock_port) + ' ok!'
#def child_handler(signum, _):
#    print "received SIGQUIT, shutting down....  signum: %d" % signum
#    server.shutdown()
#    server.server_close()
#signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), child_handler)
#def int_handler(signum, _):
#    print "received SIGINT, shutting down....  signum: %d" % signum
#    server.shutdown()
#    server.server_close()
#    sys.exit(1)
#signal.signal(signal.SIGINT, int_handler)
server.serve_forever()
