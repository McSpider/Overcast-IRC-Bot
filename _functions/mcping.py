#!/usr/bin/env python
# -*- coding: utf-8 -*-
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["mcping"]
        self.function_string = "Ping a minecraft server."

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            argument = msg_data["message"][1]

            try:
              data = get_info(argument)
            except:
              bot._irc.sendMSG("Unable to connect to: %s" % (argument), msg_data["target"])
              raise
            
            if data:
                data["players"]["max"]
                data["players"]["online"]

                data["version"]["protocol"]
                data["version"]["name"]

                data["ping"]
                data["description"]

                ping_status = "Online Players: " + str(data["players"]["online"]) + "/" + str(data["players"]["max"])
                ping_status = ping_status + " - Ping: " + str(data["ping"]) + "ms"
                bot._irc.sendMSG("%s" % (ping_status), msg_data["target"])

                motd = string.split(data["description"].encode('utf-8'), "\n")

                prev_line_color = ""
                for line in motd:
                    bot._irc.sendMSG("%s%s" % (self.handleMcColors(prev_line_color).decode('utf-8'), self.handleMcColors(line).decode('utf-8')), msg_data["target"])
                    prev_line_color = re.findall("§[0-9a-fk-r]", line, re.IGNORECASE)[-1]
        else:
            bot._irc.sendMSG("Please provide a minecraft server address to ping.", msg_data["target"])


        return True

    # Converts minecraft color codes to irc colors
    # Ambiguous colors (colors that are hard to see on certain backgrounds)
    # are replaced with the clear color so that a irc client can pick a contrasting color
    def handleMcColors(self, string):
        string = string.replace("§0", color.irc_clear) # Black
        string = string.replace("§1", color.irc_blue)
        string = string.replace("§2", color.irc_green)
        string = string.replace("§3", color.irc_cyan)
        string = string.replace("§4", color.irc_red)
        string = string.replace("§5", color.irc_violet)
        string = string.replace("§6", color.irc_yellow)
        string = string.replace("§7", color.irc_clear) # Grey
        string = string.replace("§8", color.irc_clear) # Dark grey
        string = string.replace("§9", color.irc_blue)
        string = string.replace("§a", color.irc_green)
        string = string.replace("§b", color.irc_cyan)
        string = string.replace("§c", color.irc_red)
        string = string.replace("§d", color.irc_violet)
        string = string.replace("§e", color.irc_yellow)
        string = string.replace("§f", color.irc_clear) # White

        string = string.replace("§k", "")
        string = string.replace("§l", "")
        string = string.replace("§m", "")
        string = string.replace("§n", "")
        string = string.replace("§o", "")
        string = string.replace("§r", color.irc_clear)
        return string


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
