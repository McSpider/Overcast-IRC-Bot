#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["status","mcstatus"]
        self.function_string = "Get the Overcast and minecraft server status."
    
    def main(self, bot, msg_data, func_type):
        show_legacy = False
        if len(msg_data["message"]) > 1 and re.match("^-l$", msg_data["message"][1]):
            show_legacy = True

        error = ''
        r = requests.get("https://oc.tc/play")
        if r.status_code != requests.codes.ok:
            status_string = ""
            if r.status_code == 522:
                status_string = "Connection Timed Out"
            error = 'oc.tc - Error: &05' + str(r.status_code) + "&c" + status_string
        else:
            oc_status = ""
            soup = BeautifulSoup(r.text)
            players_online = soup.find(text=re.compile(".*Players Online.*")).findParent('h3').find_all('small')[0].string.replace('\n','')

            eu_main_soup = soup.find('div',id="eu-main")
            us_main_soup = soup.find('div',id="us-main")
            if us_main_soup:
                us_status = us_main_soup.find("b", text=["Status"]).findParent('td').findParent('tr').find_all('td')[1].contents[2].strip('\n')
                oc_status += "US: " + us_status.title()
            if eu_main_soup:
                eu_status = eu_main_soup.find("b", text=["Status"]).findParent('td').findParent('tr').find_all('td')[1].contents[2].strip('\n')
                oc_status += (", " if oc_status else "") + "EU: " + eu_status.title()

            if len(players_online) > 0:
                oc_status = oc_status + " - Online Players: " + players_online
            bot._irc.sendMSG("%s" % (oc_status), msg_data["target"])

            ## Offline servers
            eu_servers = []
            us_servers = []
            us_soup = soup.find('div',id="us")
            eu_soup = soup.find('div',id="eu")

            us_offline = us_soup.find_all(text='(Offline)')
            for item in us_offline:
                offline_server = item.parent.parent.contents[0].replace('\n','')
                if offline_server:
                    us_servers.append(offline_server)

            eu_offline = eu_soup.find_all(text='(Offline)')
            for item in eu_offline:
                offline_server = item.parent.parent.contents[0].replace('\n','')
                if offline_server:
                    eu_servers.append(offline_server)

            if len(us_servers) > 0:
                bot._irc.sendMSG("US Servers Offline: " + prettyListString(us_servers, " & ", cc = color.irc_red), msg_data["target"])
            if len(eu_servers) > 0:
                bot._irc.sendMSG("EU Servers Offline: " + prettyListString(eu_servers, " & ", cc = color.irc_red), msg_data["target"])
            ##
            

        r = requests.get("http://status.mojang.com/check")
        if r.status_code != requests.codes.ok:
            error = 'status.mojang.com/check - &05' + str(r.status_code) + "&c"
        else:
            mojang_status_raw = r.json()
            legacy_items = ["login.minecraft.net"];
            mojang_status = []
            legacy_status = []
            # Move status items to correct list
            for status in mojang_status_raw:
                for key in status:
                    if key in legacy_items:
                        legacy_status.append(status)
                    else:
                        mojang_status.append(status)

            status_string = self.parseStatus(mojang_status)
            status_string = colorizer(status_string.rstrip(', '))
            bot._irc.sendMSG("%s" % (status_string), msg_data["target"])
            
            if show_legacy:
                status_string_legacy = self.parseStatus(legacy_status)
                status_string_legacy = colorizer(status_string.rstrip(', '))
                bot._irc.sendMSG("Legacy: %s" % (status_string_legacy), msg_data["target"])


        if error: bot._irc.sendMSG(colorizer(error), msg_data["target"])
        return True

    def parseStatus(self, status):
        result = ""
        for x in status:
            for key in x:
                keyvalue = key
                if key != "minecraft.net":
                    keyvalue = key.split(".",1)[0]

                if x[key] == "green":
                    result = result + keyvalue + " &03OK&c, "
                else:
                    result = result + keyvalue + " &05Offline&c, "
        return result
