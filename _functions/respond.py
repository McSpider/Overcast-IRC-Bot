#!/usr/bin/env python
from function_template import *
import datetime  


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.functionString = "I'm alive!"
        self.blocking = True

        self.cooldown = {}

    def main(self, bot, msgData, funcType):
        message = string.join(msgData["message"])
        currentTime = datetime.datetime.now()
        cooldownID = msgData["sender"] + message
        print cooldownID

        if re.match("^(hi|hello) %s.*?$" % config.nick, message, re.IGNORECASE) or re.match("^%s: (hi|hello)$" % config.nick, message, re.IGNORECASE):
            if self.checkCooldownForID(cooldownID):
                bot._irc.sendMSG("Hello %s" % msgData["sender"], msgData["target"])
                self.cooldown[cooldownID] = currentTime + datetime.timedelta(seconds = 30)
                return True
        if re.match("^.*?how (do you do|are you) %s?" % config.nick, message, re.IGNORECASE):
            if self.checkCooldownForID(cooldownID):
                bot._irc.sendMSG("I'm good, thanks.", msgData["target"])
                self.cooldown[cooldownID] = currentTime + datetime.timedelta(seconds = 30)
                return True

        return False

    def checkCooldownForID(self, cooldownID):
        return (cooldownID in self.cooldown and ((self.cooldown[cooldownID] == None) or (currentTime > self.cooldown[cooldownID]))) or not cooldownID in self.cooldown