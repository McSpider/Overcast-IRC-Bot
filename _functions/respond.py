#!/usr/bin/env python
from function_template import *
import datetime  


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "respond"
        self.type = ["natural"]
        self.priority = 100
        self.functionString = "I'm alive!"
        self.blocking = True

        self.cooldown = None

    def main(self, irc, msgData, funcType):
        message = string.join(msgData["message"])
        if re.match("^hi$", message) or re.match("^hello$", message):
            currentTime = datetime.datetime.now()
            if (self.cooldown == None) or (currentTime > self.cooldown):
                irc.sendMSG("hi!", msgData["recipient"])
                self.cooldown = currentTime + datetime.timedelta(seconds = 30)
                return True

        return False