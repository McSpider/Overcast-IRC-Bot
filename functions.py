#!/usr/bin/env python
import os, sys
import string, re

import importlib
from utils import *
import datetime
import traceback


class functions:
    def __init__(self, delegate, irc):
        self.functions_list = []
        self.loadFunctions()
        self._bot = delegate
        self._irc = irc
        self.global_cooldown = {}
        self.error_tracebacks = []
        pass

    def loadFunctions(self):
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
                self.functions_list.append(instance)

            self.functions_list = sorted(self.functions_list, key=lambda function: function.priority, reverse=False)

    def checkForFunction(self, msg_components, message_type, message_data):
        private_message = (message_type == "QUERY_MSG") or (message_type == "ACTION_MSG")
        public_message = (message_type == "CHANNEL_MSG") or (message_type == "CHANNEL_ACTION_MSG")

        # Sender status/permissions check
        if public_message or private_message:
            sender_full_hostmask = message_data["nick"] + "!" + message_data["username"] + "@" + message_data["hostmask"]
            if self._bot.hostmaskBlacklisted(sender_full_hostmask):
                if not self._bot.isUserAuthed(sender_full_hostmask):
                    print color.b_red + "Ignoring message from blacklisted hostmask: " + color.clear + sender_full_hostmask
                    return
                else: self._irc.sendMSG("Authed user blacklist match: %s (Verify?)" % sender_full_hostmask, self._bot.masterChannel)

            # Global same sender message cooldown
            msg_sender = message_data["nick"]
            if msg_sender in self.global_cooldown and not self.global_cooldown[msg_sender] == None:
                current_time = datetime.datetime.now()
                cooldown = self.global_cooldown[msg_sender]["cooldown"]
                print self.global_cooldown[msg_sender]

                # Auto blacklist user if they have sent 10 triggering messages in the last 5 seconds
                if self.global_cooldown[msg_sender]["messages"] > 10 and current_time < cooldown + datetime.timedelta(seconds = 5):
                    if not self._bot.hostmaskBlacklisted(sender_full_hostmask):
                        sender_full_hostmask = message_data["username"] + "@" + message_data["hostmask"]
                        self._bot.addBlacklistedHostmask(sender_full_hostmask)
                        self._irc.sendMSG("Auto blacklisting hostmask: %s" % sender_full_hostmask, self._bot.masterChannel)
                        return

                # Ignore user if they have sent 2 or more messages in the last 2 seconds, or 3 messages in 3 seconds
                if self.global_cooldown[msg_sender]["messages"] >= 2 and current_time < cooldown + datetime.timedelta(seconds = 2) or \
                 self.global_cooldown[msg_sender]["messages"] >= 3 and current_time < cooldown + datetime.timedelta(seconds = 3):
                    self.global_cooldown[msg_sender]["cooldown"] = current_time
                    self.global_cooldown[msg_sender]["messages"] += 1
                    print color.b_red + "Ignoring possible flood message from: " + color.clear + msg_sender
                    return
                
                # Reset cooldown if the user hasn't sent a message in the last 5 seconds
                if current_time > cooldown + datetime.timedelta(seconds = 5):
                    self.global_cooldown[msg_sender]["messages"] = 0


        # Handle channel messages
        if (public_message or private_message) and len(msg_components) >= 3:
            sender_full_hostmask = message_data["nick"] + "!" + message_data["username"] + "@" + message_data["hostmask"]
            message_recipient = msg_components[2]
            msg_sender = message_data["nick"]

            target = message_recipient
            if private_message:
                target = msg_sender

            msgData = {"recipient":message_recipient,"message":msg_components[3:], "rawMessage":" ".join(msg_components), "sender":msg_sender, "senderHostmask":message_data["hostmask"], "message_type":message_type, "target":target}
            if msgData["message"][0].startswith(":"):
                msgData["message"][0] = (msgData["message"][0])[1:]
            # Check functions
            for func in self.functions_list:
                disabled = self.isFunctionDisabled(func)
                if "command" in func.type and len(msg_components) >= 4:
                    # Check if the message has a trigger and a subcommand or just a subcommand if its a PM
                    if (self._irc._channels.isConnectedTo(message_recipient) or private_message):
                        triggerMatch = self.checkForTriggerMatch(msg_components,private_message)
                        if triggerMatch:
                            messageCommand = triggerMatch[0].lower()
                            msgData["message"] = triggerMatch[1]
                            msgData["command"] = messageCommand
                            if messageCommand in func.commands:
                                if disabled:
                                    self._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), self._bot.masterChannel)
                                    continue
                                if not func.restricted or (func.restricted and self._bot.isUserAuthed(sender_full_hostmask)):
                                    funcExectuted = self.runFunction(func, msgData, "command")
                                    if funcExectuted and func.blocking:
                                        return
                                else: self._bot.notAllowedMessage(msgData["sender"],message_recipient)

                if "natural" in func.type:
                    funcExectuted = self.runFunction(func, msgData, "natural")
                    if funcExectuted and func.blocking:
                        return


        # Handle status messages
        else:
            msgData = {"recipient":None,"message":msg_components[3:], "rawMessage":" ".join(msg_components), "sender":None, "senderHostmask":None, "message_type":message_type}
            # Check functions
            for func in self.functions_list:
                disabled = self.isFunctionDisabled(func)
                if "status" in func.type:
                    if disabled:
                        self._irc.sendMSG("%s function disabled by: %s" % (func.name ,disabled[0]), self._bot.masterChannel)
                        continue
                    funcExectuted = self.runFunction(func, msgData, "status")
                    if funcExectuted and func.blocking:
                        return

    def runFunction(self, func, message_data, type):
        try:
            functionExecuted = func.main(self._bot, message_data, type)
            if functionExecuted and func.blocking:
                func.runCount = func.runCount + 1
                print color.blue + "Blocking %s function executed: " % type + color.clear + func.functionString
            elif functionExecuted:
                func.runCount = func.runCount + 1
                print color.blue + "%s function executed: " % type.capitalize() + color.clear + func.name

            if functionExecuted:
                if not message_data["sender"] in self.global_cooldown:
                    self.global_cooldown[message_data["sender"]] = {"cooldown":None,"messages":0}
                self.global_cooldown[message_data["sender"]]["cooldown"] = datetime.datetime.now()
                self.global_cooldown[message_data["sender"]]["messages"] += 1
                return True
            return False
        except Exception, e:
            trace = traceback.format_exc()
            self.error_tracebacks.append(trace)
            tb_index = len(self.error_tracebacks) - 1

            self._irc.sendMSG("Failed to run function: %s%s%s - Trace index: %i" % (color.irc_blue, func.name, color.irc_clear, tb_index), self._bot.masterChannel)
            self._irc.sendMSG(str(e), self._bot.masterChannel)
            self._irc.sendMSG("Triggered by '%s'" % string.join(message_data["message"]), self._bot.masterChannel)

            print color.red + trace + color.clear

    def checkForTriggerMatch(self, msg_components, private_message):
        message = msg_components[3:]
        if message[0].startswith(":"):
            message[0] = (message[0])[1:]

        if any(re.match("^:%s$" % re.escape(trigger), msg_components[3], re.IGNORECASE) for trigger in self._bot.triggers) and len(msg_components) >= 5:
            messageCommand = msg_components[4]
            return [messageCommand,msg_components[4:]]
        elif len(msg_components) >= 4:
            if re.match("^:%s.*?$" % re.escape(self._bot.shortTrigger), msg_components[3], re.IGNORECASE):
                # Strip the short trigger
                messageCommand = (message[0])[len(self._bot.shortTrigger):]
                message[0] = messageCommand
                return [messageCommand,message]
        if private_message: # Private messages don't require a trigger
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
        for function in self.functions_list:
            if function.name == function_name:
                return function
        return False


