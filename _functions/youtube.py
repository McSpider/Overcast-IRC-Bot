#!/usr/bin/env python
from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural","command"]
        self.commands = ["youtube","yt"] 
        self.priority = 100
        self.function_string = "Get youtube movies and movie info."


    def main(self, bot, msg_data, func_type):
        if (func_type == "natural"):
            message = string.join(msg_data["message"])
            youtube_match = re.findall("youtube\.com/watch\?.*?v=([A-Za-z0-9-_]+)", message, re.IGNORECASE)
            if not youtube_match: youtube_match = re.findall("youtu\.be/([A-Za-z0-9-_]+)", message, re.IGNORECASE)
            if youtube_match:
                for video_id in youtube_match:
                    print "Getting YT Video: " + str(video_id)
                    video_info = self.getVideoInfo(video_id)
                    if video_info and not video_info == 'RequestException':
                        bot._irc.sendMSG(video_info, msg_data["target"])
                return True
            return False

        if (func_type == "command"):
            if len(msg_data["message"]) > 1:
                message = msg_data["message"][1]
                youtube_match = re.findall("youtube\.com/watch\?.*?v=([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if not youtube_match: youtube_match = re.findall("youtu\.be/([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if youtube_match:
                    for video_id in youtube_match:
                        print "Getting YT Video: " + str(video_id)
                        video_info = self.getVideoInfo(video_id)
                        if video_info == 'APIException':
                            bot._irc.sendMSG('Error: Failed to query youtube API', msg_data["target"])
                            return True
                        elif video_info == 'RequestException':
                            bot._irc.sendMSG('Error: Invalid video URL', msg_data["target"])
                            return True
                        if video_info:
                            bot._irc.sendMSG(video_info, msg_data["target"])
                            return True
            return False

    def getVideoInfo(self,video_id):
        r = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % video_id, headers = bot.http_header)
        if r.status_code != requests.codes.ok:
            return 'APIException'
        youtube_soup = BeautifulSoup(r.text)
        if youtube_soup.find(text='InvalidRequestUriException'):
            return 'RequestException'

        if youtube_soup.find('title'):
            youtube_title = youtube_soup.find('title').get_text()
            youtube_rating = ""
            youtube_author = ""

            if youtube_soup.find('author').find('name'):
                youtube_author = ' by: ' + youtube_soup.find('author').find('name').get_text()
            if youtube_soup.find('yt:rating'):
                youtube_rating = colorizer(" - Likes:&03 %s&c Dislikes:&05 %s" % (youtube_soup.find('yt:rating')['numlikes'], youtube_soup.find('yt:rating')['numdislikes']))
            return "%s%s%s" % (youtube_title, youtube_author, youtube_rating)

        return False



