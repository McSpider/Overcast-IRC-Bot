#!/usr/bin/env python
from function_template import *
import datetime
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["lart"]
        self.functionString = "Lart users."
        self.helpString = "Credits to jcp/JZBot for the larts file."

        self.larts = loadMessagesFile("./_data/larts.txt")
        self.randomness = []

        self.cooldown = {}
        self.lartLimit = 3


    def main(self, bot, msgData, funcType):
        lart = None;
        cooldownID = msgData["sender"]

        if self.checkCooldownForID(cooldownID) == 0:
            while not lart:
              alart = random.choice(self.larts)
              if not alart in self.randomness:
                    lart = alart
                    self.randomness.append(alart)
                    if len(self.randomness) > int(len(self.larts)/2):
                        del self.randomness[0]

            if len(msgData["message"]) > 1:
                argument = msgData["message"][1]
                if argument == bot._irc.nick:
                    lart = lart.replace("!target!", msgData["sender"])
                else:
                    lart = lart.replace("!target!", argument)
                bot._irc.sendActionMSG(lart, msgData["target"])
            else:
                lart = lart.replace("!target!", msgData["sender"])
                bot._irc.sendActionMSG(lart, msgData["target"])
        elif self.checkCooldownForID(cooldownID) == self.lartLimit:
            bot._irc.sendMSG("Cooldown for lart function exceeded!", msgData["sender"])
        elif self.checkCooldownForID(cooldownID) == self.lartLimit + 2:
            bot._irc.sendMSG("Go away, %s." % msgData["sender"], msgData["target"])

        self.addCooldownForID(cooldownID)
        return True

    def checkCooldownForID(self, cooldownID):
        if not cooldownID in self.cooldown:
            return 0
        currentTime = datetime.datetime.now()
        timeout = currentTime > self.cooldown[cooldownID][0]
        if timeout:
            return 0
        if cooldownID in self.cooldown:
            if self.cooldown[cooldownID][1] >= self.lartLimit:
                return self.cooldown[cooldownID][1]
            return 0


    def addCooldownForID(self, cooldownID, cooldownTime = 2):
        currentTime = datetime.datetime.now()
        if cooldownID in self.cooldown:
            if currentTime > self.cooldown[cooldownID][0]:
                self.cooldown[cooldownID] = [currentTime + datetime.timedelta(minutes = cooldownTime),1]
            else:
                self.cooldown[cooldownID][1] = self.cooldown[cooldownID][1] + 1
        else:
            self.cooldown[cooldownID] = [currentTime + datetime.timedelta(minutes = cooldownTime),1]

