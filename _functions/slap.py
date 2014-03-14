#!/usr/bin/env python
from function_template import *
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural","command"]
        self.commands = ["slap"] 
        self.priority = 100
        self.function_string = "Slap a person."
        self.blocking = True

    def load(self, bot):
        function_template.load(self, bot)
        self.slaps = self.loadMessagesFile("slaps.txt")
        self.ouch = ["Ouch!","That hurt!","Oww!","Will you stop that!",">_>"]
        self.randomness = []


    def main(self, bot, msg_data, func_type):
        if (func_type == "natural"):
            message = string.join(msg_data["message"])

            if re.match("^.*?(slaps|whacks) %s.*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE) or re.match("^.*?gives.*?%s a.*?(slap|whack).*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE):
                bot._irc.sendMSG(random.choice(self.ouch), msg_data["target"])
                return True
            return False

        if (func_type == "command"):
            slap = None;
            while not slap:
              aslap = random.choice(self.slaps)
              if not aslap in self.randomness:
                    slap = aslap
                    self.randomness.append(aslap)
                    if len(self.randomness) > int(len(self.slaps)/2):
                        del self.randomness[0]

            if len(msg_data["message"]) > 1:
                argument = msg_data["message"][1]
                if re.match("^(%s|himself|itself)$" % (bot._irc.nick), argument, re.IGNORECASE):
                    slap = slap.replace("!target!", msg_data["sender"])
                else:
                    slap = slap.replace("!target!", argument)
                bot._irc.sendActionMSG(slap, msg_data["target"])
            else:
                slap = slap.replace("!target!", msg_data["sender"])
                bot._irc.sendActionMSG(slap, msg_data["target"])
            return True

