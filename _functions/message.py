#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["msg","me","notice"]
        self.function_string = "Send custom messages to joined channels."
        self.restricted = True
        self.priority = 10

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 2:
            argument = msg_data["message"][1]
            msg = " ".join(msg_data["message"][2:])
            if not bot._irc._channels.isConnectedTo(argument):
                argument = msg_data["target"]

            if (msg_data["message"][0] == "msg"):
                bot._irc.sendMSG(msg, argument)
            if (msg_data["message"][0] == "me"):
                bot._irc.sendActionMSG(msg, argument)
            if (msg_data["message"][0] == "notice"):
                bot._irc.sendNoticeMSG(msg, argument)
            return True
        return False
