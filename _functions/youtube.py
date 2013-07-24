#!/usr/bin/env python
from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural","command"]
        self.commands = ["youtube"] 
        self.priority = 100
        self.functionString = "Get youtube movies and movie info."


    def main(self, bot, msgData, funcType):
        if (funcType == "natural"):
            message = string.join(msgData["message"])

            # /(www\.youtube\.com\/watch\?v=(\S+))/
            youtubeMatch = re.search("www\.youtube\.com/watch\?.*?v=(\S+)", message, re.IGNORECASE)
            if youtubeMatch:
                youtubeMatch = youtubeMatch.group(1)
                r = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % youtubeMatch)
                youtubeSoup = BeautifulSoup(r.text)
                print youtubeSoup
                if youtubeSoup.find(text='InvalidRequestUriException'):
                    return False

                if youtubeSoup.find('title'):
                    youtubeTitle = youtubeSoup.find('title').get_text()
                    youtubeRating = ""
                    youtubeAuthor = ""

                    if youtubeSoup.find('author').find('name'):
                        youtubeAuthor = ' by: ' + youtubeSoup.find('author').find('name').get_text()
                    if youtubeSoup.find('yt:rating'):
                        print youtubeSoup.find('yt:rating')
                        youtubeRating = colorizer(" - Likes:&03 %s&c Dislikes:&04 %s" % (youtubeSoup.find('yt:rating')['numlikes'], youtubeSoup.find('yt:rating')['numdislikes']))
                    bot._irc.sendMSG("%s%s%s" % (youtubeTitle, youtubeAuthor, youtubeRating), msgData["target"])
                    return True

            return False

        if (funcType == "command"):
            if len(msgData["message"]) > 1:
                pass
            else:
                pass
            return True

