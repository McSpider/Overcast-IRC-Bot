#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import traceback
import socket, errno
from time import sleep

from irc import *
from functions import *
import ConfigParser
import json


import logging
setupLogging(logging.DEBUG,logging.DEBUG)
log = logging.getLogger('bot')

class bot:
    def __init__(self):
        self.irc = irc(self)

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
        auth_data = self.openDataFile("_authed", "", default = [])
        if type(auth_data) is list:
            self.authed_hostmasks = auth_data

        self.blacklisted_users = []
        blacklist_data = self.openDataFile("_blacklist", "", default = [])
        if type(blacklist_data) is list:
            self.blacklisted_users = blacklist_data


        self.triggers = filter(None, [self.nick + ":"] + config.get('bot_config', 'triggers').split(','))
        self.short_trigger = config.get('bot_config', 'short_trigger')

        self.intentional_disconnect = False;
        self.disconnected_errno = None;
        self.reconnect_count = 0;
        self.reconnect_limit = 5;

        agent_str = "Overcast IRC Bot/1.0 (https://github.com/McSpider/Overcast-IRC-Bot)"
        self.http_header = {'User-Agent': agent_str + ' (' + str(self.server) + " / " + str(self.nick) + ")"}
        self.functions = functions(self, self.irc)

        attrs = vars(self)
        log.debug(', '.join("%s: %s" % item for item in attrs.items()) + "\n")

    def unload(self):
        self.functions.unloadFunctions()

        self.saveDataFile(self.authed_hostmasks,"_authed","")
        self.saveDataFile(self.blacklisted_users,"_blacklist","")


    def main(self):
        log.info(color.bold + "Overcast IRC Bot - Hi! \n" + color.clear)
        did_connect = False
        reconnect_delay = 5
        reconnect_count = 0
        while did_connect == False and reconnect_count < self.reconnect_limit:
            did_connect = self.irc.connectToServer(self.server,self.server_port)
            if not did_connect:
                log.error(color.b_red + "Overcast IRC Bot - Failed to connect, retrying. (attempt #%s, delay %s sec) \n" % (reconnect_count + 1, reconnect_delay) + color.clear)
                sleep(reconnect_delay)
                reconnect_delay = reconnect_delay * 2
                reconnect_count += 1

        if did_connect:
            self.irc.authUser(self.ident,self.nick,self.realname,self.password)
            self.irc.read() # Blocks till the socket closes

        self.irc.disconnect()
        self.unload()

        if self.intentional_disconnect:
            return 0
        if not did_connect:
            return 0

        if self.disconnected_errno: log.debug(errno.errorcode[self.disconnected_errno])
        if self.reconnect_count < self.reconnect_limit:
            self.reconnect_count += 1
            return 1

        return 0

    def parseMessage(self, msgComponents, messageType, messageData):
        self.functions.checkForFunction(msgComponents, messageType, messageData)

    def isUserAuthed(self, hostmask):
        for mask in self.authed_hostmasks:
            regex_mask = self.simplifiedMatcherToRegex(mask)
            if re.match("^%s$" % regex_mask, hostmask, re.IGNORECASE):
                return True
        return False

    def addAuthedHostmask(self, hostmask):
        if not hostmask in self.authed_hostmasks:
            self.authed_hostmasks.append(hostmask)
            return True
        return False

    def removeAuthedHostmask(self, hostmask):
        if hostmask in self.authed_hostmasks:
            self.authed_hostmasks.remove(hostmask)
            return True
        return False

    # Checks if a IRC hostmask is blacklisted
    # - If a match is found the hostmask matcher is returned
    # - If no match is found returns False
    def hostmaskBlacklisted(self,hostmask):
        for mask in self.blacklisted_users:
            regex_mask = self.simplifiedMatcherToRegex(mask)
            if re.match("^%s$" % regex_mask, hostmask, re.IGNORECASE):
                return mask
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

    # Escapes and converts a simplified matcher string to valid regex.
    # - Currently only supports * as a wildcard
    def simplifiedMatcherToRegex(self, mask):
        regex_mask = re.escape(mask)
        regex_mask = regex_mask.replace("\*",".*")
        return regex_mask


    # Open a JSON data file
    # - The optional default argument specifies the data to create the file with if no file is found
    # - If None is specified no file will be created (defaults to None)
    def openDataFile(self, filename, directory, default = None):
        data = None
        data_file = directory + str(filename) + '.json'
        try:
            with open(data_file, 'r') as input:
                try:
                    data = json.load(input)
                except Exception, e:
                    log.error(color.red + "Malformed JSON data file: " + color.clear + data_file)
                    trace = traceback.format_exc()
                    log.error(color.red + trace + color.clear)

        except IOError:
            log.info(color.red + "Data file not found: " + color.clear + data_file)
            if default != None:
                with open(data_file, 'w') as output:
                    json.dump(default, output, sort_keys=True, indent=4, separators=(',', ': '))

        data = self.decodeutf8(data)
        return data

    # Save a JSON data file
    def saveDataFile(self, data, filename, directory):
        data = self.encodeutf8(data)
        data_file = directory + str(filename) + '.json'
        with open(data_file, 'w') as output:
            json.dump(data, output, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

    def encodeutf8(self, input):
        if isinstance(input, dict):
            return {self.encodeutf8(key): self.encodeutf8(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.encodeutf8(element) for element in input]
        elif isinstance(input, unicode):
            try:
                return input.encode('utf-8')
            except Exception, e:
                trace = traceback.format_exc()
                log.error(color.red + trace + color.clear)
                return input
        else:
            return input

    def decodeutf8(self, input):
        if isinstance(input, dict):
            return {self.decodeutf8(key): self.decodeutf8(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [self.decodeutf8(element) for element in input]
        elif isinstance(input, str):
            try:
                return input.decode('utf-8')
            except Exception, e:
                trace = traceback.format_exc()
                log.error(color.red + trace + color.clear)
                return input
        else:
            return input


    def notAllowedMessage(self,user,recipient):
        self.irc.sendMSG("%sYou're not allowed to do that %s%s" % (color.irc_red, user, color.irc_clear), recipient)


# Start the bot
try:
    status = -1
    while status != 0:
        _bot = bot()
        try:
            status = _bot.main()
            if status == 1:
                log.error(color.b_red + "Overcast IRC Bot - Unintentionally disconnected, reconnecting. %s\n" % (self.disconnected_errno,) + color.clear)
        except Exception, e:
            trace = traceback.format_exc()
            log.error(color.red + trace + color.clear)
    
    log.info(color.bold + "Overcast IRC Bot - Shutdown, have a nice day." + color.clear)

except KeyboardInterrupt:
    pass
