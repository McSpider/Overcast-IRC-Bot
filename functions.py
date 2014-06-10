#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import string, re
import traceback

import importlib
from utils import *
import datetime

import logging
log = logging.getLogger(__name__)


class functions:
    def __init__(self, delegate, irc):
        self.functions_list = []
        self._bot = delegate
        self._irc = irc
        self.global_cooldown = {}
        self.error_tracebacks = []

        self.statistics = {}
        stats_data = self._bot.openDataFile("_statistics", "_functions/", default = {})
        if type(stats_data) is dict:
            self.statistics = stats_data
        
        # Make sure the function data directory exists and if not, create it
        function_data_dir = os.path.dirname('./_functiondata/')
        if not os.path.exists(function_data_dir):
            os.makedirs(function_data_dir)
            log.warning(color.red + "Function data directory not found, creating" + color.clear)

        self.loadFunctions()
        pass

    def loadFunctions(self):
        lib_path = os.path.abspath('./_functions/')
        sys.path.append(lib_path)

        for f in os.listdir(os.path.abspath("./_functions/")):
            function_name, ext = os.path.splitext(f)
            if ext == ".py":
                function = __import__(function_name)
                command_func = getattr(function, "function")
                instance = command_func()
                instance.name = function_name + ext
                instance.load(self._bot)
                self.functions_list.append(instance)

            self.functions_list = sorted(self.functions_list, key=lambda function: function.priority, reverse=False)

    def unloadFunctions(self):
        for func in self.functions_list:
            # Update the function statistics
            if func.name in self.statistics:
                self.statistics[func.name]["run_count"] = int(self.statistics[func.name]["run_count"]) + func.run_count
            else:
                self.statistics[func.name] = {"first_run":str(datetime.datetime.now()),"run_count":func.run_count}

            func.unload(self._bot)

        self._bot.saveDataFile(self.statistics,"_statistics","_functions/")

    def checkForFunction(self, msg_components, message_type, message_data):
        private_message = (message_type == "QUERY_MSG") or (message_type == "ACTION_MSG")
        public_message = (message_type == "CHANNEL_MSG") or (message_type == "CHANNEL_ACTION_MSG")

        # Sender status/permissions check
        if public_message or private_message:
            sender_full_hostmask = message_data["nick"] + "!" + message_data["username"] + "@" + message_data["hostmask"]
            blacklist_match = self._bot.hostmaskBlacklisted(sender_full_hostmask)
            if blacklist_match:
                if not self._bot.isUserAuthed(sender_full_hostmask):
                    log.info(color.b_red + "Ignoring message from blacklisted hostmask: " + color.clear + sender_full_hostmask + color.b_red + " matches: " + color.clear + blacklist_match)
                    return
                else: self._irc.sendMSG("Authed user blacklist match: %s matches: %s (Verify?)" % sender_full_hostmask, blacklist_match, self._bot.master_channel)

            # Global same sender message cooldown
            msg_sender = message_data["nick"]
            if msg_sender in self.global_cooldown and not self.global_cooldown[msg_sender] == None:
                current_time = datetime.datetime.now()
                cooldown = self.global_cooldown[msg_sender]["cooldown"]

                # Auto blacklist user if they have sent 10 triggering messages in the last 5 seconds
                if self.global_cooldown[msg_sender]["messages"] > 10 and current_time < cooldown + datetime.timedelta(seconds = 5):
                    if not self._bot.hostmaskBlacklisted(sender_full_hostmask):
                        sender_full_hostmask = message_data["username"] + "@" + message_data["hostmask"]
                        self._bot.addBlacklistedHostmask(sender_full_hostmask)
                        self._irc.sendMSG("Auto blacklisting hostmask: %s" % sender_full_hostmask, self._bot.master_channel)
                        return

                # Ignore user if they have sent 2 or more messages in the last 2 seconds, or 3 messages in 3 seconds
                if self.global_cooldown[msg_sender]["messages"] >= 2 and current_time < cooldown + datetime.timedelta(seconds = 2) or \
                 self.global_cooldown[msg_sender]["messages"] >= 3 and current_time < cooldown + datetime.timedelta(seconds = 3):
                    self.global_cooldown[msg_sender]["cooldown"] = current_time
                    self.global_cooldown[msg_sender]["messages"] += 1
                    log.info(color.b_red + "Ignoring possible flood message from: " + color.clear + msg_sender)
                    return
                
                # Reset cooldown if the user hasn't sent a message in the last 5 seconds
                if current_time > cooldown + datetime.timedelta(seconds = 5):
                    self.global_cooldown[msg_sender]["messages"] = 0


        # Handle channel/private messages
        if (public_message or private_message) and len(msg_components) >= 3:
            sender_full_hostmask = message_data["nick"] + "!" + message_data["username"] + "@" + message_data["hostmask"]
            message_recipient = msg_components[2]
            msg_sender = message_data["nick"]

            if public_message and self._irc.channels.isConnectedTo(message_recipient):
                if self._irc.channels.isIgnoring(message_recipient):
                    log.info(color.b_red + "Ignoring message from ignored channel: " + color.clear + message_recipient)
                    return

            target = message_recipient
            if private_message:
                target = msg_sender

            msg_data = {"recipient":message_recipient,"message":msg_components[3:], "raw_message":" ".join(msg_components), "sender":msg_sender, "sender_hostmask":sender_full_hostmask, "message_type":message_type, "target":target, "time":message_data["time"]}
            if msg_data["message"][0].startswith(":"):
                msg_data["message"][0] = (msg_data["message"][0])[1:]

            # Check functions
            for func in self.functions_list:
                disabled = self.isFunctionDisabled(func)
                if "key" in func.type and func.hasKeyLockFor(target):
                    log.info(color.cyan + "Main function lock active" + color.clear)
                    func_exectuted = self.runFunction(func, msg_data, "key")
                    if func_exectuted:
                        return

                if "command" in func.type and len(msg_components) >= 4:
                    # Check if the message has a trigger and a subcommand or just a subcommand if its a PM
                    if (self._irc.channels.isConnectedTo(message_recipient) or private_message):
                        trigger_match = self.checkForTriggerMatch(msg_components,private_message)
                        if trigger_match:
                            message_command = trigger_match[0].lower()
                            msg_data["message"] = trigger_match[1]
                            msg_data["command"] = message_command
                            if message_command in func.commands:
                                if disabled:
                                    self._irc.sendMSG("%s function disabled by: %s - Expires in: %s" % (func.name ,disabled[0], timedstr(disabled[1])), self._bot.master_channel)
                                    # self._irc.sendMSG("Triggered by: '%s'" % msg_data["raw_message"], self._bot.master_channel)
                                    continue
                                if not func.restricted or (func.restricted and self._bot.isUserAuthed(sender_full_hostmask)):
                                    func_exectuted = self.runFunction(func, msg_data, "command")
                                    if func_exectuted and func.blocking:
                                        return
                                else: self._bot.notAllowedMessage(msg_data["sender"],message_recipient)

                if "natural" in func.type:
                    func_exectuted = self.runFunction(func, msg_data, "natural")
                    if func_exectuted and func.blocking:
                        return


        # Handle status messages
        else:
            msg_data = {"recipient":None,"message":msg_components[3:], "raw_message":" ".join(msg_components), "sender":None, "sender_hostmask":None, "message_type":message_type}
            # Check functions
            for func in self.functions_list:
                disabled = self.isFunctionDisabled(func)
                if "status" in func.type:
                    if disabled:
                        self._irc.sendMSG("%s function disabled by: %s - Expires in: %s" % (func.name ,disabled[0], timedstr(disabled[1])), self._bot.master_channel)
                        # self._irc.sendMSG("Triggered by: '%s'" % msg_data["raw_message"], self._bot.master_channel)
                        continue
                    func_exectuted = self.runFunction(func, msg_data, "status")
                    if func_exectuted and func.blocking:
                        return

    def runFunction(self, func, message_data, func_type):
        try:
            function_executed = func.main(self._bot, message_data, func_type)
            if function_executed and func.blocking:
                func.run_count = func.run_count + 1
                log.info(color.blue + "Blocking %s function executed: " % func_type + color.clear + func.name)
            elif function_executed:
                func.run_count = func.run_count + 1
                log.info(color.blue + "%s function executed: " % func_type.capitalize() + color.clear + func.name)

            if function_executed:
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

            self._irc.sendMSG("Failed to run function: %s%s%s - Trace index: %i" % (color.irc_blue, func.name, color.irc_clear, tb_index), self._bot.master_channel)
            self._irc.sendMSG(str(e), self._bot.master_channel)
            self._irc.sendMSG("Triggered by '%s'" % string.join(message_data["message"]), self._bot.master_channel)

            log.error(color.red + trace + color.clear)

    def checkForTriggerMatch(self, msg_components, private_message):
        message = msg_components[3:]
        if message[0].startswith(":"):
            message[0] = (message[0])[1:]

        if any(re.match("^:%s$" % re.escape(trigger), msg_components[3], re.IGNORECASE) for trigger in self._bot.triggers) and len(msg_components) >= 5:
            message_command = msg_components[4]
            return [message_command,msg_components[4:]]
        elif len(msg_components) >= 4:
            if re.match("^:%s.*?$" % re.escape(self._bot.short_trigger), msg_components[3], re.IGNORECASE):
                # Strip the short trigger
                message_command = (message[0])[len(self._bot.short_trigger):]
                message[0] = message_command
                return [message_command,message]
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
        return [function.disabled["disabled_by"], function.disabled["time"] - current_time]

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
            if re.match("^%s(\.py$|$)" % re.escape(function_name), function.name, re.IGNORECASE):
                return function
        return False


