#!/usr/bin/env python
from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural","command"]
        self.commands = ["youtube","yt"] 
        self.priority = 100
        self.functionString = "Get youtube movies and movie info."


    def main(self, bot, msgData, funcType):
        if (funcType == "natural"):
            message = string.join(msgData["message"])
            youtubeMatch = re.findall("www\.youtube\.com/watch\?.*?v=([A-Za-z0-9]+)", message, re.IGNORECASE)
            if youtubeMatch:
                for video_id in youtubeMatch:
                    videoInfo = self.getVideoInfo(video_id)
                    if videoInfo:
                        bot._irc.sendMSG(colorizer("&15%s&c %s" % (video_id, videoInfo)), msgData["target"])
                return True
            return False

        if (funcType == "command"):
            if len(msgData["message"]) > 1:
                video_url = msgData["message"][1]
                youtubeMatch = re.search("www\.youtube\.com/watch\?.*?v=([A-Za-z0-9]+)", video_url, re.IGNORECASE)
                if youtubeMatch:
                    video_id = youtubeMatch.group(1)
                    videoInfo = self.getVideoInfo(video_id)
                    if videoInfo == 'InvalidRequestUriException':
                        bot._irc.sendMSG(colorizer('&04Error:&c Invalid video URL'), msgData["target"])
                        return True
                    if videoInfo:
                        bot._irc.sendMSG(videoInfo, msgData["target"])
                        return True
            else:
                pass
            return False

    def getVideoInfo(self,video_id):
        r = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % video_id)
        if r.status_code != requests.codes.ok:
            return 'RequestException'
        youtubeSoup = BeautifulSoup(r.text)
        if youtubeSoup.find(text='InvalidRequestUriException'):
            return 'InvalidRequestUriException'

        if youtubeSoup.find('title'):
            youtubeTitle = youtubeSoup.find('title').get_text()
            youtubeRating = ""
            youtubeAuthor = ""

            if youtubeSoup.find('author').find('name'):
                youtubeAuthor = ' by: ' + youtubeSoup.find('author').find('name').get_text()
            if youtubeSoup.find('yt:rating'):
                youtubeRating = colorizer(" - Likes:&03 %s&c Dislikes:&04 %s" % (youtubeSoup.find('yt:rating')['numlikes'], youtubeSoup.find('yt:rating')['numdislikes']))
            return "%s%s%s" % (youtubeTitle, youtubeAuthor, youtubeRating)

        return False



