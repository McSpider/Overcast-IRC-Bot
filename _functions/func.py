#!/usr/bin/env python
from function_template import *


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "functions"
        self.command = "func"
        self.functionString = "Manage bot functions."
        self.restricted = True

    def main(self, irc, msgData, funcType):
        if len(msgData["message"]) > 2:
            if msgData["message"][2] == "reload":
                irc._functions.reloadfunctions()
                return True
            if msgData["message"][2] == "list":
                irc.sendMSG("Functions page 1 of 1:", msgData["recipient"])
                for func in irc._functions.functionsList:
                    irc.sendMSG("%s - \"%s\"  t:%s r:%s" % (func.command, func.functionString, func.type, int(func.restricted)), msgData["recipient"])
                return True
        else:
            irc.sendMSG("Subcommands: reload & list.", msgData["recipient"])

        return False


# TODO update help command to list unrestricted commands
# we should also register subcommands in the function so that they can be listed with seperate auth status.
# functionsList = irc._functions.functionsList
# offset = 0
# pageSize = 2
# if (msgData["message"] >= 4):
#     offset = int(msgData["message"][3])

# irc.sendMSG("Functions page offset %i of %s:" % (offset, pageSize * offset), msgData["recipient"])
# for func in functionsList[1 * offset:pageSize * offset]:
#     irc.sendMSG("%s - \"%s\" type:%s" % (func.command, func.functionString, func.type), msgData["recipient"])