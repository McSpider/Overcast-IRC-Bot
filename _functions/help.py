#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["help"]
        self.functionString = "Overcast bot help."
        self.blocking = True
        self.priority = 2

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            subcommand = msgData["message"][1]
            for func in bot._functions.functionsList:
                if re.match("^%s.*?$" % subcommand, func.name, re.IGNORECASE):
                    bot._irc.sendMSG("Info for function: %s" % (func.name), msgData["target"])
                    bot._irc.sendMSG("%s" % func.functionString, msgData["target"])
                    bot._irc.sendMSG("Restricted:%s Type:%s" % (bool(func.restricted), ', '.join(func.type)), msgData["target"])
                    if (func.helpString != None):
                        bot._irc.sendMSG(func.helpString, msgData["target"])
                    return True
        else:
            bot._irc.sendMSG("Trigger the bot with: \"%s\"" % ", ".join(config.triggers), msgData["target"])
            
            # List all the unrestricted functions
            functionMsg = []
            for func in bot._functions.functionsList:
                funcType = ""
                for fType in func.type:
                    if fType == "command":
                        funcType = "C" + funcType
                    if fType == "natural":
                        funcType = "N" + funcType
                    if fType == "status":
                        funcType = "S" + funcType
                funcType = funcType + "."
                if func.restricted == True and bot.isUserAuthed(msgData["sender"],msgData["senderHostmask"]):
                    continue
                functionMsg.append(funcType + func.name)
            if len(functionMsg) > 0:
                bot._irc.sendMSG("Functions you can trigger:", msgData["target"])
                bot._irc.sendMSG(", ".join(functionMsg), msgData["target"])
                bot._irc.sendMSG("For more info about a specific function use: help {function name}", msgData["target"])

        return True