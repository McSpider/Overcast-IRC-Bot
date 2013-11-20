#!/usr/bin/env python
from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.functionString = "Get the title for specific links."
        self.hidden = True


    def main(self, bot, msgData, funcType):
        if (funcType == "natural"):
            message = string.join(msgData["message"])

            link_matchers = {"Reddit":"(www\.reddit\.com/r/[A-Za-z0-9-_]+/[A-Za-z0-9-/_]+|redd\.it/[A-Za-z0-9-]+)", \
            "Overcast":"(oc\.tc/forums/topics/[A-Za-z0-9-]+|oc\.tc/forums/[A-Za-z0-9-]+)", \
            "Imgur":"(imgur\.com/[A-Za-z0-9-/_#]+|i\.imgur\.com/[A-Za-z0-9-/_#\.]+)", \
            "Oc Issues":"(github\.com/OvercastNetwork/[^\s/]+/issues/[0-9]+)"}


            titles = []
            match_found = False
            for key, value in link_matchers.iteritems():
                linkMatch = re.findall(value, message, re.IGNORECASE)

                if linkMatch:
                    for link in linkMatch:
                        # Ignore image imgur links since they usually don't have a useful title. (This should be handled differently...)
                        if re.match("i\.imgur\.com/[A-Za-z0-9-/_#\.]+", link, re.IGNORECASE):
                            continue

                        r = requests.get("http://" + link)
                        if r.status_code != requests.codes.ok:
                            continue

                        soup = BeautifulSoup(r.text)
                        if soup.find('title'):
                            match_found = True
                            pageTitle = soup.find('title').get_text().strip()

                            pageTitle = encode_unicode(pageTitle)

                            # Ignore oc.tc 404 pages
                            if key == "Overcast":
                                if pageTitle == "Home - Overcast Network Forum":
                                    continue

                            # Ignore imgur 404 pages
                            if key == "Imgur":
                                if pageTitle == "imgur: the simple image sharer":
                                    continue

                            # Don't print the same title twice
                            if not pageTitle in titles:
                                titles.append(pageTitle)
                                bot._irc.sendMSG(pageTitle, msgData["target"])
                    
            return match_found
       
        return False


