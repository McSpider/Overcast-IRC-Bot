#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["channel", "chan"]
        self.function_string = "Manage connected channels."
        self.help_string = "Subcommands: join, part & list."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            if msg_data["message"][1] == "join":
                bot._irc._channels.join(msg_data["message"][2])
                bot._irc.sendMSG("Joining channel: %s" % msg_data["message"][2], msg_data["target"])
            if msg_data["message"][1] == "part":
                bot._irc._channels.part(msg_data["message"][2])
                bot._irc.sendMSG("Parting channel: %s" % msg_data["message"][2], msg_data["target"])
            if msg_data["message"][1] == "list":
                bot._irc.sendMSG("Connected channels:", msg_data["sender"])
                for chan, data in bot._irc._channels.list.items():
                    chan_flags = prettyListString(data.my_flags, " & ")
                    bot._irc.sendMSG("%s: %s - %s" % (chan, chan_flags if chan_flags else "No flags set", ("Connected" if data.connected else "Not connected")), msg_data["target"])
        else:
            bot._irc.sendMSG("Subcommands: join, part & list.", msg_data["target"])

        return False
