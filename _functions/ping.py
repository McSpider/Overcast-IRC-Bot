#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["ping"]
        self.function_string = "Ask the bot for a ping reply."

    def main(self, bot, msg_data, func_type):
        if msg_data["sender"] == msg_data["target"]:
            bot.irc.sendMSG("pong", msg_data["target"])
        else:
            bot.irc.sendMSG("%s: pong" % (msg_data["sender"]), msg_data["target"])
        return True
