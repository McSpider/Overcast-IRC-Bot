#!/usr/bin/env python

host = "irc.esper.net"
port = 6667
nick = "Overcast"
ident = "McSpider"
password = "sn0w.spider"
realname = "Overcast - Python IRC Bot"
channels = {"##mcspider":{"connected":False,"chanFlags":None,"botFlags":None},"#overcastnetwork":{"connected":False,"chanFlags":None,"botFlags":None}}
masterChannel = "##mcspider"

authedHostmasks = ["McSpider@192.65.241.17","plastix@192.65.241.17"]

debug = True
triggers = [nick + ":","oc."]
