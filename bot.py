#!/usr/bin/env python
import sys
from time import sleep

from irc import *
from functions import *
import config

class bot:
    def __init__(self):
        self._irc = irc(self)
        self._functions = functions(self)


    def main(self):
        print color.b_cyan + "Overcast IRC Bot - Hi! \n" + color.clear
        self._irc.connectToServer(config.host,config.port)
        self._irc.authUser(config.ident,config.nick,config.realname,config.password)

        self._irc.read()
        self._irc.disconnect()
        print color.b_cyan + "\nOvercast IRC Bot - Shutdown, have a nice day. " + color.clear

    def parseMessage(self, msgComponents, messageType):
        self._functions.checkForFunction(msgComponents, messageType)

    def isUserAuthed(self,user,hostmask):
        hostmask = string.split(hostmask,"!~")[1]
        if (hostmask in config.authedHostmasks):
            return True

        return False

# Start the bot
try:
    _bot = bot()
    _bot.main()
except KeyboardInterrupt:
    pass

