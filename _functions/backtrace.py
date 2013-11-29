#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.commands = ["trace"]
        self.function_string = "Get error tracebacks."
        self.restricted = True

    def main(self, bot, msg_data, func_type):
        if len(msg_data["message"]) > 1:
            trace_index = int(msg_data["message"][1])
            tracebacks = bot._functions.error_tracebacks
            if len(tracebacks) > trace_index:
                trace = tracebacks[trace_index]
                trace = trace.splitlines()
                for line in trace:
                    bot._irc.sendMSG(line, msg_data["target"])
                return True
            else:
                bot._irc.sendMSG("Trace index out of bounds.", msg_data["target"])
                return True
        else:
            bot._irc.sendMSG("Trace function requires a index argument.", msg_data["target"])
        return True
