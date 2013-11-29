#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["help"]
        self.function_string = "Overcast bot help."
        self.blocking = True
        self.priority = 3

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            subcommand = msg_data["message"][1]
            for func in bot._functions.functions_list:
                if re.match("^%s.*?$" % re.escape(subcommand), func.name, re.IGNORECASE):
                    bot._irc.sendMSG("Info for function: %s%s%s" % (color.irc_blue, func.name, color.irc_clear), msg_data["sender"])
                    bot._irc.sendMSG("%s" % func.function_string, msg_data["sender"])
                    bot._irc.sendMSG("Restricted: %s - Type: %s" % (bool(func.restricted), prettyListString(func.type," & ")), msg_data["sender"])
                    if "command" in func.type:
                        bot._irc.sendMSG("Commands: %s" % (prettyListString(func.commands," & ")), msg_data["sender"])
                    if not func.help_string == None:
                        bot._irc.sendMSG(func.help_string, msg_data["sender"])
                    return True
        else:
            bot._irc.sendMSG("Trigger the bot with: \"%s\" Short trigger: \"%s%s%s\"" % (prettyListString(bot.triggers," or ",color.irc_green), color.irc_green, bot.shortTrigger, color.irc_clear), msg_data["sender"])

            function_msg = []
            for func in bot._functions.functions_list:
                func_type = ""
                for fType in func.type:
                    if fType == "command":
                        func_type = "C" + func_type
                    if fType == "natural":
                        func_type = "N" + func_type
                    if fType == "status":
                        func_type = "S" + func_type
                func_type = func_type + "."
                if func.hidden == True:
                    continue
                if func.restricted == True and bot.isUserAuthed(msg_data["sender"],msg_data["sender_hostmask"]):
                    continue
                function_msg.append(color.irc_white + func_type + color.irc_clear + func.name)
            if len(function_msg) > 0:
                bot._irc.sendMSG("Functions you can trigger:", msg_data["sender"])
                bot._irc.sendMSG(", ".join(function_msg), msg_data["sender"])
                bot._irc.sendMSG("For more info about a specific function use: help {function name}", msg_data["sender"])
                return True

        return False
