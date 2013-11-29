#!/usr/bin/env python
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
            "Overcast":"(oc\.tc/forums/topics/[A-Za-z0-9-]+|oc\.tc/forums/[A-Za-z0-9-]+)", \
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
                            print "linktitle.py - imgur image link"
                            continue

                        r = requests.get("http://" + link)
                        if r.status_code != requests.codes.ok:
                            print "linktitle.py - request status code error"
                            continue

                        soup = BeautifulSoup(r.text)
                        if soup.find('title'):
                            match_found = True
                            page_title = soup.find('title').get_text().strip()

                            page_title = encode_unicode(page_title)

                            # Ignore oc.tc 404 pages
                            if key == "Overcast":
                                if page_title == "Home - Overcast Network Forum":
                                    print "linktitle.py - oc.tc home/404 page"
                                    continue

                            # Ignore imgur 404 pages
                            if key == "Imgur":
                                if page_title == "imgur: the simple image sharer":
                                    print "linktitle.py - imgur home/404 page"
                                    continue

                            # Don't print the same title twice
                            if not page_title in titles:
                                titles.append(page_title)
                                bot._irc.sendMSG(page_title, msg_data["target"])
                    
            return match_found
       
        return False


