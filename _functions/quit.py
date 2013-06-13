#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "quit"
        self.command = "quit"
        self.functionString = "Quit the bot."
        self.restricted = True
        self.priority = 1
        self.blocking = True

    def main(self, irc, msgData, funcType):
        irc.quit()
        return True