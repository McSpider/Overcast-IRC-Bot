#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["trace"]
        self.functionString = "Get error tracebacks."
        self.restricted = True

    def main(self, bot, msgData, funcType):
        if len(msgData["message"]) > 1:
            traceIndex = int(msgData["message"][1])
            tracebacks = bot._functions.errorTracebacks
            if len(tracebacks) > traceIndex:
                trace = tracebacks[traceIndex]
                trace = trace.splitlines()
                for line in trace:
                    bot._irc.sendMSG(line, msgData["target"])
                return True
            else:
                bot._irc.sendMSG("Trace index out of bounds.", msgData["target"])
                return True
        else:
            bot._irc.sendMSG("Trace function requires a index argument.", msgData["target"])
        return True
