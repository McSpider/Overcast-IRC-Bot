#!/usr/bin/env python
import sys
from time import sleep

from irc import *
import config

class bot:
    def __init__(self):
        self.irc = irc()

    def main(self):
        print color.b_cyan + "Overcast IRC Bot - Hi! \n" + color.clear
        self.irc.connectToServer(config.host,config.port)
        self.irc.authUser(config.ident,config.nick,config.realname,config.password)

        self.irc.read()
        self.irc.disconnect()
        print color.b_cyan + "\nOvercast IRC Bot - Shutdown, have a nice day. " + color.clear


# Start the bot
try:
    bot = bot()
    bot.main()
except KeyboardInterrupt:
    pass

