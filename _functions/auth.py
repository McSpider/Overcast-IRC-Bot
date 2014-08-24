#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["auth"]
        self.function_string = "Manage authed users."
        self.help_string = "Subcommands:\n&03{t}auth &c- list all authed users.\n&03{t}auth add {hostmask matcher} &c- Add a user to the auth list.\n&03{t}auth remove {hostmask matcher} &c- Remove a user from the authlist."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 2:
            new_mask = msg_data["message"][2]
            if msg_data["message"][1] == "add":
                if bot.addAuthedHostmask(new_mask):
                    bot.irc.sendMSG("Added hostmask (%s) to auth list" % new_mask, msg_data["target"])
            if msg_data["message"][1] == "remove":
                if bot.removeAuthedHostmask(msg_data["message"][2]):
                    bot.irc.sendMSG("Removed hostmask (%s) from auth list" % new_mask, msg_data["target"])

        else:
            if len(bot.authed_hostmasks) == 0:
                bot.irc.sendMSG("No users authed.", msg_data["sender"])
                return True

            authentication_list = bot.authed_hostmasks

            page = 1
            page_size = 5
            all_pages = False
            pages = int(math.ceil(len(authentication_list) / float(page_size)))

            if len(msg_data["message"]) > 1 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][1]):
                if msg_data["message"][1] == "-a":
                    page_size = len(authentication_list);
                    all_pages = True
                else: page = int(msg_data["message"][1])

            if page > pages:
                page = 1

            pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
            if all_pages or page == pages: pages_info_string = "(&05%i&c)" % len(authentication_list)
            #?? pages is not very useful here

            bot.irc.sendMSG("Authed Users: %s" % colorizer(pages_info_string), msg_data["sender"])
            for index, mask in enumerate(pageFromList(authentication_list,page,page_size)):
                bot.irc.sendMSG("%s: %s" % (((page - 1) * page_size) + index, mask), msg_data["sender"])

        return True
