#!/usr/bin/env python
import os, sys
import string, re

import config
import importlib
from utils import *


class channels:
    def __init__(self, delegate):
        self._irc = delegate
        pass

    def isConnectedToChannel(self,channel):
        pass

    def isOpedInChannel(self,channel):
        pass

    def join(self, channel):
        print color.blue + 'Joining channel: ' + color.clear + channel
        self._irc.sendRaw(('JOIN :%s\r\n' % channel))

    def part(self, channel):
        print color.blue + 'Parting channel: ' + color.clear + channel
        self._irc.sendRaw(('PART %s \r\n' % channel))

    def joinedTo(self, channel):
        print color.blue + 'Joined channel: ' + color.clear + channel
        config.channels[channel]["connected"] = True
        pass

    def partedFrom(self, channel):
        print color.blue + 'Parted channel: ' + color.clear + channel
        config.channels[channel]["connected"] = False
        pass

    def kickedFrom(self, channel):
        print color.red + 'Kicked from channel: ' + color.clear + channel
        config.channels[channel]["connected"] = False
        pass