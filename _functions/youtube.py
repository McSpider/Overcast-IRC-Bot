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
            youtubeMatch = re.findall("youtube\.com/watch\?.*?v=([A-Za-z0-9-_]+)", message, re.IGNORECASE)
            if not youtubeMatch: youtubeMatch = re.findall("youtu\.be/([A-Za-z0-9-_]+)", message, re.IGNORECASE)
            if youtubeMatch:
                for video_id in youtubeMatch:
                    print "Getting YT Video: " + str(video_id)
                    videoInfo = self.getVideoInfo(video_id)
                    if videoInfo and not videoInfo == 'RequestException':
                        bot._irc.sendMSG(videoInfo, msgData["target"])
                return True
            return False

        if (funcType == "command"):
            if len(msgData["message"]) > 1:
                message = msgData["message"][1]
                youtubeMatch = re.findall("youtube\.com/watch\?.*?v=([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if not youtubeMatch: youtubeMatch = re.findall("youtu\.be/([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if youtubeMatch:
                    for video_id in youtubeMatch:
                        print "Getting YT Video: " + str(video_id)
                        videoInfo = self.getVideoInfo(video_id)
                        if videoInfo == 'APIException':
                            bot._irc.sendMSG('Error: Failed to query youtube API', msgData["target"])
                            return True
                        elif videoInfo == 'RequestException':
                            bot._irc.sendMSG('Error: Invalid video URL', msgData["target"])
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
            return 'APIException'
        youtubeSoup = BeautifulSoup(r.text)
        if youtubeSoup.find(text='InvalidRequestUriException'):
            return 'RequestException'

        if youtubeSoup.find('title'):
            youtubeTitle = youtubeSoup.find('title').get_text()
            youtubeRating = ""
            youtubeAuthor = ""

            if youtubeSoup.find('author').find('name'):
                youtubeAuthor = ' by: ' + youtubeSoup.find('author').find('name').get_text()
            if youtubeSoup.find('yt:rating'):
                youtubeRating = colorizer(" - Likes:&03 %s&c Dislikes:&05 %s" % (youtubeSoup.find('yt:rating')['numlikes'], youtubeSoup.find('yt:rating')['numdislikes']))
            return "%s%s%s" % (youtubeTitle, youtubeAuthor, youtubeRating)

        return False



