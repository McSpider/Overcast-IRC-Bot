#!/usr/bin/env python
import sys
from time import sleep

from irc import *
from functions import *
import ConfigParser

class bot:
    def __init__(self):
        self._irc = irc(self)
        self._functions = functions(self,self._irc)

        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')

        self.ident = config.get('irc_config', 'ident')
        self.password = config.get('irc_config', 'password')
        self.nick =  config.get('irc_config', 'nick')
        self.realname = config.get('irc_config', 'realname')

        self.server = config.get('irc_config', 'server')
        self.serverPort = config.getint('irc_config', 'server_port')

        self.autojoin_channels = filter(None, config.get('bot_config', 'autojoin_channels').split(','))
        self.masterChannel = config.get('bot_config', 'master_channel')

        self.authedHostmasks = ["~McSpider@192.65.241.17","~plastix@192.65.241.17"]
        self.blacklistedUsers = [] #{} #{"~McSpider@192.65.241.17":"0"}


        self.debug = config.get('bot_config', 'debug')
        self.triggers = filter(None, [self.nick + ":"] + config.get('bot_config', 'triggers').split(','))
        self.shortTrigger = config.get('bot_config', 'short_trigger')

        self.intentionalDisconnect = False;
        self.reconnectCount = 0;
        self.reconnectLimit = 5;

        if self.debug:
            attrs = vars(self)
            print ', '.join("%s: %s" % item for item in attrs.items())


    def main(self):
        print color.b_cyan + "Overcast IRC Bot - Hi! \n" + color.clear
        self._irc.connectToServer(self.server,self.serverPort)
        self._irc.authUser(self.ident,self.nick,self.realname,self.password)

        self._irc.read()
        self._irc.disconnect()

        if not self.intentionalDisconnect and self.reconnectCount < self.reconnectLimit:
            self.reconnectCount += 1
            return 1

        return 0

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
    status = -1
    while status != 0:
        if status == 1:
            print color.b_red + "\nOvercast IRC Bot - Unintentionally disconnected, reconnecting. " + color.clear
        _bot = bot()
        status = _bot.main()
    
    print color.b_cyan + "\nOvercast IRC Bot - Shutdown, have a nice day. " + color.clear

except KeyboardInterrupt:
    pass
