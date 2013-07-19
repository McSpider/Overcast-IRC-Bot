
#!/usr/bin/env python
import re
import string

import urllib
from bs4 import BeautifulSoup
from utils import *

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

        # Specify if the function blocks any other functions that come after itself and are triggerable with the same parameters. (Only used with natural and status functions)
        self.blocking = True

        # To be used internally by functions, may be reset to 0 for spam filters, etc. However it is recomended that you use your own variable in that case.
        self.runCount = 0


    def main(self, bot, msgData, funcType):
        irc.sendMSG("Function not setup, still using template.", bot.masterChannel)
        return True


def prettyListString(alist, joiner, cc = None):
    if not cc == None:
        alist = [cc + item + color.irc_clear for item in alist]

    if len(alist) > 1:
        result = ", ".join(alist[:-1])
        if len(alist) > 1:
            result = result + joiner + alist[-1]
        return result
    elif len(alist) == 1: return alist[0]

def loadMessagesFile(file):
    lines1 = open(file).read().splitlines()
    lines2 = [line for line in lines1 if not line.startswith('#')]
    lines3 = [line for line in lines2 if line]

    return lines3

def colorizer(message):
    message = message.replace("&10", color.irc_cyan)
    message = message.replace("&11", color.irc_lightcyan)
    message = message.replace("&12", color.irc_blue)
    message = message.replace("&13", color.irc_violet)
    message = message.replace("&14", color.irc_darkgrey)
    message = message.replace("&15", color.irc_lightgrey)

    message = message.replace("&00", color.irc_white)
    message = message.replace("&01", color.irc_black)
    message = message.replace("&02", color.irc_darkblue)
    message = message.replace("&03", color.irc_darkgreen)
    message = message.replace("&04", color.irc_red)
    message = message.replace("&05", color.irc_darkred)
    message = message.replace("&06", color.irc_darkviolet)
    message = message.replace("&07", color.irc_orange)
    message = message.replace("&08", color.irc_yellow)
    message = message.replace("&09", color.irc_lightgreen)

    message = message.replace("&b", color.irc_bold)
    message = message.replace("&i", color.irc_italic)
    message = message.replace("&u", color.irc_underline)
    message = message.replace("&c", color.irc_clear)
    return message


