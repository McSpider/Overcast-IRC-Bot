#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["blacklist"]
        self.function_string = "Manage blacklisted users."
        self.help_string = "Subcommands:\n&03{t}blacklist &c- list all blacklisted users.\n&03{t}blacklist add {username or hostmask matcher} &c- Add a user to the blacklist.\n&03{t}blacklist remove {username or hostmask matcher} &c- Remove a user from the blacklist."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 2:
            new_mask = msg_data["message"][2]
            if msg_data["message"][1] == "add":
                if bot.addBlacklistedHostmask(new_mask):
                    bot.irc.sendMSG("Added hostmask (%s) to blacklist" % new_mask, msg_data["target"])
            if msg_data["message"][1] == "remove":
                if bot.removeBlacklistedHostmask(msg_data["message"][2]):
                    bot.irc.sendMSG("Removed hostmask (%s) from blacklist" % new_mask, msg_data["target"])

        else:
            if len(bot.blacklisted_users) == 0:
                bot.irc.sendMSG("No users blacklisted.", msg_data["sender"])
                return True

            blacklist_list = bot.blacklisted_users

            page = 1
            page_size = 5
            all_pages = False
            pages = int(math.ceil(len(blacklist_list) / float(page_size)))

            if len(msg_data["message"]) > 1 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][1]):
                if msg_data["message"][1] == "-a":
                    page_size = len(blacklist_list);
                    all_pages = True
                else: page = int(msg_data["message"][1])

            if page > pages:
                page = 1

            pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
            if all_pages or page == pages: pages_info_string = "(&05%i&c)" % pages

            bot.irc.sendMSG("Blacklisted Users: %s" % colorizer(pages_info_string), msg_data["sender"])
            for mask in pageFromList(blacklist_list,page,page_size):
                bot.irc.sendMSG("%s" % mask, msg_data["sender"])

        return True
