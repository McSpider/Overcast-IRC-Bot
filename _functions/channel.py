#!/usr/bin/env python
from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["channel", "chan", "leave"]
        self.function_string = "Manage connected channels."
        self.help_string = "Subcommands:\n&03{t}channel join {channel} &c- Join the specified channel.\n&03{t}channel part {channel} &c- Leave the specified channel.\n&03{t}channel ignore {channel} &c- Ignore messages from the specified channel.\n&03{t}channel list {channel} &c- List all managed channels.\n&02{t}leave &c- quick command, leaves the current channel."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        command = msg_data["message"][0]
        if command == "channel" or command == "chan":
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

                    channels_list = []
                    for chan, data in bot._irc._channels.list.items():
                        chan_flags = prettyListString(data.my_flags, " & ")
                        channels_list.append("&10%s&c: %s - %s %s" % (chan, chan_flags if chan_flags else "No flags set", ("Connected" if data.connected else "Not connected"), ("Ignored" if data.ignored else "Handling")))

                    if len(channels_list) > 0:
                        page = 1
                        page_size = 5
                        all_pages = False
                        pages = int(math.ceil(len(channels_list) / float(page_size)))

                        if len(msg_data["message"]) > 1 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][1]):
                            if msg_data["message"][1] == "-a":
                                page_size = len(channels_list);
                                all_pages = True
                            else: page = int(msg_data["message"][1])

                        if page > pages:
                            page = 1

                        pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
                        if all_pages or page == pages: pages_info_string = "(&05%i&c)" % pages

                        bot._irc.sendMSG("Channels: %s" % colorizer(pages_info_string), msg_data["sender"])
                        for chan in pageFromList(channels_list,page,page_size):
                            bot._irc.sendMSG("%s" % colorizer(chan), msg_data["sender"])
                    else:
                        bot._irc.sendMSG("No channels to list.", msg_data["sender"])

            else:
                bot._irc.sendMSG("Subcommands: join, part, ignore & list.", msg_data["target"])
        
        if command == "leave":
            if not msg_data["message_type"] == "QUERY_MSG" or msg_data["message_type"] == "ACTION_MSG":
                bot._irc.sendMSG("Bye!", msg_data["target"])
                bot._irc._channels.part(msg_data["target"])
            else:
                bot._irc.sendMSG("This is not an IRC channel.", msg_data["target"])


        return True
