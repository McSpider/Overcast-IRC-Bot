#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import string, re

import importlib
from utils import *

import logging
log = logging.getLogger(__name__)


class channels:
    def __init__(self, delegate):
        self._irc = delegate
        self.list = {}

        self.chantypes = ""

        # self.list[##test] = (channel(self,"##test"))
        pass

    def join(self, channel_name):
        log.info(color.blue + 'Joining channel: ' + color.clear + channel_name)
        self.list[channel_name] = channel(channel_name)
        self._irc.sendRaw(('JOIN :%s\r\n' % channel_name), "IMPORTANT")

    def part(self, channel_name):
        log.info(color.blue + 'Parting channel: ' + color.clear + channel_name)
        self._irc.sendRaw(('PART %s \r\n' % channel_name), "IMPORTANT")

    def ignore(self, channel_name, flag):
        log.info(color.blue + 'Ignoring chat from channel: ' + color.clear + channel_name + strFromBool(flag))
        if channel_name in self.list:
            self.list[channel_name].ignored = flag

    def joinedTo(self, channel_name):
        log.info(color.blue + 'Joined channel: ' + color.clear + channel_name)
        if channel_name in self.list:
            self.list[channel_name].connected = True

    def partedFrom(self, channel_name):
        log.info(color.blue + 'Parted channel: ' + color.clear + channel_name)
        if channel_name in self.list:
            self.list[channel_name].connected = False

    def kickedFrom(self, channel_name):
        log.info(color.red + 'Kicked from channel: ' + color.clear + channel_name)
        if channel_name in self.list:
            self.list[channel_name].connected = False

    def isConnectedTo(self, channel_name):
        if channel_name in self.list:
            return self.list[channel_name].connected
        return False

    def isIgnoring(self, channel_name):
        if channel_name in self.list:
            return self.list[channel_name].ignored
        return False

    def hasFlagIn(self, flag, channel_name):
        if channel_name in self.list:
            if flag in self.list[channel_name].my_flags:
                return True
        return False

    def flagIn(self, flag, channel_name, bool):
        if channel_name in self.list:
            if bool:
                self.list[channel_name].my_flags.append(flag)
            else:
                if flag in self.list[channel_name].my_flags:
                    self.list[channel_name].my_flags.remove(flag)
            return True
        return False

    def isValidChannelName(self, string_in):
        for char in self.chantypes:
            if string_in.startswith(char):
                return True
        return False

    def voiceUser(self, username, in_channel, auto_voice):
        return False
        pass


    def userIsVoiced(self, username, in_channel, recursive):
        return False
        pass


class channel:
    def __init__(self, name):
        self.name = name;
        self.users = {} # {"username":["flag","+v"]}
        self.flags = [] # ["flag","+v"]
        self.my_flags = []
        self.connected = False
        self.ignored = False
        pass




