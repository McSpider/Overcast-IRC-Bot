#!/usr/bin/env python
import sys
import traceback
import socket
from time import sleep

from irc import *
from functions import *
import ConfigParser
import json

class bot:
    def __init__(self):
        self._irc = irc(self)

        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')

        self.ident = config.get('irc_config', 'ident')
        self.password = config.get('irc_config', 'password')
        self.nick =  config.get('irc_config', 'nick')
        self.realname = config.get('irc_config', 'realname')

        self.server = config.get('irc_config', 'server')
        self.server_port = config.getint('irc_config', 'server_port')

        self.autojoin_channels = filter(None, config.get('bot_config', 'autojoin_channels').split(','))
        self.master_channel = config.get('bot_config', 'master_channel')

        self.authed_hostmasks = filter(None, config.get('bot_config', 'master_auth').split(','))
        auth_data = self.openDataFile("authed","")
        if type(auth_data) is list:
            self.authed_hostmasks = auth_data

        self.blacklisted_users = []
        blacklist_data = self.openDataFile("blacklist","")
        if type(blacklist_data) is list:
            self.blacklisted_users = blacklist_data


        self.debug = config.get('bot_config', 'debug')
        self.triggers = filter(None, [self.nick + ":"] + config.get('bot_config', 'triggers').split(','))
        self.short_trigger = config.get('bot_config', 'short_trigger')

        self.intentional_disconnect = False;
        self.reconnect_count = 0;
        self.reconnect_limit = 5;
        self.disconnected_errno = None;

        self._functions = functions(self, self._irc)

        if self.debug:
            attrs = vars(self)
            print ', '.join("%s: %s" % item for item in attrs.items())

    def unload(self):
        self._functions.unloadFunctions()

        self.saveDataFile(self.authed_hostmasks,"authed","")
        self.saveDataFile(self.blacklisted_users,"blacklist","")


    def main(self):
        print color.b_cyan + "Overcast IRC Bot - Hi! \n" + color.clear
        self._irc.connectToServer(self.server,self.server_port)
        self._irc.authUser(self.ident,self.nick,self.realname,self.password)

        self._irc.read()
        self._irc.disconnect()

        self.unload()

        if not self.intentional_disconnect and self.reconnect_count < self.reconnect_limit:
            if (self.disconnected_errno != errno.ECONNRESET):
                return 0

            self.reconnect_count += 1
            print color.b_red + "\nOvercast IRC Bot - Unintentionally disconnected!" + color.clear
            return 1

        return 0

    def parseMessage(self, msgComponents, messageType, messageData):
        self._functions.checkForFunction(msgComponents, messageType, messageData)

    def isUserAuthed(self,hostmask):
        hostmask = string.split(hostmask,"!")[1]
        for mask in self.authed_hostmasks:
            if re.match(".*%s.*" % mask, hostmask, re.IGNORECASE):
                return True
        return False

    def hostmaskBlacklisted(self,hostmask):
        for mask in self.blacklisted_users:
            if re.match(".*%s.*" % mask, hostmask, re.IGNORECASE):
                return True
        return False

    def addBlacklistedHostmask(self,hostmask):
        if not hostmask in self.blacklisted_users:
            self.blacklisted_users.append(hostmask)
            return True
        return False

    def removeBlacklistedHostmask(self,hostmask):
        if hostmask in self.blacklisted_users:
            self.blacklisted_users.remove(hostmask)
            return True
        return False

    def openDataFile(self, file, directory):
        data = None
        data_file = directory + '_'+ str(file) + '.json'
        try:
            with open(data_file, 'r') as input:
                data = json.load(input)
            return data
        except IOError:
            print color.red + "Data file not found: " + color.clear + data_file
            with open(data_file, 'w') as output:
                json.dump(data, output, sort_keys=True, indent=4, separators=(',', ': '))

        return data

    def saveDataFile(self, data, file, directory):
        data_file = directory + '_'+ str(file) + '.json'
        with open(data_file, 'w') as output:
            json.dump(data, output, sort_keys=True, indent=4, separators=(',', ': '))


    def notAllowedMessage(self,user,recipient):
        self._irc.sendMSG("%sYou're not allowed to do that %s%s" % (color.irc_red, user, color.irc_clear), recipient)


# Start the bot
try:
    status = -1
    while status != 0:
        if status == 1:
            print color.b_red + "\nOvercast IRC Bot - Unintentionally disconnected, reconnecting. " + color.clear
        _bot = bot()
        try:
            status = _bot.main()
        except Exception, e:
            trace = traceback.format_exc()
            print color.red + trace + color.clear
    
    print color.b_cyan + "\nOvercast IRC Bot - Shutdown, have a nice day." + color.clear

except KeyboardInterrupt:
    pass
