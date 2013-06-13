#!/usr/bin/env python
from function_template import *
import datetime  


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "face"
        self.type = ["natural"]
        self.priority = 100
        self.functionString = ">_< face."
        self.blocking = True

        self.cooldown = None

    def main(self, irc, msgData, funcType):
        message = string.join(msgData["message"])
        if re.match("^\>_\<$", message):
            currentTime = datetime.datetime.now()
            if (self.cooldown == None) or (currentTime > self.cooldown):
                irc.sendMSG("Ouch!", msgData["recipient"])
                self.cooldown = currentTime + datetime.timedelta(minutes = 5)
                return True

        return False