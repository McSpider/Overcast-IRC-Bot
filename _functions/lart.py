#!/usr/bin/env python
from function_template import *
import datetime
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["lart"]
        self.function_string = "Lart users."
        self.help_string = "Credits to jcp/JZBot for the larts file."

        self.larts = loadMessagesFile("./_data/larts.txt")
        self.randomness = []

        self.cooldown = {}
        self.lart_limit = 3


    def main(self, bot, msg_data, func_type):
        lart = None;
        cooldown_id = msg_data["sender"]

        if self.checkCooldownForID(cooldown_id) == 0:
            while not lart:
              alart = random.choice(self.larts)
              if not alart in self.randomness:
                    lart = alart
                    self.randomness.append(alart)
                    if len(self.randomness) > int(len(self.larts)/2):
                        del self.randomness[0]

            if len(msg_data["message"]) > 1:
                argument = msg_data["message"][1]
                if re.match("^(%s|himself|itself)$" % (bot._irc.nick), argument, re.IGNORECASE):
                    lart = lart.replace("!target!", msg_data["sender"])
                else:
                    lart = lart.replace("!target!", argument)
                bot._irc.sendActionMSG(lart, msg_data["target"])
            else:
                lart = lart.replace("!target!", msg_data["sender"])
                bot._irc.sendActionMSG(lart, msg_data["target"])
        elif self.checkCooldownForID(cooldown_id) == self.lart_limit:
            bot._irc.sendMSG("Cooldown for lart function exceeded!", msg_data["sender"])
        elif self.checkCooldownForID(cooldown_id) == self.lart_limit + 2:
            bot._irc.sendMSG("Go away, %s." % msg_data["sender"], msg_data["target"])
        elif self.checkCooldownForID(cooldown_id) == self.lart_limit + 5:
            # Abuse of lart command
            hostmask = string.lstrip(msg_data["senderHostmask"],":")
            bot.addBlacklistedHostmask(hostmask)
            bot._irc.sendMSG("Auto blacklisting hostmask: %s" % hostmask, bot.master_channel)

        self.addCooldownForID(cooldown_id)
        return True

    def checkCooldownForID(self, cooldown_id):
        if not cooldown_id in self.cooldown:
            return 0
        current_time = datetime.datetime.now()
        timeout = current_time > self.cooldown[cooldown_id][0]
        if timeout:
            return 0
        if cooldown_id in self.cooldown:
            if self.cooldown[cooldown_id][1] >= self.lart_limit:
                return self.cooldown[cooldown_id][1]
            return 0


    def addCooldownForID(self, cooldown_id, cooldown_time = 2):
        current_time = datetime.datetime.now()
        if cooldown_id in self.cooldown:
            if current_time > self.cooldown[cooldown_id][0]:
                self.cooldown[cooldown_id] = [current_time + datetime.timedelta(minutes = cooldown_time),1]
            else:
                self.cooldown[cooldown_id][1] = self.cooldown[cooldown_id][1] + 1
        else:
            self.cooldown[cooldown_id] = [current_time + datetime.timedelta(minutes = cooldown_time),1]

