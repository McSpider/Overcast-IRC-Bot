#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "ping"
        self.command = "ping"
        self.functionString = "Ping the bot."

    def main(self, irc, msgData, funcType):
        irc.sendMSG("pong", msgData["recipient"])
        return True