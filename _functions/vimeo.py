#!/usr/bin/env python
from function_template import *
import requests

class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["natural"]
        self.priority = 100
        self.function_string = "Get vimeo movie info."


    def main(self, bot, msg_data, func_type):
        message = string.join(msg_data["message"])
        return_val = False
        
        vimeo_match = re.findall("vimeo\.com/([0-9]+)", message, re.IGNORECASE)
        if vimeo_match:
            for video_id in vimeo_match:
                print "Getting vimeo video: " + str(video_id)
                video_info = self.getVideoInfo(video_id)
                if video_info and not video_info == 'RequestException':
                    bot._irc.sendMSG(video_info, msg_data["target"])
                    return_val = True
        
        return return_val


    def getVideoInfo(self,video_id):
        r = requests.get("http://vimeo.com/api/v2/video/%s.xml" % video_id, headers = bot.http_header)
        if r.status_code != requests.codes.ok:
            return 'APIException'
        vimeo_soup = BeautifulSoup(r.text)

        if vimeo_soup.find('title'):
            vimeo_title = vimeo_soup.find('title').get_text()
            vimeo_rating = ""
            vimeo_author = ""

            # duration = vimeo_soup.find('duration').get_text()
            # if duration.isalnum():
            #     duration = int(duration)
            #     print timedstr(datetime.timedelta(seconds = duration))

            if vimeo_soup.find('user_name'):
                vimeo_author = ' by: ' + vimeo_soup.find('user_name').get_text()
            if vimeo_soup.find('stats_number_of_likes') and vimeo_soup.find('stats_number_of_comments'):
                vimeo_rating = colorizer(" - Likes:&03 %s&c Comments:&02 %s" % (vimeo_soup.find('stats_number_of_likes').get_text(), vimeo_soup.find('stats_number_of_comments').get_text()))
            return "%s%s%s" % (vimeo_title, vimeo_author, vimeo_rating)

        return False



