#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import math

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["help"]
        self.function_string = "Overcast bot help."
        self.blocking = True
        self.priority = 3

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1 and not re.match("^(-a|[0-9]{1,3})$", msg_data["message"][1]):
            subcommand = msg_data["message"][1]
            
            func = bot.functions.getFunctionWithName(subcommand)
            if func:
                bot.irc.sendMSG("Info for function: %s%s%s" % (color.irc_blue, func.name, color.irc_clear), msg_data["sender"])
                bot.irc.sendMSG("%s" % func.function_string, msg_data["sender"])
                bot.irc.sendMSG("Restricted: %s - Type: %s" % (strFromBool(func.restricted), prettyListString(func.type, " & ", capitalize = True)), msg_data["sender"])
                
                if "command" in func.type:
                    bot.irc.sendMSG("Commands: %s" % (prettyListString(func.commands," & ")), msg_data["sender"])
                if not func.help_string == None:
                    help_str = func.help_string.replace("{t}",bot.short_trigger)
                    help_str = colorizer(help_str)
                    help_string_lines = string.split(help_str,"\n")
                    for line in help_string_lines:
                        bot.irc.sendMSG(line, msg_data["sender"])
            else:
                bot.irc.sendMSG("No function found with name: %s" % subcommand, msg_data["target"])
        else:
            bot.irc.sendMSG("Trigger the bot with: \"%s\" Short trigger: \"%s%s%s\"" % (prettyListString(bot.triggers," or ",color.irc_green), color.irc_green, bot.short_trigger, color.irc_clear), msg_data["sender"])


            function_msg = []
            authed = bot.isUserAuthed(msg_data["sender_hostmask"])
            functions_list = self.filterBotFunctions(bot.functions.functions_list, authed);

            page = 1
            page_size = 5
            all_pages = False
            pages = int(math.ceil(len(functions_list) / float(page_size)))

            if len(msg_data["message"]) > 1 and re.match("^(-a|[0-9]{1,3})$", msg_data["message"][1]):
                if msg_data["message"][1] == "-a":
                    page_size = len(functions_list);
                    all_pages = True
                else: page = int(msg_data["message"][1])

            if page > pages:
                page = 1

            pages_info_string = "(Page &05%i&c of &05%i&c) (Use &03-a&c to list all)" % (page, pages)
            if all_pages or pages == 1: pages_info_string = "(&05%i&c)" % len(functions_list)

            bot.irc.sendMSG("Functions you can trigger: %s" % colorizer(pages_info_string), msg_data["sender"])

            for func in pageFromList(functions_list,page,page_size):
                func_type = ""
                for fType in func.type:
                    if fType == "command":
                        func_type = "C" + func_type
                    if fType == "natural":
                        func_type = "N" + func_type
                    if fType == "status":
                        func_type = "S" + func_type
                func_type = func_type + "."
                func_string = "No commands"
                if fType == "command":
                    func_string = "Commands: %s" % prettyListString(func.commands, " & ", color.irc_blue).ljust(24)
                disabled = bot.functions.isFunctionDisabled(func)
                funct_disabled = colorizer(" &05Disabled for: %s&c" % timedstr(disabled[1],True) if disabled else "")
                bot.irc.sendMSG((color.irc_white + func_type + color.irc_clear + func.name).ljust(20) + func_string + funct_disabled, msg_data["sender"])

            if page == 1 or all_pages:
                bot.irc.sendMSG("For more info about a specific function use: %shelp {function name}" % (bot.short_trigger), msg_data["sender"])
            return True

        return False

    def filterBotFunctions(self, functions_list, authed):
        new_list = []
        for func in functions_list:
            if func.hidden == True:
                continue
            if func.restricted == True and not authed:
                continue
            new_list.append(func)
        return new_list

