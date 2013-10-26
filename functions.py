#!/usr/bin/env python
import os, sys
import string, re

import importlib
from utils import *
import datetime
import traceback


class functions:
    def __init__(self, delegate):
        self.functionsList = []
        self.loadfunctions()
        self.bot = delegate
        self.globalCooldown = {}
        self.errorTracebacks = []
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

    def checkForFunction(self, msgComponents, messageType, messageData):
        privateMessage = (messageType == "QUERY_MSG") or (messageType == "ACTION_MSG")
        publicMessage = (messageType == "CHANNEL_MSG") or (messageType == "CHANNEL_ACTION_MSG")

        msgSenderHostmask = msgComponents[0]
        msgSender = string.lstrip(string.split(msgSenderHostmask,"!")[0],":")

        if publicMessage or privateMessage:
            fullHostmask = messageData["username"] + "@" + messageData["hostmask"]
            if self.bot.hostmaskBlacklisted(fullHostmask):
                print color.b_red + "Ignoring message from blacklisted hostmask: " + color.clear + string.split(msgSenderHostmask,"!")[1]
                return

        # Global same sender message cooldown
        if msgSender in self.globalCooldown and not self.globalCooldown[msgSender] == None:
            print "Cooldown: " + str(self.globalCooldown[msgSender])
            if self.globalCooldown[msgSender]["messages"] > 2 and datetime.datetime.now() < self.globalCooldown[msgSender]["cooldown"] + datetime.timedelta(seconds = 5):
                self.globalCooldown[msgSender]["cooldown"] = datetime.datetime.now() + datetime.timedelta(seconds = 5)

            if datetime.datetime.now() < self.globalCooldown[msgSender]["cooldown"]:
                self.globalCooldown[msgSender]["cooldown"] = datetime.datetime.now() + datetime.timedelta(seconds = 1)
                self.globalCooldown[msgSender]["messages"] += 1

                print color.b_red + "Ignoring possible flood message" + color.clear
                if self.globalCooldown[msgSender]["messages"] > 10:
                    fullHostmask = messageData["username"] + "@" + messageData["hostmask"]
                    self.bot.addBlacklistedHostmask(fullHostmask)
                    self.bot._irc.sendMSG("Auto blacklisting hostmask: %s" % fullHostmask, self.bot.masterChannel)
                return
            else:
                self.globalCooldown[msgSender]["messages"] = 0

        # Check functions
        for func in self.functionsList:
            disabled = self.isFunctionDisabled(func)

            # Handle channel messages
            if (publicMessage or privateMessage) and len(msgComponents) >= 3:
                messageRecipient = msgComponents[2]

                target = messageRecipient
                if privateMessage:
                    target = msgSender

                msgData = {"recipient":messageRecipient,"message":msgComponents[3:], "rawMessage":" ".join(msgComponents), "sender":msgSender, "senderHostmask":msgSenderHostmask, "messageType":messageType, "target":target}
                msgData["message"][0] = msgData["message"][0][1:]

                if "command" in func.type:
                    # Check if the message has a trigger and a subcommand
                    if len(msgComponents) >= 4:
                        # :McSpider!~McSpider@192.65.241.17 PRIVMSG Qwerty1234444 :help ping ping ping
                        if privateMessage:
                            messageCommand = string.lstrip(msgComponents[3],":")
                            msgData["message"] = msgComponents[3:]

                            if messageCommand.lower() in func.commands:
                                # if disabled:
                                #     self.bot._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), messageRecipient)
                                #     continue
                                if not func.restricted or (func.restricted and self.bot.isUserAuthed(msgData["sender"],msgData["senderHostmask"])):
                                    funcExectuted = self.runFunction(func, msgData, "command")
                                    if funcExectuted and func.blocking:
                                        return
                                else: self.bot.notAllowedMessage(msgData["sender"],messageRecipient)
                                return

                        if (messageRecipient in self.bot.channels or privateMessage):
                            triggerMatch = self.checkForTriggerMatch(msgComponents)
                            if triggerMatch:
                                messageCommand = triggerMatch[0]
                                msgData["message"] = triggerMatch[1]
                                if messageCommand.lower() in func.commands:
                                    # if disabled:
                                    #     self.bot._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), messageRecipient)
                                    #     continue
                                    if not func.restricted or (func.restricted and self.bot.isUserAuthed(msgData["sender"],msgData["senderHostmask"])):
                                        funcExectuted = self.runFunction(func, msgData, "command")
                                        if funcExectuted and func.blocking:
                                            return
                                    else: self.bot.notAllowedMessage(msgData["sender"],messageRecipient)

                if "natural" in func.type:
                    funcExectuted = self.runFunction(func, msgData, "natural")
                    if funcExectuted and func.blocking:
                        return


            # Handle status messages
            else:
                msgData = {"recipient":None,"message":msgComponents[3:], "rawMessage":" ".join(msgComponents), "sender":None, "senderHostmask":None, "messageType":messageType}
                if "status" in func.type:
                    # if disabled:
                    #     self.bot._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), self.bot.masterChannel)
                    #     continue
                    funcExectuted = self.runFunction(func, msgData, "status")
                    if funcExectuted and func.blocking:
                        return

    def runFunction(self, func, messageData, type):
        try:
            functionExecuted = func.main(self.bot, messageData, type)
            if functionExecuted and func.blocking:
                func.runCount = func.runCount + 1
                print color.blue + "Blocking %s function executed: " % type + color.clear + func.functionString
            elif functionExecuted:
                func.runCount = func.runCount + 1
                print color.blue + "%s function executed: " % type.capitalize() + color.clear + func.name

            if functionExecuted:
                if not messageData["sender"] in self.globalCooldown:
                    self.globalCooldown[messageData["sender"]] = {"cooldown":None,"messages":0}
                self.globalCooldown[messageData["sender"]]["cooldown"] = datetime.datetime.now() + datetime.timedelta(seconds = 1)
                self.globalCooldown[messageData["sender"]]["messages"] += 1
                return True
            return False
        except Exception, e:
            trace = traceback.format_exc()
            self.errorTracebacks.append(trace)
            tb_index = len(self.errorTracebacks) - 1

            self.bot._irc.sendMSG("Failed to run function: %s%s%s - Trace index: %i" % (color.irc_blue, func.name, color.irc_clear, tb_index), self.bot.masterChannel)
            self.bot._irc.sendMSG(str(e), self.bot.masterChannel)
            self.bot._irc.sendMSG("Triggered by '%s'" % string.join(messageData["message"]), self.bot.masterChannel)

            print color.red + trace + color.clear

    def checkForTriggerMatch(self, msgComponents):
        if any(re.match("^:%s$" % re.escape(trigger), msgComponents[3], re.IGNORECASE) for trigger in self.bot.triggers) and len(msgComponents) >= 5:
            messageCommand = msgComponents[4]
            return [messageCommand,msgComponents[4:]]
        elif len(msgComponents) >= 4:
            if re.match("^:%s.*?$" % re.escape(self.bot.shortTrigger), msgComponents[3], re.IGNORECASE):
                messageCommand = string.lstrip(msgComponents[3],":"+ self.bot.shortTrigger)
                return [messageCommand,msgComponents[3:]]
        return False

    def isFunctionDisabled(self, function):
        if function.disabled == None:
            return False
        currentTime = datetime.datetime.now()
        if currentTime > function.disabled["time"]:
            function.disabled = None
            return False
        return [function.disabled["disabled_by"], currentTime - function.disabled["time"]]

    def disableFunction(self, function_name, time_delta, disabled_by):
        function = self.getFunctionWithName(function_name)
        if function:
            function.disabled = {}
            function.disabled["disabled_by"] = disabled_by
            function.disabled["time"] = datetime.datetime.now() + time_delta
            return True
        return False

    def enableFunction(self, function_name):
        function = self.getFunctionWithName(function_name)
        if function:
            function.disabled = None
            return True
        return False

    def getFunctionWithName(self, function_name):
        for function in self.functionsList:
            if function.name == function_name:
                return function
        return False


