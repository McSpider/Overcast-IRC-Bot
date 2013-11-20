#!/usr/bin/env python
import os, sys
import string, re

import importlib
from utils import *
import datetime
import traceback


class functions:
    def __init__(self, delegate, irc):
        self.functionsList = []
        self.loadfunctions()
        self._bot = delegate
        self._irc = irc
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

            self.functionsList = sorted(self.functionsList, key=lambda function: function.priority, reverse=False)

    def checkForFunction(self, msgComponents, messageType, messageData):
        privateMessage = (messageType == "QUERY_MSG") or (messageType == "ACTION_MSG")
        publicMessage = (messageType == "CHANNEL_MSG") or (messageType == "CHANNEL_ACTION_MSG")

        msgSenderHostmask = msgComponents[0]
        msgSender = (string.split(msgSenderHostmask,"!")[0])[1:]

        if publicMessage or privateMessage:
            fullHostmask = messageData["username"] + "@" + messageData["hostmask"]
            if self._bot.hostmaskBlacklisted(fullHostmask):
                print color.b_red + "Ignoring message from blacklisted hostmask: " + color.clear + string.split(msgSenderHostmask,"!")[1]
                return

        # Global same sender message cooldown
        if msgSender in self.globalCooldown and not self.globalCooldown[msgSender] == None:
            current_time = datetime.datetime.now()
            if self.globalCooldown[msgSender]["messages"] < 2 and current_time < self.globalCooldown[msgSender]["cooldown"] + datetime.timedelta(seconds = 5):
                self.globalCooldown[msgSender]["cooldown"] = current_time + datetime.timedelta(seconds = 5)

            if current_time < self.globalCooldown[msgSender]["cooldown"]:
                self.globalCooldown[msgSender]["cooldown"] = current_time + datetime.timedelta(seconds = 1)
                self.globalCooldown[msgSender]["messages"] += 1

                print color.b_red + "Ignoring possible flood message" + color.clear
                if self.globalCooldown[msgSender]["messages"] > 10:
                    fullHostmask = messageData["username"] + "@" + messageData["hostmask"]
                    self._bot.addBlacklistedHostmask(fullHostmask)
                    self._irc.sendMSG("Auto blacklisting hostmask: %s" % fullHostmask, self._bot.masterChannel)
                return
            else:
                self.globalCooldown[msgSender]["messages"] = 0


        # Handle channel messages
        if (publicMessage or privateMessage) and len(msgComponents) >= 3:
            messageRecipient = msgComponents[2]

            target = messageRecipient
            if privateMessage:
                target = msgSender

            msgData = {"recipient":messageRecipient,"message":msgComponents[3:], "rawMessage":" ".join(msgComponents), "sender":msgSender, "senderHostmask":msgSenderHostmask, "messageType":messageType, "target":target}
            if msgData["message"][0].startswith(":"):
                msgData["message"][0] = (msgData["message"][0])[1:]
            # Check functions
            for func in self.functionsList:
                disabled = self.isFunctionDisabled(func)
                if "command" in func.type and len(msgComponents) >= 4:
                    # Check if the message has a trigger and a subcommand or just a subcommand if its a PM
                    if (self._irc._channels.isConnectedTo(messageRecipient) or privateMessage):
                        triggerMatch = self.checkForTriggerMatch(msgComponents,privateMessage)
                        if triggerMatch:
                            messageCommand = triggerMatch[0].lower()
                            msgData["message"] = triggerMatch[1]
                            msgData["command"] = messageCommand
                            if messageCommand in func.commands:
                                if disabled:
                                    self._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), self._bot.masterChannel)
                                    continue
                                if not func.restricted or (func.restricted and self._bot.isUserAuthed(msgData["sender"],msgData["senderHostmask"])):
                                    funcExectuted = self.runFunction(func, msgData, "command")
                                    if funcExectuted and func.blocking:
                                        return
                                else: self._bot.notAllowedMessage(msgData["sender"],messageRecipient)

                if "natural" in func.type:
                    funcExectuted = self.runFunction(func, msgData, "natural")
                    if funcExectuted and func.blocking:
                        return


        # Handle status messages
        else:
            msgData = {"recipient":None,"message":msgComponents[3:], "rawMessage":" ".join(msgComponents), "sender":None, "senderHostmask":None, "messageType":messageType}
            # Check functions
            for func in self.functionsList:
                disabled = self.isFunctionDisabled(func)
                if "status" in func.type:
                    if disabled:
                        self._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), self._bot.masterChannel)
                        continue
                    funcExectuted = self.runFunction(func, msgData, "status")
                    if funcExectuted and func.blocking:
                        return

    def runFunction(self, func, messageData, type):
        try:
            functionExecuted = func.main(self._bot, messageData, type)
            if functionExecuted and func.blocking:
                func.runCount = func.runCount + 1
                print color.blue + "Blocking %s function executed: " % type + color.clear + func.functionString
            elif functionExecuted:
                func.runCount = func.runCount + 1
                print color.blue + "%s function executed: " % type.capitalize() + color.clear + func.name

            if functionExecuted:
                if not messageData["sender"] in self.globalCooldown:
                    self.globalCooldown[messageData["sender"]] = {"cooldown":None,"messages":0}
                self.globalCooldown[messageData["sender"]]["cooldown"] = datetime.datetime.now()
                self.globalCooldown[messageData["sender"]]["messages"] += 1
                return True
            return False
        except Exception, e:
            trace = traceback.format_exc()
            self.errorTracebacks.append(trace)
            tb_index = len(self.errorTracebacks) - 1

            self._irc.sendMSG("Failed to run function: %s%s%s - Trace index: %i" % (color.irc_blue, func.name, color.irc_clear, tb_index), self._bot.masterChannel)
            self._irc.sendMSG(str(e), self._bot.masterChannel)
            self._irc.sendMSG("Triggered by '%s'" % string.join(messageData["message"]), self._bot.masterChannel)

            print color.red + trace + color.clear

    def checkForTriggerMatch(self, msgComponents, privateMessage):
        message = msgComponents[3:]
        if message[0].startswith(":"):
            message[0] = (message[0])[1:]

        if any(re.match("^:%s$" % re.escape(trigger), msgComponents[3], re.IGNORECASE) for trigger in self._bot.triggers) and len(msgComponents) >= 5:
            messageCommand = msgComponents[4]
            return [messageCommand,msgComponents[4:]]
        elif len(msgComponents) >= 4:
            if re.match("^:%s.*?$" % re.escape(self._bot.shortTrigger), msgComponents[3], re.IGNORECASE):
                # Strip the short trigger
                messageCommand = (message[0])[len(self._bot.shortTrigger):]
                message[0] = messageCommand
                return [messageCommand,message]
        if privateMessage: # Private messages don't require a trigger
            return [message[0],message]
        return False

    def isFunctionDisabled(self, function):
        if function.disabled == None:
            return False
        current_time = datetime.datetime.now()
        if current_time > function.disabled["time"]:
            function.disabled = None
            return False
        return [function.disabled["disabled_by"], current_time - function.disabled["time"]]

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


