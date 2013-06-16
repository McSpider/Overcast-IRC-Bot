#!/usr/bin/env python
import config

import re
import string

import urllib
from bs4 import BeautifulSoup


class function_template(object):
    def __init__(self):
        self.name = None

        # Register the funtion types, COMMAND, NATURAL and STATUS
        # Natural functions parse all text and should return True if they are triggered.
        self.type = ["command"]

        # Specify the functions priority from 100 to 1
        self.priority = 50

        # Specify the functions triggerable commands. (Not needed for natural functions.)
        self.commands = []

        # Specify if the function requires auth status, can also be handled manually.
        self.restricted = False

        # Specify the functions function.
        self.functionString = "Function template."
        self.helpString = None


        # Specify a help string read by the help function.
        self.helpString = ""

        # Specify if the function blocks any other functions that come after itself and are triggerable with the same parameters. (Only used with natural and status functions)
        self.blocking = False

        # To be used internally by functions, may be reset to 0 for spam filters, etc. However it is recomended that you use your own variable in that case.
        self.runCount = 0


    def main(self, irc, msgData):
        irc.sendMSG("Function not setup, still using template.", config.masterChannel)
        return True


def prettyListString(list, joiner):
    result = ", ".join(list[:1])
    if len(list) > 1:
        result = result + joiner + list[-1]
    return result
