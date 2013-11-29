#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["colors"]
        self.function_string = "List all available colorzer() colors."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        bot._irc.sendMSG(colorizer("&00BWhite &01Black &02Blue &03Green &04BRed &05Red &06Violet &07Yellow &08BYellow &09BGreen &10Cyan &11BCyan &12BBlue &13BViolet &14BBlack &15White&c"), msg_data["target"])
        return True
