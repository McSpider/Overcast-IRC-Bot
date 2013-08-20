#!/usr/bin/env python
from function_template import *
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.functionString = "I'm alive! (Well as alive as I'll ever be...)"
        self.blocking = True

        self.greetings = ["Hello","Hi","Heyo"]

        self.cooldown = {}

    def main(self, bot, msgData, funcType):
        message = string.join(msgData["message"])
        currentTime = datetime.datetime.now()
        cooldownID = msgData["sender"] + message

        if re.match("^(hi|hello|hey),? %s.*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE) or re.match("^%s[,:]? (hi|hello)$" % re.escape(bot._irc.nick), message, re.IGNORECASE):
            if self.checkCooldownForID(cooldownID,1):
                bot._irc.sendMSG("%s %s" % (random.choice(self.greetings), msgData["sender"]), msgData["target"])
                self.addCooldownForID(cooldownID,1)
                return True
        if re.match("^.*?how (do you do|are you) %s?" % re.escape(bot._irc.nick), message, re.IGNORECASE):
            if self.checkCooldownForID(cooldownID,1):
                bot._irc.sendMSG("I'm good, thanks.", msgData["target"])
                self.addCooldownForID(cooldownID,1)
                return True
        if re.match("^\>_\<$", message):
            if self.checkCooldownForID(cooldownID,2):
                bot._irc.sendMSG("Ouch!", msgData["target"])
                self.addCooldownForID(cooldownID,2)
                return True
        if re.match("^Ew{3,7}!$", message):
            if self.checkCooldownForID(cooldownID,3):
                bot._irc.sendMSG("...", msgData["target"])
                self.addCooldownForID(cooldownID,3,3600)
                return True
        match = re.match("^WTF[^!]*?(!+)$", message)
        if match:
            if self.checkCooldownForID(cooldownID,3):
                count = len(match.group(1))
                expression = None
                if count > 3: expression = 'Large WTF!'
                if count > 5: expression = 'Huge WTF!'
                if count > 7: expression = 'Giga WTF!'
                if expression:
                    bot._irc.sendMSG(expression, msgData["target"])
                    self.addCooldownForID(cooldownID,3,300)
                    return True

        return False

    def checkCooldownForID(self, cooldownID, messageTypeID):
        currentTime = datetime.datetime.now()
        cooldownID = cooldownID + str(messageTypeID)
        return (cooldownID in self.cooldown and ((self.cooldown[cooldownID] == None) or (currentTime > self.cooldown[cooldownID]))) or not cooldownID in self.cooldown

    def addCooldownForID(self, cooldownID, messageTypeID, cooldownTime = 60):
        currentTime = datetime.datetime.now()
        cooldownID = cooldownID + str(messageTypeID)
        self.cooldown[cooldownID] = currentTime + datetime.timedelta(seconds = cooldownTime)
