#!/usr/bin/env python
from function_template import *
import requests


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["status","mcstatus"]
        self.function_string = "Get the Overcast and minecraft server status. (uses xpaw.ru/mcstatus)"
        self.help_string = "Arguments:|.-e Show extended status info, if available."
    
    def main(self, bot, msg_data, func_type):
        show_legacy = False
        show_extended = False

        if len(msg_data["message"]) > 1:
            for msg_part in msg_data["message"][1:]:
                if re.match("^-e$", msg_part):
                    show_extended = True

        self.getOvercastStatus(bot, msg_data)
        self.getMinecraftStatus(bot, msg_data, show_legacy, show_extended)


        return True


    def getOvercastStatus(self, bot, msg_data):
        r = requests.get("https://oc.tc/play", headers = bot.http_header)
        if r.status_code != requests.codes.ok:
            status_string = ""
            if r.status_code == 522:
                status_string = "Connection Timed Out"
            error = 'oc.tc - Error: &05' + str(r.status_code) + "&c" + status_string
            bot._irc.sendMSG(error, msg_data["target"])
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


    def getMinecraftStatus(self, bot, msg_data, show_legacy, show_extended):
        try:
            r = requests.get("http://xpaw.ru/mcstatus/status.json", headers = bot.http_header)
        except requests.exceptions.RequestException:
            raise
            return False

        if r.status_code != requests.codes.ok:
            error = 'xpaw.ru/mcstatus - &05' + str(r.status_code) + "&c"
            bot._irc.sendMSG(error, msg_data["target"])
            return False
        else:
            xpaw_status_raw = r.json()
            status_string = "xpaw.ru/mcstatus - "

            login_status = xpaw_status_raw["report"]["login"]
            sessions_status = xpaw_status_raw["report"]["session"]
            website_status = xpaw_status_raw["report"]["website"]
            skins_status = xpaw_status_raw["report"]["skins"]
            realms_status = xpaw_status_raw["report"]["realms"]

            status_string += "login: " + self.colorizeStatusCode(login_status["status"])
            status_string += ", session: " + self.colorizeStatusCode(sessions_status["status"])
            status_string += ", website: " + self.colorizeStatusCode(website_status["status"])
            status_string += ", skins: " + self.colorizeStatusCode(skins_status["status"])
            status_string += ", realms: " + self.colorizeStatusCode(realms_status["status"])

            status_string = colorizer(status_string.rstrip(', '))
            bot._irc.sendMSG("%s" % (status_string), msg_data["target"])

            if show_extended:
                login_title = self.colorizeExtendedStatus(login_status)
                if login_title != None:
                    bot._irc.sendMSG("Login: %s" % colorizer(login_title), msg_data["target"])
                session_title = self.colorizeExtendedStatus(sessions_status)
                if session_title != None:
                    bot._irc.sendMSG("Session: %s" % colorizer(session_title), msg_data["target"])
                website_title = self.colorizeExtendedStatus(website_status)
                if website_title != None:
                    bot._irc.sendMSG("Website: %s" % colorizer(website_title), msg_data["target"])
                skins_title = self.colorizeExtendedStatus(skins_status)
                if skins_title != None:
                    bot._irc.sendMSG("Skins: %s" % colorizer(skins_title), msg_data["target"])
                realms_title = self.colorizeExtendedStatus(realms_status)
                if realms_title != None:
                    bot._irc.sendMSG("Realms: %s" % colorizer(realms_title), msg_data["target"])
        return True

    def colorizeStatusCode(self, status):
        if status == "down":
            return "&05Offline&c"
        elif status == "up":
            return "&03OK&c"
        elif status == "problem":
            return "&07Problem&c"
        return "&07Unknown&c"

    def colorizeExtendedStatus(self, status):
        if status["status"] == "down":
            return "&05" + status["title"] + "&c"
        if status["status"] == "up" and status["title"] != "Online":
            return "&03" + status["title"] + "&c"
        if status["status"] == "problem":
            return "&07" + status["title"] + "&c"
        return None
