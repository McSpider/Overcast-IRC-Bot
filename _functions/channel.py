#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["channel", "chan"]
        self.function_string = "Manage connected channels."
        self.help_string = "Subcommands: join, part, ignore & list."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            if len(msg_data["message"]) > 2:
                channel = msg_data["message"][2]

                if msg_data["message"][1] == "join":
                    bot._irc._channels.join(channel)
                    bot._irc.sendMSG("Joining channel: %s" % channel, msg_data["target"])
                if msg_data["message"][1] == "part":
                    bot._irc._channels.part(channel)
                    bot._irc.sendMSG("Parting channel: %s" % channel, msg_data["target"])
                
                if msg_data["message"][1] == "ignore":
                    if not bot._irc._channels.isIgnoring(channel):
                        bot._irc._channels.ignore(channel, True)
                        bot._irc.sendMSG("Ignoring chat from channel: %s" % channel, msg_data["target"])
                    else:
                        bot._irc._channels.ignore(channel, False)
                        bot._irc.sendMSG("Handling chat from channel: %s" % channel, msg_data["target"])

            if msg_data["message"][1] == "list":
                bot._irc.sendMSG("Connected channels:", msg_data["sender"])
                for chan, data in bot._irc._channels.list.items():
                    chan_flags = prettyListString(data.my_flags, " & ")
                    bot._irc.sendMSG("%s: %s - %s %s" % (chan, chan_flags if chan_flags else "No flags set", ("Connected" if data.connected else "Not connected"), ("Ignored" if data.ignored else "Handling")), msg_data["sender"])
        else:
            bot._irc.sendMSG("Subcommands: join, part, ignore & list.", msg_data["target"])

        return False
