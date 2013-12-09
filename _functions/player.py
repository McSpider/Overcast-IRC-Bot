#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["player","stats"]
        self.functionString = "Show the stats for a player."

    def main(self, bot, msgData, funcType):
        message = msgData["message"]
        player = "";
        if len(message) > 1:
            player = message[1]
        else:
            bot._irc.sendMSG("No player specified", msgData["target"])
            return True

        error = ''
        r = requests.get("http://oc.tc/" + str(player))
        if r.status_code != requests.codes.ok:
            if r.status_code == 404:
                error = '404 - User not found'
            else:
                error = 'Request Exception - Code: ' + str(r.status_code)
        else:
            soup = BeautifulSoup(r.text)
            if soup.find("h4", text=["Account Suspended"]):
                error = 'User Account Suspended'
            elif soup.find("p", text=["Page Exploded"]):
                error = '404 - User not found'
            elif soup.find("small", text=["server joins"]):
                kills = soup.find("small", text=["kills"]).findParent('h2').contents[0].strip('\n')

                last_seen = "- Last seen unavailable"
                last_seen_data = soup.find("span", text=re.compile(".*%s.*" % str(player), re.IGNORECASE)).findParent('h1')
                if not len(last_seen_data.contents) < 5:
                    last_seen = string.join(last_seen_data.contents[3].contents[0].split())
                    if last_seen == "Online:":
                        last_seen_server = last_seen_data.find(href="/play").contents[1].contents[0]
                        last_seen = last_seen + " " + last_seen_server
                    last_seen = "- " + last_seen
                
                deaths = soup.find("small", text=["deaths"]).findParent('h2').contents[0].strip('\n')
                friends = soup.find("small", text=["friends"]).findParent('h2').contents[0].strip('\n')
                kd_ratio = soup.find("small", text=["kd ratio"]).findParent('h2').contents[0].strip('\n')
                kk_ratio = soup.find("small", text=["kk ratio"]).findParent('h2').contents[0].strip('\n')
                joins = soup.find("small", text=["server joins"]).findParent('h2').contents[0].strip('\n')
                raindrops = soup.find("small", text=["raindrops"]).findParent('h2').contents[0].strip('\n')

                wools = soup.find("small", text=["wools placed"]).findParent('h2').contents[0].strip('\n')
                cores = soup.find("small", text=["cores leaked"]).findParent('h2').contents[0].strip('\n')
                monuments = soup.find("small", text=["monuments destroyed"]).findParent('h2').contents[0].strip('\n')

                stats_message = colorizer("Kills:&05 %s&c, Deaths:&05 %s&c, KD Ratio:&05 %s&c, KK Ratio:&05 %s&c" % (kills, deaths, kd_ratio, kk_ratio))
                objectives_message = colorizer("Wools Placed:&02 %s&c, Cores Leaked:&02 %s&c, Monuments Destroyed:&02 %s&c" % (wools, cores, monuments))
                friends_message = colorizer("Friends:&03 %s&c, Joins:&03 %s&c" % (friends, joins))
                raindrops_message = colorizer("&10Rain&cdrops: %s" % (raindrops))

                bot._irc.sendMSG("%s %s - %s" % (str(player), last_seen, raindrops_message), msgData["target"])
                bot._irc.sendMSG(stats_message, msgData["target"])
                bot._irc.sendMSG(objectives_message, msgData["target"])
                bot._irc.sendMSG(friends_message, msgData["target"])
            else:
                error = 'Invalid user.'

        if error: bot._irc.sendMSG(error, msgData["target"])
        return True
