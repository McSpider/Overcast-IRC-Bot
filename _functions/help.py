#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["help"]
        self.functionString = "Overcast bot help."
        self.blocking = True
        self.priority = 3

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            subcommand = msgData["message"][1]
            for func in bot._functions.functionsList:
                if re.match("^%s.*?$" % re.escape(subcommand), func.name, re.IGNORECASE):
                    bot._irc.sendMSG("Info for function: %s%s%s" % (color.irc_blue, func.name, color.irc_clear), msgData["sender"])
                    bot._irc.sendMSG("%s" % func.functionString, msgData["sender"])
                    bot._irc.sendMSG("Restricted: %s - Type: %s" % (bool(func.restricted), prettyListString(func.type," & ")), msgData["sender"])
                    if "command" in func.type:
                        bot._irc.sendMSG("Commands: %s" % (prettyListString(func.commands," & ")), msgData["sender"])
                    if not func.helpString == None:
                        bot._irc.sendMSG(func.helpString, msgData["sender"])
                    return True
        else:
            bot._irc.sendMSG("Trigger the bot with: \"%s\" Short trigger: \"%s%s%s\"" % (prettyListString(bot.triggers," or ",color.irc_darkgreen), color.irc_darkgreen, bot.shortTrigger, color.irc_clear), msgData["sender"])

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
                functionMsg.append(color.irc_lightgrey + funcType + color.irc_clear + func.name)
            if len(functionMsg) > 0:
                bot._irc.sendMSG("Functions you can trigger:", msgData["sender"])
                bot._irc.sendMSG(", ".join(functionMsg), msgData["sender"])
                bot._irc.sendMSG("For more info about a specific function use: help {function name}", msgData["sender"])
                return True

        return False
