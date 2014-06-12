#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import minecraft.ping


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["mcping","mcp"]
        self.function_string = "Ping a minecraft server."

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            argument = msg_data["message"][1]

            try:
              data = minecraft.ping.get_info(argument)
            except:
              bot.irc.sendMSG("Unable to connect to: %s" % (argument), msg_data["target"])
              raise
            
            if data:
                ping_status = "Online Players: " + str(data["players"]["online"]).encode('utf-8') + "/" + str(data["players"]["max"]).encode('utf-8')
                ping_status = ping_status + " - Ping: " + str(data["ping"]).encode('utf-8') + "ms"
                bot.irc.sendMSG("%s" % (ping_status), msg_data["target"])

                motd = ""
                if isinstance(data["description"], str) or isinstance(data["description"], unicode):
                  motd = string.split(data["description"].encode('utf-8'), "\n")
                elif isinstance(data["description"], dict):
                  motd = string.split(data["description"]["text"].encode('utf-8'), "\n")

                prev_line_color = ""
                for line in motd:
                    bot.irc.sendMSG("%s%s" % (self.handleMcColors(prev_line_color), self.handleMcColors(line)), msg_data["target"])
                    prev_line_color = re.findall("§[0-9a-fk-r]", line, re.IGNORECASE)[-1]
        else:
            bot.irc.sendMSG("Please provide a minecraft server address to ping.", msg_data["target"])


        return True

    # Converts minecraft color codes to irc colors
    # Ambiguous colors (colors that are hard to see on certain backgrounds)
    # are replaced with the clear color so that a irc client can pick a contrasting color
    def handleMcColors(self, string):
        string = string.replace("§0", color.irc_clear) # Black
        string = string.replace("§1", color.irc_blue)
        string = string.replace("§2", color.irc_green)
        string = string.replace("§3", color.irc_cyan)
        string = string.replace("§4", color.irc_red)
        string = string.replace("§5", color.irc_violet)
        string = string.replace("§6", color.irc_yellow)
        string = string.replace("§7", color.irc_clear) # Grey
        string = string.replace("§8", color.irc_clear) # Dark grey
        string = string.replace("§9", color.irc_blue)
        string = string.replace("§a", color.irc_green)
        string = string.replace("§b", color.irc_cyan)
        string = string.replace("§c", color.irc_red)
        string = string.replace("§d", color.irc_violet)
        string = string.replace("§e", color.irc_yellow)
        string = string.replace("§f", color.irc_clear) # White

        string = string.replace("§k", "")
        string = string.replace("§l", "")
        string = string.replace("§m", "")
        string = string.replace("§n", "")
        string = string.replace("§o", "")
        string = string.replace("§r", color.irc_clear)
        return string
