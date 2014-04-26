#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["ask"]
        self.function_string = "Prompt a person to ask the freaking question already."

    def load(self, bot):
        function_template.load(self, bot)
        # From +Brottweiler in #overcastnetwork
        self.ask_message = "If you have a question, please just ask it. Don't look for staff or topic experts. Don't ask to ask or ask if people are awake or available. Just ask the question to the channel straight out, and wait patiently for a reply."

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            argument = msg_data["message"][1]
            bot.irc.sendMSG("%s: %s" % (argument, self.ask_message), msg_data["target"])
        else:
            bot.irc.sendMSG(self.ask_message, msg_data["target"])
        return True
