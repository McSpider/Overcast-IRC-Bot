#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import string
import datetime

import urllib
from bs4 import BeautifulSoup
from utils import *

import logging
log = logging.getLogger(__name__)


class function_template(object):
    def __init__(self):
        self.name = None

        # Register the function types, COMMAND, KEY, NATURAL and STATUS
        # Command functions parse text messages for the functions commands.
        # - If no match is found the function is ignored.
        # Natural & Status functions parse all text & status messages respectively.
        # Key functions handle all messages sent by a user/channel if they have a key lock.
        # - If the user/channel does not have key lock the function is ignored.
        # All functions should return True if they do anything, e.g. send messages, update data files.
        self.type = ["command"]

        # Specify the functions priority from 100 to 1, one being the highest priority
        self.priority = 50

        # Specify the functions triggerable commands. (Not needed for natural functions.)
        self.commands = []

        # Specify if the function requires auth status, can also be handled manually if individual sub commands need to be restricted.
        self.restricted = False

        # Specify the functions function, this is the description shown in the help list.
        self.function_string = "Function template."
        # The functions help string, shown when running help on a specific function.
        # Multiple lines can be separated with the newline (\n) character.
        # The short trigger can be specified with {t} and will be dynamically replaced when the the help string is shown via the help function.
        self.help_string = None

        # Specify if the function blocks any other functions that come after itself and are triggerable with the same parameters.
        # Not used with KEY type functions since they are always blocking.
        self.blocking = True

        # The functions run count, incremented every time the function is triggered.
        self.run_count = 0

        # Used when the function is of type KEY to check if the lock is currently active.
        self.key_lock = []

        # Used to hide the function from the help list.
        self.hidden = False

        # Disable a function for specific period of time.
        self.disabled = None #{disabled_by:"", time:""}

    def load(self, bot):
        log.debug("Function load: " + self.name)
        self._bot = bot

    def unload(self, bot):
        log.debug("Function unload: " + self.name)


    def main(self, bot, msg_data, func_type):
        function_name = string.split(self.name,".")[0]
        irc.sendMSG("Function not setup, still using template: " + function_name, bot.master_channel)
        return True

    # Load and save function JSON data files
    # - Files are stored in ./_functiondata/
    # - The optional default argument specifies the data to create the file with if no file is found
    # - If None is specified no file will be created (defaults to None)
    def loadFunctionDataFile(self, filename, default = None):
        function_name = string.split(self.name,".")[0]
        directory = '_functiondata/' + str(function_name)
        data = self._bot.openDataFile('_'+ filename, directory, default)

        return data

    def saveDataToDataFile(self, data, filename):
        function_name = string.split(self.name,".")[0]
        directory = '_functiondata/' + str(function_name)
        self._bot.saveDataFile(data, '_'+ filename, directory)


    # Load a file and split it into a list of lines.
    # - Ignores empty lines and lines commented with a hash (#)
    def loadMessagesFile(self, filename):
        filename = './_data/' + filename
        lines1 = open(filename).read().splitlines()
        lines2 = [line for line in lines1 if not line.startswith('#')]
        lines3 = [line for line in lines2 if line]

        return lines3

    # Load and parse a JSON data file
    # - Returns the files data or None if no data/file is found
    def loadDataFile(self, filename):
        directory = '_data/'
        data = self._bot.openDataFile(filename, directory)

        return data

    def hasKeyLockFor(self, entity):
        if entity in self.key_lock:
            return True
        return False

    def addToKeyLock(self, entity):
        log.info(color.cyan + "Adding " + entity + " to key lock" + color.clear)
        self.key_lock.append(entity)

    def removeFromKeyLock(self, entity):
        log.info(color.cyan + "Removing key lock for " + entity + color.clear)
        self.key_lock.append(entity)


def prettyListString(alist, joiner, cc = None, capitalize = False):
    if capitalize:
        alist = [item.capitalize() for item in alist]

    if not cc == None:
        alist = [cc + item + color.irc_clear for item in alist]

    if len(alist) > 1:
        result = ", ".join(alist[:-1])
        if len(alist) > 1:
            result = result + joiner + alist[-1]
        return result
    elif len(alist) == 1: return alist[0]

def colorizer(message):
    message = message.replace("&00", color.irc_boldwhite)
    message = message.replace("&01", color.irc_black)
    message = message.replace("&02", color.irc_blue)
    message = message.replace("&03", color.irc_green)
    message = message.replace("&04", color.irc_boldred)
    message = message.replace("&05", color.irc_red)
    message = message.replace("&06", color.irc_violet)
    message = message.replace("&07", color.irc_yellow)
    message = message.replace("&08", color.irc_boldyellow)
    message = message.replace("&09", color.irc_boldgreen)
    message = message.replace("&10", color.irc_cyan)
    message = message.replace("&11", color.irc_boldcyan)
    message = message.replace("&12", color.irc_boldblue)
    message = message.replace("&13", color.irc_boldviolet)
    message = message.replace("&14", color.irc_boldblack)
    message = message.replace("&15", color.irc_white)

    # message = message.replace("&b", color.irc_bold)
    # message = message.replace("&i", color.irc_italic)
    # message = message.replace("&u", color.irc_underline)
    message = message.replace("&c", color.irc_clear)
    return message

def parseTimeDelta(str_input):
    value = str_input
    if str_input.endswith(("s","m","h","d")):
        value = str_input[:-1]

    if not value.isalnum():
        return False
    value = int(value)

    if str_input.endswith("s"):
        return datetime.timedelta(seconds = value)
    elif str_input.endswith("h"):
        return datetime.timedelta(hours = value)
    elif str_input.endswith("d"):
        return datetime.timedelta(days = value)
    else:
        return datetime.timedelta(minutes = value)

    return False

def pageFromList(page_list, page_index, page_size):
    start = (page_index - 1) * page_size
    end = start + page_size

    if start >= len(page_list):
        start = 0
        end = page_size
    elif end >= len(page_list):
        end = len(page_list)

    return page_list[start:end]

