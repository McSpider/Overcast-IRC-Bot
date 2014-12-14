#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["auth"]
        self.function_string = "Manage authed users."
        self.help_string = "Subcommands:\n&03{t}auth list &c- list all authed users.\n&03{t}auth add {hostmask matcher} &c- Add a user to the auth list.\n&03{t}auth remove {hostmask matcher} &c- Remove a user from the authlist."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) >= 2:
            if msg_data["message"][1] == "list":
                if len(bot.authed_hostmasks) == 0:
                    bot.irc.sendMSG("No users authed.", msg_data["sender"])
                    return True

                authentication_list = bot.authed_hostmasks

                page = 1
                page_size = 5
                all_pages = False
                pages = int(math.ceil(len(authentication_list) / float(page_size)))

                if len(msg_data["message"]) > 2 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][2]):
                    if msg_data["message"][2] == "-a":
                        page_size = len(authentication_list);
                        all_pages = True
                    else: page = int(msg_data["message"][2])

                if page > pages:
                    page = 1

                pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
                if all_pages or pages == 1: pages_info_string = "(&05%i&c)" % len(authentication_list)

                bot.irc.sendMSG("Authed Users: %s" % colorizer(pages_info_string), msg_data["sender"])
                for index, mask in enumerate(pageFromList(authentication_list,page,page_size)):
                    bot.irc.sendMSG("%s: %s" % (((page - 1) * page_size) + index, mask), msg_data["sender"])
            else:
                # Add new hostmask
                if msg_data["message"][1] == "add" and len(msg_data["message"]) >= 3:
                    new_mask = msg_data["message"][2]
                    if bot.addAuthedHostmask(new_mask):
                        bot.irc.sendMSG("Added hostmask (%s) to auth list" % new_mask, msg_data["target"])

                # Remove hostmask or list of hostmask indexes.
                if msg_data["message"][1] == "remove" and len(msg_data["message"]) >= 3:
                    arguments = msg_data["message"][2]
                    if arguments.startswith("[") and arguments.endswith("]"):
                        indexes = arguments.rstrip("]").lstrip("[").split(',')
                        masks_removed = []
                        for index in sorted(indexes, reverse = True):
                            if re.match("^[0-9]{1,3}$", index):
                                mask = bot.authed_hostmasks[int(index)]
                                if bot.removeAuthedHostmask(mask):
                                    masks_removed.append(mask)
                        
                        if len(masks_removed) > 0:
                            masks_removed = sorted(masks_removed, reverse = True)
                            bot.irc.sendMSG("Removed hostmask('s) (%s) from auth list" % prettyListString(masks_removed, " & "), msg_data["target"])
                    else:
                        if re.match("^[0-9]{1,3}$", arguments):
                            mask = bot.authed_hostmasks[int(arguments)]
                            if bot.removeAuthedHostmask(mask):
                                bot.irc.sendMSG("Removed hostmask (%s) from auth list" % mask, msg_data["target"])
                        else:
                            if bot.removeAuthedHostmask(arguments):
                                bot.irc.sendMSG("Removed hostmask (%s) from auth list" % arguments, msg_data["target"])

        else:
            help_str = self.help_string.replace("{t}", bot.short_trigger)
            help_str = colorizer(help_str)
            help_string_lines = string.split(help_str,"\n")
            for line in help_string_lines:
                bot.irc.sendMSG(line, msg_data["sender"])

        return True
