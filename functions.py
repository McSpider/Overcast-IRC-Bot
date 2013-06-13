#!/usr/bin/env python
import os, sys
import string, re

import config
import importlib
from utils import *


class functions:
    def __init__(self):
        self.functionsList = []
        self.loadfunctions()
        pass

    def loadfunctions(self):
        lib_path = os.path.abspath('./_functions/')
        sys.path.append(lib_path)

        for f in os.listdir(os.path.abspath("./_functions/")):
            functionName, ext = os.path.splitext(f)
            if ext == ".py":
                # print color.green + 'Imported module: ' + color.clear + functionName
                function = __import__(functionName)
                command_func = getattr(function, "function")
                instance = command_func()
                self.functionsList.append(instance)

            self.functionsList = sorted(self.functionsList, key=lambda function: function.priority, reverse=True)

    def reloadfunctions(self):
        for func in self.functionsList:
            func = reload(func)
        self.irc.sendMSG("Functions reloaded", config.masterChannel)

    def checkForFunction(self, irc, msgComponents, messageType):
        msgSenderHostmask = msgComponents[0]
        msgSender = string.lstrip(string.split(msgSenderHostmask,"!")[0],":")

        for func in self.functionsList:
            # Handle channel messages
            if ((messageType == "CHANNEL_MSG") or (messageType == "CHANNEL_ACTION_MSG") or (messageType == "QUERY_MSG") or (messageType == "ACTION_MSG")) and len(msgComponents) >= 3:
                messageRecipient = msgComponents[2]
                messageData = {"recipient":messageRecipient,"message":msgComponents[3:], "sender":msgSender, "senderHostmask":msgSenderHostmask, "messageType":messageType}
                messageData["message"][0] = messageData["message"][0][1:]

                if "natural" in func.type:
                    functionExecuted = func.main(irc, messageData, "natural")
                    if functionExecuted and func.blocking:
                        func.runCount = func.runCount + 1
                        print color.blue + "Natural blocking function executed:" + color.clear + func.functionString
                        return
                    elif functionExecuted:
                        func.runCount = func.runCount + 1
                        print color.blue + "Natural function executed:" + color.clear + func.functionString

                elif "command" in func.type:
                    # Check if the message has a trigger and a subcommand
                    if len(msgComponents) >= 5:
                        messageCommand = msgComponents[3]
                        messageSubCommand = msgComponents[4]

                        if (messageRecipient in config.channels) and any(messageCommand in ":" + trigger for trigger in config.triggers) and len(messageData["message"]) >= 2:
                            if (messageSubCommand == func.command):
                                if not func.restricted or (func.restricted and irc.isUserAuthed(messageData["sender"],messageData["senderHostmask"])):
                                    print color.blue + "Run command function: " + color.clear + func.functionString
                                    func.main(irc, messageData, "command")
                                    func.runCount = func.runCount + 1
                                    return
                                else:
                                    irc.sendMSG("You're not allowed to do that %s" % messageData["sender"], messageRecipient)

            # Handle status messages
            else:
                messageData = {"recipient":None,"message":msgComponents[3:], "sender":None, "senderHostmask":None, "messageType":messageType}
                if "status" in func.type:
                    functionExecuted = func.main(irc, messageData, "status")
                    if functionExecuted and func.blocking:
                        func.runCount = func.runCount + 1
                        print color.blue + "Status blocking function executed:" + color.clear + func.functionString
                        return
                    elif functionExecuted:
                        func.runCount = func.runCount + 1
                        print color.blue + "Status function executed:" + color.clear + func.functionString








