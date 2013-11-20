#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["channel", "chan"]
        self.functionString = "Manage connected channels."
        self.helpString = "Subcommands: join, part & list."
        self.restricted = True

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            if msgData["message"][1] == "join":
                bot._irc._channels.join(msgData["message"][2])
                bot._irc.sendMSG("Joining channel: %s" % msgData["message"][2], msgData["target"])
            if msgData["message"][1] == "part":
                bot._irc._channels.part(msgData["message"][2])
                bot._irc.sendMSG("Parting channel: %s" % msgData["message"][2], msgData["target"])
            if msgData["message"][1] == "list":
                bot._irc.sendMSG("Connected channels:", msgData["sender"])
                for chan, data in bot._irc._channels.list.items():
                    chan_flags = prettyListString(data.my_flags, " & ")
                    bot._irc.sendMSG("%s: %s - %s" % (chan, chan_flags if chan_flags else "No flags set", ("Connected" if data.connected else "Not connected")), msgData["target"])
        else:
            bot._irc.sendMSG("Subcommands: join, part & list.", msgData["target"])

        return False
