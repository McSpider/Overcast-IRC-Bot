#!/usr/bin/env python
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
            bot._irc.sendMSG("Please provide a username or comma separated list of usernames", msg_data["target"])


        recipient = msg_data["target"]
        if len(players) > 1:
            recipient = msg_data["sender"]

        for player in players:
            error = ''
            r = requests.get("https://account.minecraft.net/buy/frame/checkName/" + str(player))
            if r.status_code != requests.codes.ok:
                error = 'Request Exception - Code: ' + str(r.status_code)
            else:
                soup = BeautifulSoup(r.text)
                if soup.find(text=["OK"]):
                    bot._irc.sendMSG("%s - Username is available" % player, recipient)
                elif soup.find(text=["TAKEN"]):
                    bot._irc.sendMSG("%s - Username has already been taken" % player, recipient)
                elif soup.find(text=["invalid characters"]):
                    bot._irc.sendMSG("%s - Name contains invalid characters. Please stick to letters, numbers and _" % player, recipient)
                else:
                    bot._irc.sendMSG("%s - %s" % (player, soup.text), recipient)

            if error: bot._irc.sendMSG(error, recipient)
        return True
