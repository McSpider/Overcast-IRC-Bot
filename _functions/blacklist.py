#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["blacklist"]
        self.functionString = "Manage blacklisted users."
        self.helpString = "Subcommands: add & remove."
        self.restricted = True

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            if msgData["message"][1] == "add":
                if bot.addBlacklistedHostmask(msgData["message"][2]):
                    bot._irc.sendMSG("Added hostmask (%s) to blacklist" % msgData["message"][2], msgData["target"])

            if msgData["message"][1] == "remove":
                if bot.removeBlacklistedHostmask(msgData["message"][2]):
                    bot._irc.sendMSG("Removed hostmask (%s) from blacklist" % msgData["message"][2], msgData["target"])
        else:
            if len(bot.blacklistedUsers) == 0:
                bot._irc.sendMSG("No users blacklisted.", msgData["sender"])
                return
            bot._irc.sendMSG("Blacklisted Users:", msgData["sender"])
            for mask in bot.blacklistedUsers:
                bot._irc.sendMSG("%s" % mask, msgData["sender"])

        return False
