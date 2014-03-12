#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["blacklist"]
        self.function_string = "Manage blacklisted users."
        self.help_string = "Subcommands: add & remove."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 2:
            new_mask = msg_data["message"][2]
            if msg_data["message"][1] == "add":
                if bot.addBlacklistedHostmask(new_mask):
                    bot._irc.sendMSG("Added hostmask (%s) to blacklist" % new_mask, msg_data["target"])
            if msg_data["message"][1] == "remove":
                if bot.removeBlacklistedHostmask(msg_data["message"][2]):
                    bot._irc.sendMSG("Removed hostmask (%s) from blacklist" % new_mask, msg_data["target"])

        else:
            if len(bot.blacklisted_users) == 0:
                bot._irc.sendMSG("No users blacklisted.", msg_data["sender"])
                return
            bot._irc.sendMSG("Blacklisted Users:", msg_data["sender"])
            for mask in bot.blacklisted_users:
                bot._irc.sendMSG("%s" % mask, msg_data["sender"])

        return False
