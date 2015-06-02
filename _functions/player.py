#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["player","stats"]
        self.function_string = "Show the stats for a player."

    def main(self, bot, msg_data, func_type):
        message = msg_data["message"]
        player = "";
        if len(message) > 1:
            player = message[1]
        else:
            player = msg_data["sender"]

        error = ''
        r = requests.get("http://oc.tc/" + str(player), headers = bot.http_header)
        if r.status_code != requests.codes.ok:
            if r.status_code == 404:
                error = '404 - User not found'
            if r.status_code == 522:
                error = '522 - Request Timed Out'
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

                last_seen = ""
                last_seen_data = soup.find("span", text=re.compile(".*%s.*" % str(player), re.IGNORECASE)).findParent('h1')
                print last_seen_data.contents
                if not len(last_seen_data.contents) < 5:
                    last_seen = string.join(last_seen_data.contents[3].contents[0].split()) # Remove newlines
                    last_seen = last_seen.strip('(').strip(')')
                    last_seen = last_seen.split(" ")[1]
                    last_seen = " - Formerly: " + last_seen

                deaths = soup.find("small", text=["deaths"]).findParent('h2').contents[0].strip('\n')
                friends = soup.find("small", text=["friends"]).findParent('h2').contents[0].strip('\n')
                kd_ratio = soup.find("small", text=["kd ratio"]).findParent('h2').contents[0].strip('\n')
                kk_ratio = soup.find("small", text=["kk ratio"]).findParent('h2').contents[0].strip('\n')
                joins = soup.find("small", text=["server joins"]).findParent('h2').contents[0].strip('\n')
                raindrops = soup.find("small", text=["raindrops"]).findParent('h2').contents[0].strip('\n')

                wools = "0"
                cores = "0"
                monuments = "0"

                wools_element = soup.find("small", text=["wools placed"])
                if wools_element:
                    wools = wools_element.findParent('h2').contents[0].strip('\n')

                cores_element = soup.find("small", text=["cores leaked"])
                if cores_element:
                    cores = cores_element.findParent('h2').contents[0].strip('\n')

                monuments_element = soup.find("small", text=["monuments destroyed"])
                if monuments_element:
                    monuments = monuments_element.findParent('h2').contents[0].strip('\n')

                stats_message = colorizer("Kills:&05 %s&c, Deaths:&05 %s&c, KD Ratio:&05 %s&c, KK Ratio:&05 %s&c" % (kills, deaths, kd_ratio, kk_ratio))
                objectives_message = colorizer("Wools Placed:&02 %s&c, Cores Leaked:&02 %s&c, Monuments Destroyed:&02 %s&c" % (wools, cores, monuments))
                friends_message = colorizer("Friends:&03 %s&c, Joins:&03 %s&c" % (friends, joins))
                raindrops_message = colorizer("&10Rain&cdrops: %s" % (raindrops))
                player = colorizer("&b%s&c" % player)
                bot.irc.sendMSG("%s%s - %s" % (str(player), last_seen, raindrops_message), msg_data["target"])
                bot.irc.sendMSG(stats_message, msg_data["target"])
                bot.irc.sendMSG(objectives_message, msg_data["target"])
                bot.irc.sendMSG(friends_message, msg_data["target"])
            else:
                error = 'Invalid user.'

        if error: bot.irc.sendMSG(error, msg_data["target"])
        return True
