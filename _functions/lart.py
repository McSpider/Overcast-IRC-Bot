#!/usr/bin/env python
from function_template import *
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["lart"]
        self.functionString = "Lart users."
        self.helpString = "Credits to jcp/JZBot for the larts file."

        self.larts = loadMessagesFile("./_data/larts.txt")
        self.randomness = []

    def main(self, bot, msgData, funcType):
        lart = None;
        while not lart:
          alart = random.choice(self.larts)
          if not alart in self.randomness:
                lart = alart
                self.randomness.append(alart)
                if len(self.randomness) > int(len(self.larts)/2):
                    del self.randomness[0]

        if len(msgData["message"]) > 1:
            argument = msgData["message"][1]
            lart = lart.replace("!target!", argument)
            bot._irc.sendActionMSG(lart, msgData["target"])
        else:
            lart = lart.replace("!target!", msgData["sender"])
            bot._irc.sendActionMSG(lart, msgData["target"])
        return True
