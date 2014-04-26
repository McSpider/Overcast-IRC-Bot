#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["premium","haspaid","paid"]
        self.function_string = "Check if a minecraft user has paid."

    def main(self, bot, msg_data, func_type):
        message = msg_data["message"]
        player = "";
        if len(message) > 1:
            player = message[1]
        else:
            player = msg_data["sender"]

        error = ''
        r = requests.get("https://minecraft.net/haspaid.jsp?user=" + str(player), headers = bot.http_header)
        if r.status_code != requests.codes.ok:
            if r.status_code == 404:
                error = '404 - User not found'
            else:
                error = 'Request Exception - Code: ' + str(r.status_code)
        else:
            soup = BeautifulSoup(r.text)
            if soup.find(text=["false"]):
                bot.irc.sendMSG("%s has not purchased minecraft yet." % (player), msg_data["target"])
            else:
                bot.irc.sendMSG("%s has purchased minecraft." % (player), msg_data["target"])

        if error: bot.irc.sendMSG(error, msg_data["target"])
        return True
