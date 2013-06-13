#!/usr/bin/env python
from function_template import *
import datetime  


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.name = "afk_msg"
        self.type = ["status","command"]
        self.command = "afk_msg"
        self.priority = 100
        self.functionString = "AFK nick change kicker."
        self.blocking = True

        self.timeout = None

        self.infractions = {}
        self.enabledChannels = []

    def main(self, irc, msgData, funcType):
        if (funcType == "status"):
            message = string.join(msgData["message"])
            if (msgData["messageType"] == "NICKCHANGE_NOTICE"):
                hostmask = string.lstrip(string.split(msgData["message"][0],"!")[1],":")
                changedNick = string.lstrip(msgData["message"][2],":")
                if re.match("^.*? NICK :.*?(AFK|Away).*?$", message, re.IGNORECASE):
                    if not hostmask in self.infractions:
                        self.infractions[hostmask] = 1
                    else:
                        self.infractions[hostmask] = self.infractions[hostmask] + 1

                    irc.sendMSG("%s: afk nicks are not liked in this channel, you have %s infraction(s)." % (changedNick, self.infractions[hostmask]), msgData["recipient"])
                    return True
        
        if (funcType == "command"):
            if len(msgData["message"]) > 2:
                subcommand = msgData["message"][2]
                if (subcommand == "add"):
                    if (msgData["recipient"] in self.enabledChannels):
                        irc.sendMSG("This channel (%s) is already being monitored." % (msgData["recipient"]), msgData["recipient"])
                    else:
                        irc.sendMSG("Monitoring channel %s for infractions." % (msgData["recipient"]), msgData["recipient"])
                        self.enabledChannels.append(msgData["recipient"])
                elif (subcommand == "infractions"):
                    if not msgData["recipient"] in self.enabledChannels:
                        irc.sendMSG("This channel (%s) is currently not being monitored." % (msgData["recipient"]), msgData["recipient"])
                    else:
                        if not self.infractions:
                            irc.sendMSG("No registered infractions at this time.", msgData["recipient"])
                        else:
                            irc.sendMSG("All registered infractions:", msgData["recipient"])
                            for k,v in self.infractions.items():
                                irc.sendMSG("%s (%s)" % (k, v), msgData["recipient"])
            if not msgData["recipient"] in self.enabledChannels:
                irc.sendMSG("This channel (%s) is currently not being monitored." % (msgData["recipient"]), msgData["recipient"])

            return True

        return False