#!/usr/bin/env python
from function_template import *
import random


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.function_string = "I'm alive! (Well as alive as I'll ever be...)"
        self.blocking = True

        self.greetings = ["Hello","Hi","Heyo"]

        self.cooldown = {}

    def main(self, bot, msg_data, func_type):
        message = string.join(msg_data["message"])
        current_time = datetime.datetime.now()
        cooldown_id = msg_data["sender"] + message

        if re.match("^(hi|hello|hey),? %s.*?$" % re.escape(bot._irc.nick), message, re.IGNORECASE) or re.match("^%s[,:]? (hi|hello)$" % re.escape(bot._irc.nick), message, re.IGNORECASE):
            if self.checkCooldownForID(cooldown_id,1):
                bot._irc.sendMSG("%s %s" % (random.choice(self.greetings), msg_data["sender"]), msg_data["target"])
                self.addCooldownForID(cooldown_id,1)
                return True
        if re.match("^.*?how (do you do|are you) %s?" % re.escape(bot._irc.nick), message, re.IGNORECASE):
            if self.checkCooldownForID(cooldown_id,1):
                bot._irc.sendMSG("I'm good, thanks.", msg_data["target"])
                self.addCooldownForID(cooldown_id,1)
                return True
        if re.match("^\>_\<$", message):
            if self.checkCooldownForID(cooldown_id,2):
                bot._irc.sendMSG("Ouch!", msg_data["target"])
                self.addCooldownForID(cooldown_id,2)
                return True
        if re.match("^Ew{3,7}!$", message):
            if self.checkCooldownForID(cooldown_id,3):
                bot._irc.sendMSG("...", msg_data["target"])
                self.addCooldownForID(cooldown_id,3,3600)
                return True
        if re.match("((.*%s .* bot.*)|(.*bot .* %s.*))" % (re.escape(bot._irc.nick), re.escape(bot._irc.nick)), message):
            if self.checkCooldownForID(cooldown_id,4):
                bot._irc.sendMSG("You talking about me?", msg_data["target"])
                self.addCooldownForID(cooldown_id,4,28800)
                return True
        match = re.match("^WTF[^!]*?(!+)$", message)
        if match:
            if self.checkCooldownForID(cooldown_id,3):
                count = len(match.group(1))
                expression = None
                if count > 3: expression = 'Large WTF!'
                if count > 5: expression = 'Huge WTF!'
                if count > 7: expression = 'Giga WTF!'
                if expression:
                    bot._irc.sendMSG(expression, msg_data["target"])
                    self.addCooldownForID(cooldown_id,3,300)
                    return True

        return False

    def checkCooldownForID(self, cooldown_id, message_type_id):
        current_time = datetime.datetime.now()
        cooldown_id = cooldown_id + str(message_type_id)
        return (cooldown_id in self.cooldown and ((self.cooldown[cooldown_id] == None) or (current_time > self.cooldown[cooldown_id]))) or not cooldown_id in self.cooldown

    def addCooldownForID(self, cooldown_id, message_type_id, cooldown_time = 60):
        current_time = datetime.datetime.now()
        cooldown_id = cooldown_id + str(message_type_id)
        self.cooldown[cooldown_id] = current_time + datetime.timedelta(seconds = cooldown_time)
