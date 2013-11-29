#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["ping"]
        self.function_string = "Ping the bot or other users."

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            argument = msg_data["message"][1]
            bot._irc.sendMSG("%s: You are being requested by %s" % (argument, msg_data["sender"]), msg_data["target"])
        else:
            bot._irc.sendMSG("pong", msg_data["target"])
        return True
