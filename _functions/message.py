#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["msg","me","notice"]
        self.function_string = "Send messages to users or channels."
        self.help_string = "Usage: {t}[msg|me|notice] <recipient> <message...>"
        self.restricted = True
        self.priority = 10

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 2:
            argument = msg_data["message"][1]
            msg = " ".join(msg_data["message"][2:])

            if (msg_data["message"][0] == "msg"):
                bot.irc.sendMSG(msg, argument)
            if (msg_data["message"][0] == "me"):
                bot.irc.sendActionMSG(msg, argument)
            if (msg_data["message"][0] == "notice"):
                bot.irc.sendNoticeMSG(msg, argument)
        return True
