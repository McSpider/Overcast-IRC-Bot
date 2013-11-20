#!/usr/bin/env python
import os, sys
import string, re

import importlib
from utils import *


class channels:
    def __init__(self, delegate):
        self._irc = delegate
        self.list = {}

        # self.list[##test] = (channel(self,"##test"))
        pass

    def join(self, chan):
        print color.blue + 'Joining channel: ' + color.clear + chan
        self.list[chan] = channel(chan)
        self._irc.sendRaw(('JOIN :%s\r\n' % chan))

    def part(self, chan):
        print color.blue + 'Parting channel: ' + color.clear + chan
        self._irc.sendRaw(('PART %s \r\n' % chan))

    def joinedTo(self, chan):
        print color.blue + 'Joined channel: ' + color.clear + chan
        if self.list.has_key(chan):
            self.list[chan].connected = True

    def partedFrom(self, chan):
        print color.blue + 'Parted channel: ' + color.clear + chan
        if self.list.has_key(chan):
            self.list[chan].connected = False

    def kickedFrom(self, chan):
        print color.red + 'Kicked from channel: ' + color.clear + chan
        if self.list.has_key(chan):
            self.list[chan].connected = False

    def isConnectedTo(self,chan):
        if self.list.has_key(chan):
            return self.list[chan].connected
        return False

    def hasFlagIn(self,flag,chan):
        if self.list.has_key(chan):
            if flag in self.list[chan].my_flags:
                return True
        return False

    def flagIn(self,flag,chan,bool):
        if self.list.has_key(chan):
            if bool:
                self.list[chan].my_flags.append(flag)
            else:
                self.list[chan].my_flags.remove(flag)
            return True
        return False


class channel:
    def __init__(self, name):
        self.name = name;
        self.users = {} # {"username":["flag","+v"]}
        self.flags = [] # ["flag","+v"]
        self.my_flags = []
        self.connected = False
        pass




