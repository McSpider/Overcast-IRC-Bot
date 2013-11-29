#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["function", "func"]
        self.functionString = "Manage functions."
        self.helpString = "Subcommands: disable, enable & list."
        self.restricted = True

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            if msgData["message"][1] == "disable" and len(msgData["message"]) > 2:
                timedelta = datetime.timedelta(minutes = 5)
                disabled_by = msgData["sender"]
                if len(msgData["message"]) > 3:
                    newDelta = parseTimeDelta(msgData["message"][3])
                    if newDelta:
                        timedelta = newDelta
                    else:
                        bot._irc.sendMSG("Invalid time delta: %s" % msgData["message"][3], msgData["target"])
                        return

                if bot._functions.disableFunction(msgData["message"][2], timedelta, disabled_by):
                    bot._irc.sendMSG("Disabled function: %s timedelta: %s" % (msgData["message"][2], str(timedelta)), msgData["target"])
                else:
                    bot._irc.sendMSG("Invalid function name: %s" % msgData["message"][2], msgData["target"])

            if msgData["message"][1] == "enable":
                if bot._functions.enableFunction(msgData["message"][2]):
                    bot._irc.sendMSG("Enabled function: %s" % msgData["message"][2], msgData["target"])
                else:
                    bot._irc.sendMSG("Invalid function name: %s" % msgData["message"][2], msgData["target"])

            if msgData["message"][1] == "list":
                bot._irc.sendMSG("Functions:", msgData["sender"])
                for function in bot._functions.functions_list:
                    bot._irc.sendMSG("%s%s" % (function.name, (" Disabled" if function.disabled else "")) , msgData["sender"])
        else:
            bot._irc.sendMSG(self.helpString, msgData["sender"])


        return False
