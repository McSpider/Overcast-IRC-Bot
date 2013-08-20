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
        self.blacklistedUsers = {} #{"~McSpider@192.65.241.17":"0"}

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

    def parseMessage(self, msgComponents, messageType, messageData):
        self._functions.checkForFunction(msgComponents, messageType, messageData)

    def isUserAuthed(self,user,hostmask):
        hostmask = string.split(hostmask,"!")[1]
        if (hostmask in self.authedHostmasks):
            return True

        return False

    def hostmaskBlacklisted(self,hostmask):
        for mask in self.blacklistedUsers:
            if re.match(mask, hostmask, re.IGNORECASE):
                return True
        return False

    def addBlacklistedHostmask(self,hostmask):
        if not hostmask in self.blacklistedUsers:
            self.blacklistedUsers.append(hostmask)
            return True
        return False

    def removeBlacklistedHostmask(self,hostmask):
        if hostmask in self.blacklistedUsers:
            self.blacklistedUsers.remove(hostmask)
            return True
        return False

    def notAllowedMessage(user,recipient):
        self._irc.sendMSG("%sYou're not allowed to do that %s%s" % (color.irc_red, user, color.irc_clear), recipient)

# Start the bot
try:
    _bot = bot()
    _bot.main()
except KeyboardInterrupt:
    pass
