#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.command = "ping"
        self.functionString = "Ping the bot."

    def main(self, bot, msgData, funcType):
        bot._irc.sendMSG("pong", msgData["target"])
        return True