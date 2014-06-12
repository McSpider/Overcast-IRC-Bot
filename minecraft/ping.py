import socket
from struct import pack, unpack
import json
from time import time

# http://wiki.vg/Server_List_Ping
# Original code: https://gist.github.com/barneygale/1209061
# Modified by McSpider on Apr 09, 2014 to include the ping time in the result

def unpack_varint(s):
    d = 0
    for i in range(5):
        b = ord(s.recv(1))
        d |= (b & 0x7F) << 7*i
        if not b & 0x80:
            break
    return d

def pack_varint(d):
    o = ""
    while True:
        b = d & 0x7F
        d >>= 7
        o += pack("B", b | (0x80 if d > 0 else 0))
        if d == 0:
            break
    return o

def pack_data(d):
    return pack_varint(len(d)) + d

def pack_port(i):
    return pack('>H', i)

def pack_time(l):
    return pack('>q', l)

def unpack_time(d):
    return unpack('>q', d)[0]

def get_info(host='localhost', port=25565):
    
    # Connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
    except:
        raise
    
    # Send handshake + status request
    s.send(pack_data("\x00\x00" + pack_data(host.encode('utf8')) + pack_port(port) + "\x01"))
    s.send(pack_data("\x00"))
    
    # Read response
    unpack_varint(s)     # Packet length
    unpack_varint(s)     # Packet ID
    l = unpack_varint(s) # String length
    
    d = ""
    while len(d) < l:
        d += s.recv(1024)

    json_data = json.loads(d.decode('utf8'))

    # Send ping request
    t = long(round(time() * 1000))
    s.send(pack_data("\x01" + pack_time(t)))

    # Read response
    pl = unpack_varint(s) # Packet length
    unpack_varint(s)      # Packet ID
    l = pl - 1            # Time length

    d = ""
    while len(d) < l:
        d += s.recv(64)

    t = long(round(time() * 1000))
    p = t - unpack_time(d)
    json_data[u"ping"] = str(p)

    # Close our socket
    s.close()
    
    # Load json and return
    return json_data
