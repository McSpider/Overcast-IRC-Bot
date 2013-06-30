#!/usr/bin/env python
import sys
from time import sleep

from irc import *
from functions import *
import ConfigParser

class bot:
    def __init__(self):
        self._irc = irc(self)
        self._functions = functions(self)

        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')

        self.ident = config.get('irc_config', 'ident')
        self.password = config.get('irc_config', 'password')
        self.nick =  config.get('irc_config', 'nick')
        self.realname = config.get('irc_config', 'realname')

        self.server = config.get('irc_config', 'server')
        self.serverPort = config.getint('irc_config', 'server_port')

        self.channels = {"##testchan123":{"connected":False,"chanFlags":[],"botFlags":[]}}
        self.masterChannel = "##testchan123"

        self.authedHostmasks = ["User@123.145.457.342"]

        self.debug = True
        self.triggers = [self.nick + ":"]
        self.shortTrigger = "!"



    def main(self):
        print color.b_cyan + "Overcast IRC Bot - Hi! \n" + color.clear
        self._irc.connectToServer(self.server,self.serverPort)
        self._irc.authUser(self.ident,self.nick,self.realname,self.password)

        self._irc.read()
        self._irc.disconnect()
        print color.b_cyan + "\nOvercast IRC Bot - Shutdown, have a nice day. " + color.clear

    def parseMessage(self, msgComponents, messageType):
        self._functions.checkForFunction(msgComponents, messageType)

    def isUserAuthed(self,user,hostmask):
        hostmask = string.split(hostmask,"!")[1]
        if (hostmask in self.authedHostmasks):
            return True

        return False

    def notAllowedMessage(user,recipient):
        self._irc.sendMSG("%s%sYou're not allowed to do that %s%s" % (color.irc_red, color.irc_bold, user, color.irc_clear), recipient)

# Start the bot
try:
    _bot = bot()
    _bot.main()
except KeyboardInterrupt:
    pass
