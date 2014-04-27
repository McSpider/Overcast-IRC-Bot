#!/usr/bin/env python
# -*- coding: utf-8 -*-

from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.function_string = "Get the title for specific links."
        self.hidden = True


    def main(self, bot, msg_data, func_type):
        if (func_type == "natural"):
            message = string.join(msg_data["message"])

            link_matchers = {"Reddit":"(www\.reddit\.com/r/[A-Za-z0-9-_]+/[A-Za-z0-9-/_]+|redd\.it/[A-Za-z0-9-]+)", \
            "Overcast":"(oc\.tc/forums/topics/[A-Za-z0-9-]+|oc\.tc/forums/posts/[A-Za-z0-9-]+|oc\.tc/forums/[A-Za-z0-9-]+)", \
            "Imgur":"(imgur\.com/[A-Za-z0-9-/_#]+|i\.imgur\.com/[A-Za-z0-9-/_#\.]+)", \
            "Oc Issues":"(github\.com/OvercastNetwork/[^\s/]+/issues/[0-9]+)"}


            titles = []
            match_found = False
            for key, value in link_matchers.iteritems():
                link_match = re.findall(value, message, re.IGNORECASE)

                if link_match:
                    for link in link_match:
                        # Ignore image imgur links since they usually don't have a useful title. (This should be handled differently...)
                        if re.match("i\.imgur\.com/[A-Za-z0-9-/_#\.]+", link, re.IGNORECASE):
                            continue

                        r = requests.get("http://" + link, headers = bot.http_header)
                        if r.status_code != requests.codes.ok:
                            log.debug(r.headers)
                            if r.status_code == 404:
                                bot.irc.sendMSG(message, bot.master_channel)
                                bot.irc.sendMSG('404 - Page not found', bot.master_channel)
                            else:
                                bot.irc.sendMSG(message, bot.master_channel)
                                bot.irc.sendMSG('Request Exception - Code: %s' % str(r.status_code), bot.master_channel)
                            continue

                        soup = BeautifulSoup(r.text)
                        if soup.find('title'):
                            match_found = True
                            page_title = soup.find('title').get_text().strip()

                            page_title = page_title.encode('utf-8')

                            # Ignore oc.tc 404 pages
                            if key == "Overcast":
                                if page_title == "Home - Overcast Network Forum":
                                    continue

                            # Ignore imgur 404 pages
                            if key == "Imgur":
                                if page_title == "imgur: the simple image sharer":
                                    continue

                            # Don't print the same title twice
                            if not page_title in titles:
                                titles.append(page_title)
                                bot.irc.sendMSG(page_title, msg_data["target"])
                    
            return match_found
       
        return False


