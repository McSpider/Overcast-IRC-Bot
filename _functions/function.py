#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["function", "func"]
        self.function_string = "Manage functions."
        self.help_string = "Subcommands: disable, enable & list."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            if msg_data["message"][1] == "disable" and len(msg_data["message"]) > 2:
                timedelta = datetime.timedelta(minutes = 5)
                disabled_by = msg_data["sender"]
                if len(msg_data["message"]) > 3:
                    new_delta = parseTimeDelta(msg_data["message"][3])
                    if new_delta:
                        timedelta = new_delta
                    else:
                        bot._irc.sendMSG("Invalid time delta: %s" % msg_data["message"][3], msg_data["target"])
                        return

                if bot._functions.disableFunction(msg_data["message"][2], timedelta, disabled_by):
                    bot._irc.sendMSG("Disabled function: %s - For: %s" % (msg_data["message"][2], str(timedelta)), msg_data["target"])
                else:
                    bot._irc.sendMSG("Invalid function name: %s" % msg_data["message"][2], msg_data["target"])

            if msg_data["message"][1] == "enable":
                if bot._functions.enableFunction(msg_data["message"][2]):
                    bot._irc.sendMSG("Enabled function: %s" % msg_data["message"][2], msg_data["target"])
                else:
                    bot._irc.sendMSG("Invalid function name: %s" % msg_data["message"][2], msg_data["target"])

            if msg_data["message"][1] == "list":
                bot._irc.sendMSG("Functions:", msg_data["sender"])
                for function in bot._functions.functions_list:
                    bot._irc.sendMSG("%s%s" % (function.name, (" Disabled" if function.disabled else "")) , msg_data["sender"])
        else:
            bot._irc.sendMSG(self.help_string, msg_data["sender"])


        return False
