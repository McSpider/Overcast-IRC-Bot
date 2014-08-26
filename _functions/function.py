#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["function", "func"]
        self.function_string = "Manage functions."
        self.help_string = "Subcommands:\n&03{t}function disable {function} (duration) &c- Disable the specified function.\n&03{t}function enable {function} &c- Enable the specified function.\n&03{t}function list &c- list all disabled functions."
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
                        bot.irc.sendMSG("Invalid time delta: %s" % msg_data["message"][3], msg_data["target"])
                        return

                if bot.functions.disableFunction(msg_data["message"][2], timedelta, disabled_by):
                    bot.irc.sendMSG(colorizer("Disabled function: &05%s&c for %s" % (msg_data["message"][2], timedstr(timedelta))), msg_data["target"])
                else:
                    bot.irc.sendMSG("Invalid function name: %s" % msg_data["message"][2], msg_data["target"])

            if msg_data["message"][1] == "enable":
                if bot.functions.enableFunction(msg_data["message"][2]):
                    bot.irc.sendMSG("Enabled function: %s" % msg_data["message"][2], msg_data["target"])
                else:
                    bot.irc.sendMSG("Invalid function name: %s" % msg_data["message"][2], msg_data["target"])

            if msg_data["message"][1] == "list":
                authed = bot.isUserAuthed(msg_data["sender_hostmask"])
                functions_list = []
                for func in bot.functions.functions_list:
                    if func.hidden == True:
                        continue
                    if func.restricted == True and not authed:
                        continue
                    if not bot.functions.isFunctionDisabled(func):
                        continue
                    functions_list.append(func)

                if len(functions_list) > 0:
                    page = 1
                    page_size = 5
                    all_pages = False
                    pages = int(math.ceil(len(functions_list) / float(page_size)))

                    if len(msg_data["message"]) > 2 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][2]):
                        if msg_data["message"][2] == "-a":
                            page_size = len(functions_list);
                            all_pages = True
                        else: page = int(msg_data["message"][2])

                    if page > pages:
                        page = 1

                    pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
                    if all_pages or pages == 1: pages_info_string = "(&05%i&c)" % len(functions_list)

                    bot.irc.sendMSG("Functions: %s" % colorizer(pages_info_string), msg_data["sender"])
                    for func in pageFromList(functions_list,page,page_size):
                        disabled = bot.functions.isFunctionDisabled(func)
                        funct_disabled = colorizer(" &05Disabled for:&c %s" % timedstr(disabled[1],True) if disabled else "")
                        bot.irc.sendMSG(colorizer(func.name.ljust(20) + funct_disabled), msg_data["sender"])
                else:
                    bot.irc.sendMSG("No functions disabled", msg_data["sender"])
            return True


        else:
            bot.irc.sendMSG("Subcommands: disable, enable & list.", msg_data["sender"])
        return True

