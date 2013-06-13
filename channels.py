#!/usr/bin/env python
import os, sys
import string, re

import config
import importlib
from utils import *


class channels:
    def __init__(self):
        pass

    def isConnectedToChannel(self,channel):
        pass

    def isOpedInChannel(self,channel):
        pass

    def join(self, irc, channel):
        print color.blue + 'Joining channel: ' + color.clear + channel
        irc.sendRaw(('JOIN :%s\r\n' % channel))

    def part(self, irc, channel):
        pass