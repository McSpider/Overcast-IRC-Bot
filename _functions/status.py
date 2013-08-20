#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["status"]
        self.functionString = "Get the Overcast server status."
    
    def main(self, bot, msgData, funcType):
        error = ''
        r = requests.get("https://oc.tc/play")
        if r.status_code != requests.codes.ok:
            error = 'Request Exception - Code: ' + str(r.status_code)
        else:
            soup = BeautifulSoup(r.text)
            status = soup.find("h3", text=re.compile(".*Players Online.*"))#.contents#[1].strip('\n')

            status = soup.find("b", text=["Status"]).findParent('td').findParent('tr').find_all('td')[1].contents[2].strip('\n')
            bot._irc.sendMSG("%s" % (status), msgData["target"])

        if error: bot._irc.sendMSG(error, msgData["target"])
        return True
