#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "help"
        self.command = "help"
        self.functionString = "Overcast bot help."
        self.blocking = True
        self.priority = 2

    def main(self, irc, msgData, funcType):
        if len(msgData["message"]) > 2:
            subcommand = msgData["message"][2]
            for func in irc._functions.functionsList:
                if func.name == subcommand:
                    irc.sendMSG("Info for function: %s" % (subcommand), msgData["recipient"])
                    irc.sendMSG("%s(%s) - \"%s\"  " % (func.name, int(func.restricted), func.functionString), msgData["recipient"])
                    return True
        else:
            irc.sendMSG("Trigger the bot with: \"%s\"" % ", ".join(config.triggers), msgData["recipient"])
            
            # List all the unrestricted functions
            functionMsg = []
            for func in irc._functions.functionsList:
                if func.restricted == True and irc.isUserAuthed(msgData["sender"],msgData["senderHostmask"]):
                    continue
                functionMsg.append(func.name)
            print functionMsg
            if len(functionMsg) > 0:
                irc.sendMSG("Functions you can trigger:", msgData["recipient"])
                irc.sendMSG(", ".join(functionMsg), msgData["recipient"])
                irc.sendMSG("For more info about a specific function use: help {function name}", msgData["recipient"])

        return True