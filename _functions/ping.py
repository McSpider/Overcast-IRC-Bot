#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["ping"]
        self.functionString = "Ping the bot or other users."

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            argument = msgData["message"][1]
            bot._irc.sendMSG("%s: You are being requested by %s" % (argument, msgData["sender"]), msgData["target"])
        else:
            bot._irc.sendMSG("pong", msgData["target"])
        return True
