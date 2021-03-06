#!/usr/bin/env python
# -*- coding: utf-8 -*-

## NOTE: For this function to work you will need a valid API key.

from function_template import *
import requests
import json

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
                    log.debug("Getting YT Video: " + str(video_id))
                    video_info = self.getVideoInfo(bot, video_id)
                    if video_info and not video_info == 'RequestException':
                        bot.irc.sendMSG(video_info, msg_data["target"])
                return True
            return False

        if (func_type == "command"):
            if len(msg_data["message"]) > 1:
                message = msg_data["message"][1]
                youtube_match = re.findall("youtube\.com/watch\?.*?v=([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if not youtube_match: youtube_match = re.findall("youtu\.be/([A-Za-z0-9-_]+)", message, re.IGNORECASE)
                if youtube_match:
                    for video_id in youtube_match:
                        log.debug("Getting YT Video: " + str(video_id))
                        video_info = self.getVideoInfo(bot, video_id)
                        if video_info == 'APIException':
                            bot.irc.sendMSG('Error: Failed to query youtube API', msg_data["target"])
                            return True
                        elif video_info == 'RequestException':
                            bot.irc.sendMSG('Error: Invalid video URL', msg_data["target"])
                            return True
                        if video_info:
                            bot.irc.sendMSG(video_info, msg_data["target"])
                            return True
            return False

    def getVideoInfo(self, bot, video_id):
        r = requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=%s&fields=items(snippet,statistics)&key=%s" % (video_id, "YOUR API KEY HERE"), headers = bot.http_header)

        # log.debug(r.status_code)
        if r.status_code != requests.codes.ok:
            return 'APIException'
        # log.debug(r.text)
        youtube_soup = json.loads(r.text)


        # if youtube_soup.find(text='InvalidRequestUriException'):
        #     return 'RequestException'

        if youtube_soup['items'][0]['snippet']:
            youtube_title = youtube_soup['items'][0]['snippet']['title']
            youtube_author = ' by: ' + youtube_soup['items'][0]['snippet']['channelTitle']
            youtube_rating = ""

            if youtube_soup['items'][0]['statistics']:
                youtube_rating = colorizer(" - Likes:&03 %s&c Dislikes:&05 %s" % (youtube_soup['items'][0]['statistics']['likeCount'],youtube_soup['items'][0]['statistics']['dislikeCount']))

            return ("%s%s%s" % (youtube_title, youtube_author, youtube_rating)).encode('utf-8')

        return False

