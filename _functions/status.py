#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["status","mcstatus"]
        self.functionString = "Get the Overcast and minecraft server status."
    
    def main(self, bot, msgData, funcType):
        error = ''
        r = requests.get("https://oc.tc/play")
        if r.status_code != requests.codes.ok:
            error = 'oc.tc - &05' + str(r.status_code) + "&c"
        else:
            soup = BeautifulSoup(r.text)
            status = soup.find("h3", text=re.compile(".*Players Online.*"))#.contents#[1].strip('\n')

            status = soup.find("b", text=["Status"]).findParent('td').findParent('tr').find_all('td')[1].contents[2].strip('\n')
            bot._irc.sendMSG("oc.tc: %s" % (status), msgData["target"])
            
        r = requests.get("http://status.mojang.com/check")
        if r.status_code != requests.codes.ok:
            error = 'status.mojang.com/check - &05' + str(r.status_code) + "&c"
        else:
            result = ""
            mojang_status = r.json()
            for x in mojang_status:
                for key in x:
                    keyvalue = key
                    if key != "minecraft.net":
                        keyvalue = key.split(".",1)[0]

                    if x[key] == "green":
                        result = result + keyvalue + " &03OK&c, "
                    else:
                        result = result + keyvalue + " &050&c, "

            result = colorizer(result.rstrip(', '))
            bot._irc.sendMSG("%s" % (result), msgData["target"])

        if error: bot._irc.sendMSG(colorizer(error), msgData["target"])
        return True
