#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["status"]
        self.functionString = "Get the Overcast server status."
    
    def main(self, bot, msgData, funcType):
        error = ''
        try: data = urllib.urlopen('http://oc.tc/play')
        except urllib2.HTTPError, e:
            error = 'HTTP Error: ' + str(e.code)
        except urllib2.URLError, e:
            error = 'URL Error: ' + str(e.reason)
        except httplib.HTTPException, e:
            error = 'HTTP Exception'
        else:
            if (data.getcode() == int('404')):
                error = '404 - User not found'
            elif (data.getcode() == int('200')):
                soup = BeautifulSoup(data)
                
                status = soup.find("h3", text=re.compile(".*Players Online.*"))#.contents#[1].strip('\n')

                status = soup.find("b", text=["Status"]).findParent('td').findParent('tr').find_all('td')[1].contents[2].strip('\n')
                bot._irc.sendMSG("%s" % (status), msgData["target"])

        if error: bot._irc.sendMSG(error, msgData["target"])
        return True

