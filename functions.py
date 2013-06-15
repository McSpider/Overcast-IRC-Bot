#!/usr/bin/env python
import os, sys
import string, re

import config
import importlib
from utils import *
import datetime


class functions:
    def __init__(self, delegate):
        self.functionsList = []
        self.loadfunctions()
        self.bot = delegate
        self.globalCooldown = {}
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
                instance.name = functionName + ext
                self.functionsList.append(instance)

            self.functionsList = sorted(self.functionsList, key=lambda function: function.priority, reverse=True)

    def reloadfunctions(self):
        for func in self.functionsList:
            func = reload(func)
  #self.irc.sendMSG("Functions reloaded", config.masterChannel)

    def checkForFunction(self, msgComponents, messageType):
        msgSenderHostmask = msgComponents[0]
        msgSender = string.lstrip(string.split(msgSenderHostmask,"!")[0],":")

        # Global same sender message cooldown
        if msgSender in self.globalCooldown and (not (self.globalCooldown[msgSender] == None or datetime.datetime.now() > self.globalCooldown[msgSender])):
            return

        # Check functions
        for func in self.functionsList:
            # Handle channel messages
            privateMessage = (messageType == "QUERY_MSG") or (messageType == "ACTION_MSG")
            if ((messageType == "CHANNEL_MSG") or (messageType == "CHANNEL_ACTION_MSG") or privateMessage) and len(msgComponents) >= 3:
                messageRecipient = msgComponents[2]

                target = messageRecipient
                if privateMessage:
                    target = msgSender

                messageData = {"recipient":messageRecipient,"message":msgComponents[3:], "sender":msgSender, "senderHostmask":msgSenderHostmask, "messageType":messageType, "target":target}
                messageData["message"][0] = messageData["message"][0][1:]

                if "natural" in func.type:
                    self.runFunction(func, messageData, "natural")

                if "command" in func.type:
                    # Check if the message has a trigger and a subcommand
                    if len(msgComponents) >= 4:
                        messageCommand = msgComponents[3]
                        messageData["message"] = msgComponents[4:]
                        if (messageRecipient in config.channels) and any(messageCommand.lower() in ":" + trigger.lower() for trigger in config.triggers) and len(msgComponents) >= 5:
                            messageCommand = msgComponents[4]
                            if messageCommand in func.commands:
                                if not func.restricted or (func.restricted and self.bot.isUserAuthed(messageData["sender"],messageData["senderHostmask"])):
                                    self.runFunction(func, messageData, "command")
                                else:
                                    self.bot._irc.sendMSG("You're not allowed to do that %s" % messageData["sender"], messageRecipient)
                        elif privateMessage:
                            if messageCommand[1:] in func.commands:
                                if not func.restricted or (func.restricted and self.bot.isUserAuthed(messageData["sender"],messageData["senderHostmask"])):
                                    self.runFunction(func, messageData, "command")
                                else:
                                    self.bot._irc.sendMSG("You're not allowed to do that %s" % messageData["sender"], messageRecipient)

            # Handle status messages
            else:
                messageData = {"recipient":None,"message":msgComponents[3:], "sender":None, "senderHostmask":None, "messageType":messageType}
                if "status" in func.type:
                    self.runFunction(func, messageData, "status")

    def runFunction(self, func, messageData, type):
        # try:
        functionExecuted = func.main(self.bot, messageData, type)
        if functionExecuted and func.blocking:
            func.runCount = func.runCount + 1
            print color.blue + "Blocking %s function executed:" % type + color.clear + func.functionString
            return
        elif functionExecuted:
            func.runCount = func.runCount + 1
            print color.blue + "%s function executed:" % type.capitalize() + color.clear + func.name

        if functionExecuted:
            self.globalCooldown[messageData["sender"]] = datetime.datetime.now() + datetime.timedelta(seconds = 1)
            return True
        return False
        # except Exception:
        #         print color.red + "Exception raised!"






