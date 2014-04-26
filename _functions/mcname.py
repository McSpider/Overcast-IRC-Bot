#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["mcname"]
        self.function_string = "Check if a minecraft user name is registered."

    def main(self, bot, msg_data, func_type):
        players = [];
        if len(msg_data["message"]) > 1:
            msg = " ".join(msg_data["message"][1:])
            players = msg.strip().split(',')
        else:
            bot.irc.sendMSG("Please provide a username or comma separated list of usernames", msg_data["target"])

        if len(players) > 10 and not bot.isUserAuthed(msg_data["sender_hostmask"]):
            bot.irc.sendMSG("Please restrict your query to less that 10 usernames", msg_data["sender"])
            return True

        recipient = msg_data["target"]
        if len(players) > 1:
            recipient = msg_data["sender"]

        for player in players:
            error = ''
            r = requests.get("https://account.minecraft.net/buy/frame/checkName/" + str(player), headers = bot.http_header)
            if r.status_code != requests.codes.ok:
                error = 'Request Exception - Code: ' + str(r.status_code)
            else:
                soup = BeautifulSoup(r.text)
                if soup.find(text=["OK"]):
                    bot.irc.sendMSG("%s - Username is available" % player, recipient)
                elif soup.find(text=["TAKEN"]):
                    bot.irc.sendMSG("%s - Username has already been taken" % player, recipient)
                elif soup.find(text=["invalid characters"]):
                    bot.irc.sendMSG("%s - Name contains invalid characters. Please stick to letters, numbers and _" % player, recipient)
                else:
                    bot.irc.sendMSG("%s - %s" % (player, soup.text), recipient)

            if error: bot.irc.sendMSG(error, recipient)
        return True
