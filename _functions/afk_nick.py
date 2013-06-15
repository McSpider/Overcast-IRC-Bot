#!/usr/bin/env python
from function_template import *
import datetime  


class function(function_template):
    def __init__(self):
        function_template.__init__(self)
        self.type = ["status","command"]
        self.commands = ["afk_msg"]
        self.priority = 100
        self.functionString = "AFK nick change kicker."
        self.blocking = True

        self.timeout = None

        self.infractions = {}
        self.enabledChannels = []

    def main(self, bot, msgData, funcType):
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

                    bot._irc.sendMSG("%s: afk nicks are not liked in this channel, you have %s infraction(s)." % (changedNick, self.infractions[hostmask]), msgData["target"])
                    return True
        
        if (funcType == "command"):
            if len(msgData["message"]) > 1:
                subcommand = msgData["message"][1]
                if (subcommand == "add"):
                    if (msgData["target"] in self.enabledChannels):
                        bot._irc.sendMSG("This channel (%s) is already being monitored." % (msgData["target"]), msgData["target"])
                    else:
                        bot._irc.sendMSG("Monitoring channel %s for infractions." % (msgData["target"]), msgData["target"])
                        self.enabledChannels.append(msgData["target"])
                elif (subcommand == "infractions"):
                    if not msgData["target"] in self.enabledChannels:
                        bot._irc.sendMSG("This channel (%s) is currently not being monitored." % (msgData["target"]), msgData["target"])
                    else:
                        if not self.infractions:
                            bot._irc.sendMSG("No registered infractions at this time.", msgData["target"])
                        else:
                            bot._irc.sendMSG("All registered infractions:", msgData["target"])
                            for k,v in self.infractions.items():
                                bot._irc.sendMSG("%s (%s)" % (k, v), msgData["target"])
            if not msgData["target"] in self.enabledChannels:
                bot._irc.sendMSG("This channel (%s) is currently not being monitored." % (msgData["target"]), msgData["target"])

            return True

        return False