#!/usr/bin/env python
from function_template import *
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural","command"]
        self.commands = ["slap"] 
        self.priority = 100
        self.functionString = "Slap a person."
        self.blocking = True

        self.slaps = loadMessagesFile("./_data/slaps.txt")
        self.ouch = ["Ouch!","That hurt!","Oww!","Will you stop that!",">_>"]
        self.randomness = []

    def main(self, bot, msgData, funcType):
        if (funcType == "natural"):
            message = string.join(msgData["message"])

            if re.match("^.*?(slaps|whacks) %s.*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE) or re.match("^.*?gives.*?%s a.*?(slap|whack).*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE):
                bot._irc.sendMSG(random.choice(self.ouch), msgData["target"])
                return True
            return False

        if (funcType == "command"):
            slap = None;
            while not slap:
              aslap = random.choice(self.slaps)
              if not aslap in self.randomness:
                    slap = aslap
                    self.randomness.append(aslap)
                    if len(self.randomness) > int(len(self.slaps)/2):
                        del self.randomness[0]

            if len(msgData["message"]) > 1:
                argument = msgData["message"][1]
                if re.match("^(%s|himself|itself)$" % (bot._irc.nick), argument, re.IGNORECASE):
                    slap = slap.replace("!target!", msgData["sender"])
                else:
                    slap = slap.replace("!target!", argument)
                bot._irc.sendActionMSG(slap, msgData["target"])
            else:
                slap = slap.replace("!target!", msgData["sender"])
                bot._irc.sendActionMSG(slap, msgData["target"])
            return True

