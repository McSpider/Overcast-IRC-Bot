#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["premium","haspaid","paid"]
        self.functionString = "Check if a minecraft user has paid."

    def main(self, bot, msgData, funcType):
        message = msgData["message"]
        player = "";
        if len(message) > 1:
            player = message[1]
        else:
            player = msgData["sender"]

        error = ''
        r = requests.get("https://minecraft.net/haspaid.jsp?user=" + str(player))
        if r.status_code != requests.codes.ok:
            if r.status_code == 404:
                error = '404 - User not found'
            else:
                error = 'Request Exception - Code: ' + str(r.status_code)
        else:
            soup = BeautifulSoup(r.text)
            if soup.find(text=["false"]):
                bot._irc.sendMSG("%s has not purchased minecraft yet." % (player), msgData["target"])
            else:
                bot._irc.sendMSG("%s has purchased minecraft." % (player), msgData["target"])

        if error: bot._irc.sendMSG(error, msgData["target"])
        return True
