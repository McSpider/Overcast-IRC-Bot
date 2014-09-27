#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, errno, threading
import traceback
import string, textwrap, re
import datetime
import select
import collections

from utils import *
from channels import *

import logging
log = logging.getLogger(__name__)


class irc:
    def __init__(self, delegate):
        self._socket = None;
        self.channels = channels(self)
        self._bot = delegate;

        self.ident = None
        self.password = None
        self.nick = None
        self.realname = None

        self.current_hostmask = ""

        self.server = None
        self.server_port = None

        self.nicklength = 20

        self.read_active = True # Setting this to False stops the read loop
        self.write_active = True
        self.poll_activity = True
        self.poll_activity_interval = 60 #seconds
        self.activity_timeout_count = 0

        self.log_pings = False

        self._message_queues = {}
        self._message_sent_times = {}
        # 'interval' time it waits until it starts sending again once the allotted 'amount' of messages have been sent.
        self.queue_info = {"IMPORTANT":{"priority":1, "interval":datetime.timedelta(seconds = 2), "amount":15}, "NORMAL":{"priority":0, "interval":datetime.timedelta(seconds = 3), "amount":5}}


    def connectToServer(self, server, port):
        log.info(color.b_blue + 'Connecting to server: ' + color.clear + server + ':' + str(port))
        self.server = server
        self.server_port = port
        self._socket = socket.socket()
        try:
            self._socket.connect((server, port))
        except socket.timeout:
            return False
        except Exception, e:
            trace = traceback.format_exc()
            log.error(color.red + trace + color.clear)
            return False

        # Continuously poll the message queues and send the messages if permitted
        important_queue_t = threading.Thread(target = self._sendQueuedMessageForQueue, args = ("IMPORTANT",))
        startThread(important_queue_t)
        normal_queue_t = threading.Thread(target = self._sendQueuedMessageForQueue, args = ("NORMAL",))
        startThread(normal_queue_t)
        return True

    def didJoinServer(self):
        # Send a WHOIS request for the bot to set self.current_hostmask
        # - While current_hostmask is not set the messages sent with sendMSG, sendNoticeMSG & sendActionMSG
        # - will not be split into lines properly and data may be lost
        self.sendRaw('WHOIS %s\r\n' % self.nick, "IMPORTANT")
        for channel in self._bot.autojoin_channels:
            self.channels.join(channel)


    def getMessageType(self, msg):
        # Add the ascii character 1 to the regex using %c
        if re.match("^:\S*? PRIVMSG (&|#|\+|!).* :%cACTION .*%c$" % (1,1), msg):
            return "CHANNEL_ACTION_MSG"
        elif re.match("^:\S*? PRIVMSG .* :%cACTION .*%c$" % (1,1), msg):
            return "ACTION_MSG"
        elif re.match("^:\S*? PRIVMSG .* :%c.*%c$" % (1,1), msg):
            return "CTCP_REQUEST"
        elif re.match("^:\S*? NOTICE .* :%c.*%c$" % (1,1), msg):
            return "CTCP_REPLY"
        elif re.match("^:\S*? PRIVMSG (&|#|\+|!).* :.*$", msg):
            return "CHANNEL_MSG"
        elif re.match("^:\S*? PRIVMSG .*:.*$", msg):
            return "QUERY_MSG"
        elif re.match("^:\S*? NOTICE .* :.*$", msg):
            return "NOTICE_MSG"
        elif re.match("^:\S*? INVITE .* .*$", msg):
            return "INVITE_NOTICE"
        elif re.match("^:\S*? JOIN .*$", msg):
            return "JOIN_NOTICE"
        elif re.match("^:\S*? TOPIC .* :.*$", msg):
            return "TOPICCHANGE_NOTICE"
        elif re.match("^:\S*? NICK :.*$", msg):
            return "NICKCHANGE_NOTICE"
        elif re.match("^:\S*? KICK .* .*$", msg):
            return "KICK_NOTICE"
        elif re.match("^:\S*? PART .*$", msg):
            return "PART_NOTICE"
        elif re.match("^:\S*? MODE .* .*$", msg):
            return "MODECHANGE_NOTICE"
        elif re.match("^:\S*? 001 .*? :.*$", msg):
            return "WELCOME"
        elif re.match("^:\S*? 002 .*? :.*$", msg):
            return "YOURHOST"
        elif re.match("^:\S*? 003 .*? :.*$", msg):
            return "CREATED"
        elif re.match("^:\S*? 004 .*$", msg):
            return "MYINFO"
        elif re.match("^:\S*? 005 .*? :Try server .*, port .*$", msg):
            return "BOUNCE"
        elif re.match("^:\S*? 005 .*? :.*$", msg):
            return "PROTO"
        
        elif re.match("^:\S*? 251 .* :.*$", msg):
            return "LUSERCLIENT"
        elif re.match("^:\S*? 252 .*? [0-9]+ :.*$", msg):
            return "LUSEROP"
        elif re.match("^:\S*? 253 .*? [0-9]+ :.*$", msg):
            return "LUSERUNKNOWN"
        elif re.match("^:\S*? 254 .*? [0-9]+ :.*$", msg):
            return "LUSERCHANNELS"
        elif re.match("^:\S*? 255 .* :.*$", msg):
            return "LUSERME"

        elif re.match("^:\S*? 265 .* :.*$", msg):
            return "LLOCALUSERS"
        elif re.match("^:\S*? 266 .* :.*$", msg):
            return "LGLOBALUSERS"
        elif re.match("^:\S*? 250 .* :Highest connection count:.*$", msg):
            return "STATSCONN"
        elif re.match("^:\S*? 250 .* :.*$", msg):
            return "STATSDLINE"

        elif re.match("^:\S*? 375 .* :.*$", msg):
            return "MOTDSTART"
        elif re.match("^:\S*? 372 .* :.*$", msg):
            return "MOTD"
        elif re.match("^:\S*? 376 .* :.*$", msg):
            return "ENDOFMOTD"

        elif re.match("^:\S*? 311 .* \* :.*$", msg):
            return "WHOISUSER"
        elif re.match("^:\S*? 312 .* :.*$", msg):
            return "WHOISSERVER"
        elif re.match("^:\S*? 313 .* :.*$", msg):
            return "WHOISOPERATOR"
        elif re.match("^:\S*? 317 .* :.*$", msg):
            return "WHOISIDLE"
        elif re.match("^:\S*? 318 .* :.*$", msg):
            return "ENDOFWHOIS"
        elif re.match("^:\S*? 319 .*? :.*$", msg):
            return "WHOISCHANNELS"

        elif re.match("^:\S*? 353 .*? :.*$", msg):
            return "NAMES_LIST"
        elif re.match("^:\S*? 366 .*? :.*$", msg):
            return "NAMES_LIST_END"

        elif re.match("^:\S*? 471 .*? :.*$", msg):
            return "CHANNELISFULL"
        elif re.match("^:\S*? 473 .*? :.*$", msg):
            return "INVITEONLYCHAN"
        elif re.match("^:\S*? 474 .*? :.*$", msg):
            return "BANNEDFROMCHAN"
        elif re.match("^:\S*? 475 .*? :.*$", msg):
            return "BADCHANNELKEY"
        elif re.match("^:\S*? 476 .*? :.*$", msg):
            return "BADCHANMASK"

        elif re.match("^:\S*? QUIT :.*$", msg):
            return "QUIT_NOTICE"
        elif re.match("^PING.*?$", msg):
            return "PING"
        elif re.match("^:\S*? PONG.*?$", msg):
            return "PONG"
        elif re.match("^ERROR.*?$", msg):
            return "ERROR"

        return "GENERIC_MESSAGE"

    def getMessageData(self, msg, type):
        if not msg:
            return

        msg_components = string.split(msg)
        message_data = {}

        prefix = None
        command = None
        params = None


        if msg_components[0][0] == ":":
            prefix = msg_components[0]

            username = None
            nick = None
            hostmask = None
            server = None

            if "!" in prefix and "@" in prefix:
                split = string.split(prefix,"!")
                nick = split[0]
                if nick.startswith(":"):
                    nick = nick[1:]

                split = string.split(split[1],"@")
                hostmask = split[1]
                username = split[0]
                message_data["nick"] = nick
                message_data["username"] = username
                message_data["hostmask"] = hostmask
            else:
                if type == "MODECHANGE_NOTICE":
                    nick = prefix
                    if nick.startswith(":"):
                        nick = nick[1:]
                    message_data["nick"] = nick
                else:
                    server = prefix
                    message_data["server"] = server

        return message_data


    def parseRawMessage(self, msg):
        self.last_activity = datetime.datetime.now()
        msg = string.rstrip(msg)
        message_type = self.getMessageType(msg)
        message_data = self.getMessageData(msg,message_type)
        message_data["time"] = self.last_activity
        if not (message_type == "PING" and not self.log_pings):
            log.info(color.cyan + str(self.last_activity) + " " + color.green + message_type.rjust(22," ") + " " + color.clear + repr(msg))
        
        msg_components = string.split(msg)

        if message_type == "NAMES_LIST":
            self.handleNamesListMessage(msg, msg_components, message_data)

        if message_type == "NAMES_LIST_END" and re.match("^:.* 366 %s .*:End of /NAMES.*$" % re.escape(self.nick), msg):
            self.channels.joinedTo(msg_components[3])

        if message_type == "KICK_NOTICE" and re.match("^:%s!.*$" % re.escape(self.nick), msg):
            self.channels.kickedFrom(msg_components[2])

        if message_type == "PART_NOTICE" and re.match("^:%s!.*$" % re.escape(self.nick), msg):
            self.channels.partedFrom(msg_components[2])

        if message_type == "PING" and len(msg_components) == 2:
            self.sendPingReply(msg_components[1])

        if message_type == "PROTO":
            self.handleProtoMessage(msg, msg_components, message_data)

        if message_type == "NOTICE_MSG" and re.match("^:NickServ!.*? NOTICE %s :.*identify via \x02/msg NickServ identify.*$" % re.escape(self.nick), msg):
            log.info(color.purple + 'Identify request recieved.' + color.clear)
            if self.password:
                self.sendMSG(('identify %s' % self.password),'NickServ')
            else:
                log.warning(color.red + 'No password specified, not authenticating.' + color.clear)

        if message_type == "WHOISUSER":
            if msg_components[2] == self.nick:
                self.current_hostmask = msg_components[3] + "!" + msg_components[4] + "@" + msg_components[5]
                log.debug("IRC connection hostmask: " + color.purple + self.current_hostmask + color.clear)

        if message_type == "MODECHANGE_NOTICE":
            self.handleModeChangeMessage(msg, msg_components, message_data)

        if message_type == "ERROR":
            timeout_match = re.match("^ERROR :Closing Link: (?P<ip>\S*?) \(Ping timeout: (?P<timeout>\S*?) seconds\)$", msg)
            if timeout_match:
                log.debug("IRC connection timed out with IP: %s%s%s (timeout %s%s%s seconds) " % (color.purple,timeout_match.group('ip'),color.clear,color.red,timeout_match.group('timeout'),color.clear))
                self._bot.disconnected_errno = errno.ECONNRESET

        self._bot.parseMessage(msg_components, message_type, message_data)


    def handleModeChangeMessage(self, msg, msg_components, message_data):
        if (msg == ":" + self.nick + " MODE " + self.nick + " :+i"):
            log.info(color.bold + "Overcast IRC Bot - Connected to IRC server\n" + color.clear)
            self.didJoinServer()

        if re.match("^:\S*? MODE .* \+o %s$" % re.escape(self.nick), msg):
            channel = msg_components[2]
            log.info(color.b_purple + "Oped in channel: " + color.clear + channel)
            self.channels.flagIn("o", channel, True)
        if re.match("^:\S*? MODE .* \-o %s$" % re.escape(self.nick), msg):
            channel = msg_components[2]
            log.info(color.b_purple + "De-Oped in channel: " + color.clear + channel)
            self.channels.flagIn("o", channel, False)

        if re.match("^:\S*? MODE .* \+v %s$" % re.escape(self.nick), msg):
            channel = msg_components[2]
            log.info(color.b_purple + "Voiced in channel: " + color.clear + channel)
            self.channels.flagIn("v", channel, True)
        if re.match("^:\S*? MODE .* \-v %s$" % re.escape(self.nick), msg):
            channel = msg_components[2]
            log.info(color.b_purple + "De-Voiced in channel: " + color.clear + channel)
            self.channels.flagIn("v", channel, False)

        # MODECHANGE_NOTICE ':khazhyk!~khazhy@do-ny2-1.khaz.io MODE #overcastnetwork +b nixter1029!*@*'

        if re.match("^:\S*? MODE .* \+b \S*$", msg):
            channel = msg_components[2]
            user = msg_components[4]
            log.info("User " + color.yellow + user + color.clear + " banned in channel: " + color.blue + channel + color.clear)
        if re.match("^:\S*? MODE .* \-b \S*$", msg):
            channel = msg_components[2]
            user = msg_components[4]
            log.info("User " + color.yellow + user + color.clear + " unbanned in channel: " + color.blue + channel + color.clear)

        # MODECHANGE_NOTICE ':McSpider!~McSpider@72.14.188.239 MODE ##mcspider +q Overcast!*@*'
        if re.match("^:\S*? MODE .* \+q \S*$", msg):
            channel = msg_components[2]
            user = msg_components[4]
            log.info("User " + color.yellow + user + color.clear + " muted in channel: " + color.blue + channel + color.clear)
        if re.match("^:\S*? MODE .* \-q \S*$", msg):
            channel = msg_components[2]
            user = msg_components[4]
            log.info("User " + color.yellow + user + color.clear + " unmuted in channel: " + color.blue + channel + color.clear)

    def handleNamesListMessage(self, msg, msg_components, message_data):
        names_match = re.match("^:(?P<server>\S*?) 353 %s = (?P<channel>\S*?) :(?P<users>.*?)$" % re.escape(self.nick), msg)
        server = names_match.group('server')
        channel = names_match.group('channel')
        users = names_match.group('users')

        if channel in self.channels.list:
            for user in string.split(users, " "): ## parseUser(user)
                self.channels.list[channel].users[user] = user

        log.debug("Users in channel: " + color.purple + channel + color.clear + " From server: " + color.purple + server + color.clear)
        log.debug(string.split(users, " "))

    def handleProtoMessage(self, msg, msg_components, message_data):
        irc_chantypes = re.search("CHANTYPES=(\S*)", msg)
        if irc_chantypes:
            irc_chantypes = irc_chantypes.group(1)
            self.channels.chantypes = list(irc_chantypes)
            log.debug("IRC channel types: " + color.purple + irc_chantypes + color.clear)

        irc_nicklength = re.search("NICKLEN=(\S*)", msg)
        if irc_nicklength:
            irc_nicklength = irc_nicklength.group(1)
            self.nicklength = irc_nicklength
            log.debug("IRC max nickname length: " + color.purple + irc_nicklength + color.clear)

        irc_chanlength = re.search("CHANNELLEN=(\S*)", msg)
        if irc_chanlength:
            irc_chanlength = irc_chanlength.group(1)
            log.debug("IRC max channel name length: " + color.purple + irc_chanlength + color.clear)

        irc_topiclength = re.search("TOPICLEN=(\S*)", msg)
        if irc_topiclength:
            irc_topiclength = irc_topiclength.group(1)
            log.debug("IRC max topic length: " + color.purple + irc_topiclength + color.clear)

        irc_userprefix = re.search("PREFIX=(\S*)", msg)
        if irc_userprefix:
            irc_userprefix = string.split(irc_userprefix.group(1).lstrip("("), ")")
            irc_userprefixkeys = list(irc_userprefix[0])
            irc_userprefixvalues = list(irc_userprefix[1])
            irc_userprefix = dict(zip(irc_userprefixkeys, irc_userprefixvalues))
            log.debug("IRC user prefixes: " + color.purple + str(irc_userprefix) + color.clear)

    def read(self):
        # Start polling our active state
        self.last_activity = datetime.datetime.now()
        t = threading.Thread(target = self._pollActiveState)
        startThread(t)

        readbuffer = ""
        # Loop till the readbuffer is nil (i.e. the socket is disconnected)
        while self.read_active == True:
            socket_status = select.select([self._socket], [], [], 2)
            
            if socket_status[0]: # If the socket has data to parse
                try:
                    readdata = self._socket.recv(512)
                    try:
                        readbuffer = readbuffer + readdata
                    except Exception, e:
                        trace = traceback.format_exc()
                        log.error(color.red + trace + color.clear)
                except socket.error as e:
                    trace = traceback.format_exc()
                    log.error(color.red + trace + color.clear)

                    self._bot.disconnected_errno = e.errno
                    self.read_active = False


                if not readbuffer: break

                temp = string.split(readbuffer, "\n")
                readbuffer = temp.pop( )
                
                for msg in temp:
                    msg.strip()
                    t = threading.Thread(target = self.parseRawMessage, args = (msg,))
                    startThread(t)

        self.poll_activity = False

    def disconnect(self):
        self.write_active = False
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except Exception, e:
            if e.errno != errno.ENOTCONN:
                trace = traceback.format_exc()
                log.error(color.red + trace + color.clear)

        self._socket.close()

    def quit(self,message="And the sun shines once again."):
        log.info(color.bold + 'Overcast IRC Bot - Quitting with message: "%s"\n' % message + color.clear)
        self._bot.intentional_disconnect = True;
        self.sendRaw("QUIT :%s \r\n" % message, "IMPORTANT")


    def authUser(self, username, nick, realname, password):
        log.info(color.blue + 'IRC Login Info: ' + color.clear + username + ' | ' + realname)
        log.info(color.blue + 'IRC Nick: ' + color.clear + nick + '\n')

        if not password or len(password) < 1:
            log.warning(color.red + 'No password specified for authentication.\n' + color.clear)

        self.sendRaw('USER %s %s %s \r\n' % (username, " 0 * :", realname), "IMPORTANT")
        self.sendRaw('NICK %s\r\n' % nick, "IMPORTANT")

        self.ident = username
        self.nick = nick
        self.realname = realname
        self.password = password


    def sendRaw(self, message, priority = "NORMAL"):
        #log.debug(color.blue + 'Sending raw string: ' + color.clear + message)
        self.addMessageToQueue(message, priority)

    # Sends a PRIVMSG message split into lines equal to or less than 512 characters
    # - NOTE: The line split length is incorrect until self.current_hostmask is correctly set
    def sendMSG(self, message, recipient, priority = "NORMAL"):
        message = message.replace("\n"," ").replace("\r","")
        if recipient == None:
            log.warning(color.red + 'Send MSG Error: No message recipient specified! ' + color.clear)
            return

        log.info(color.blue + '@ Adding message to queue: ' + color.clear + message + color.blue + ' Recipient: '+ color.clear + recipient)
        msg_content_len = 512 - len(": %s PRIVMSG %s :\r\n" % (self.current_hostmask, recipient))
        message_lines = textwrap.wrap(message, msg_content_len)

        for line in message_lines:
            message_to_send = "PRIVMSG %s :%s\r\n" % (recipient, line)
            self.sendRaw(message_to_send, priority)

    # Sends a NOTICE message split into lines equal to or less than 512 characters
    # - NOTE: The line split length is incorrect until self.current_hostmask is correctly set
    def sendNoticeMSG(self, message, recipient, priority = "NORMAL"):
        message = message.replace("\n"," ").replace("\r","")
        if recipient == None:
            log.warning(color.red + 'Send Notice Error: No message recipient specified! ' + color.clear)
            return

        log.info(color.blue + '@ Adding notice message to queue: ' + color.clear + message + color.blue + ' Recipient: '+ color.clear + recipient)
        msg_content_len = 512 - len(": %s NOTICE %s :\r\n" % (self.current_hostmask, recipient))
        message_lines = textwrap.wrap(message, msg_content_len)

        for line in message_lines:
            message_to_send = "NOTICE %s :%s\r\n" % (recipient, line)
            self.sendRaw(message_to_send, priority)

    # Sends a ACTION message split into lines equal to or less than 512 characters
    # - NOTE: The line split length is incorrect until self.current_hostmask is correctly set
    def sendActionMSG(self, message, recipient, priority = "NORMAL"):
        message = message.replace("\n"," ").replace("\r","")
        if recipient == None:
            log.warning(color.red + 'Send Action Error: No message recipient specified! ' + color.clear)
            return

        log.info(color.blue + '@ Adding action message to queue: ' + color.clear + message + color.blue + ' Recipient: '+ color.clear + recipient)
        msg_content_len = 512 - len(": %s PRIVMSG %s :%cACTION %c\r\n" % (self.current_hostmask, recipient, 1, 1))
        message_lines = textwrap.wrap(message, msg_content_len)

        for line in message_lines:
            message_to_send = "PRIVMSG %s :%cACTION %s%c\r\n" % (recipient, 1, line, 1)
            self.sendRaw(message_to_send, priority)


    def sendPingReply(self, server):
        if self.log_pings:
            log.debug(color.blue + 'Sending ping reply: ' + color.clear + server)

        message = "PONG %s\r\n" % server
        self.sendRaw(message, "IMPORTANT")



    # Periodically check if there has been any activity in the last X minutes
    # - If there is no activity try to ping ourselves to force some activity.
    # - If there is no response to our ping try again and if it fails assume that the connection is gone.
    def _pollActiveState(self):
        activity_interval = datetime.timedelta(minutes = 3)

        if self.poll_activity:
            time_now = datetime.datetime.now()
            if self.last_activity < time_now - activity_interval:
                self.activity_timeout_count += 1
                if self.activity_timeout_count > 1:
                    log.warning(color.red + 'Activity timeout. Disconnecting! ' + color.clear)
                    self._bot.disconnected_errno = errno.ECONNRESET # errno.EHOSTUNREACH
                    self.read_active = False
                    return

                log.info(color.red + 'No activity in last 3 minutes.' + color.clear)
                log.info(color.blue + 'Forcing activity, sending ping to: ' + color.clear + self.nick)
                self.sendRaw("PING %s\r\n" % self.nick, "IMPORTANT")
            else:
                self.activity_timeout_count = 0

            threading.Timer(self.poll_activity_interval, self._pollActiveState).start()


    def addMessageToQueue(self, message, queue = "NORMAL"):
        if not queue in self.queue_info: # No queue with that name found use NORMAL queue
            log.warning(color.red + 'No queue found with name "' + color.clear + str(queue) + color.red + '" setting to NORMAL queue.' + color.clear)
            queue = "NORMAL"

        if queue in self._message_queues:
            self._message_queues[queue].append(message)
        else:
            self._message_queues[queue] = [message]



    def _sendQueuedMessageForQueue(self, queue):
        if queue in self._message_queues and len(self._message_queues[queue]) > 0:
            if self._socket and self.write_active:
                    if not self.queueMessageFor(queue):
                        self._message_sent_times[queue].append(datetime.datetime.now())

                        message = self._message_queues[queue].pop(0)
                        try:
                            self._socket.send(message)
                        except Exception, e:
                            trace = traceback.format_exc()
                            log.error(color.red + trace + color.clear)
        
            elif not self.write_active: # No write active, remove all queued messages
                messages = self._message_queues[queue]
                self._message_queues[queue] = []
                for message in messages:
                    log.debug(color.yellow + "Removed Queued Message: " + color.clear + message)

        if self.write_active:
            threading.Timer(0.1, self._sendQueuedMessageForQueue, [queue]).start()


    def queueMessageFor(self, queue):
        if not queue in self.queue_info: # No queue info available do not throttle
            log.warning(color.red + 'No queue found with name: ' + color.clear + str(queue))
            return False

        if not queue in self._message_sent_times: # no messages for queue exist
            self._message_sent_times[queue] = collections.deque(maxlen=10)
            return False

        interval = self.queue_info[queue]["interval"]
        amount = self.queue_info[queue]["amount"]

        if len(self._message_sent_times[queue]) < amount:
            return False
        else:
            time_now = datetime.datetime.now()
            time_nth_message = self._message_sent_times[queue][-amount]

            if (time_now - time_nth_message) < interval:
                return True

        return False


