#!/usr/bin/env python
import socket, threading
import string, re
import datetime
import select

from utils import *
from channels import *


class irc:
    def __init__(self, delegate):
        self._socket = socket.socket()
        self._channels = channels(self)
        self._bot = delegate;

        self.ident = None
        self.password = None
        self.nick = None
        self.realname = None

        self.server = None
        self.serverPort = None

        self.read_active = True
        self.poll_activity = True
        self.poll_activity_interval = 60
        self.activity_timeout_count = 0
        # Periodically check if there has been any activity in the last X minutes
        # If there is no activity try to ping ourselves to force some activity.
        # If there is no response to our ping try again and if it fails assume that the connection is gone. 


    def connectToServer(self, server, port):
        print color.b_blue + 'Connecting to server: ' + color.clear + server + ':' + str(port)
        self.server = server
        self.serverPort = port
        self._socket.connect((server, port))
    

    def getMessageType(self,msg):
        # Add the ascii character 1 to the regex using %c
        if re.match("^:.*? PRIVMSG (&|#|\+|!).* :%cACTION .*%c$" % (1,1), msg):
            return "CHANNEL_ACTION_MSG"
        elif re.match("^:.*? PRIVMSG .* :%cACTION .*%c$" % (1,1), msg):
            return "ACTION_MSG"
        elif re.match("^:.*? PRIVMSG .* :%c.*%c$" % (1,1), msg):
            return "CTCP_REQUEST"
        elif re.match("^:.*? NOTICE .* :%c.*%c$" % (1,1), msg):
            return "CTCP_REPLY"
        elif re.match("^:.*? PRIVMSG (&|#|\+|!).* :.*$", msg):
            return "CHANNEL_MSG"
        elif re.match("^:.*? PRIVMSG .*:.*$", msg):
            return "QUERY_MSG"
        elif re.match("^:.*? NOTICE .* :.*$", msg):
            return "NOTICE_MSG"
        elif re.match("^:.*? INVITE .* .*$", msg):
            return "INVITE_NOTICE"
        elif re.match("^:.*? JOIN .*$", msg):
            return "JOIN_NOTICE"
        elif re.match("^:.*? TOPIC .* :.*$", msg):
            return "TOPICCHANGE_NOTICE"
        elif re.match("^:.*? NICK :.*$", msg):
            return "NICKCHANGE_NOTICE"
        elif re.match("^:.*? KICK .* .*$", msg):
            return "KICK_NOTICE"
        elif re.match("^:.*? PART .*$", msg):
            return "PART_NOTICE"
        elif re.match("^:.*? MODE .* .*$", msg):
            return "MODECHANGE_NOTICE"
        elif re.match("^:.*? 353 .*? :.*$", msg):
            return "NAMES_LIST"
        elif re.match("^:\S*? QUIT :.*$", msg):
            return "QUIT_NOTICE"
        elif re.match("^PING.*?$", msg):
            return "PING"

        return "GENERIC_MESSAGE"

    def getMessageData(self, msg, type):
        if not msg:
            return

        msgComponents = string.split(msg)
        messageData = {}

        prefix = None
        command = None
        params = None


        if msgComponents[0][0] == ":":
            prefix = msgComponents[0]

            username = None
            nick = None
            hostmask = None
            server = None

            if "!" in prefix and "@" in prefix:
                split = string.split(prefix,"!")
                nick = split[0]

                split = string.split(split[1],"@")
                hostmask = split[1]
                username = split[0]
                messageData["nick"] = nick
                messageData["username"] = username
                messageData["hostmask"] = hostmask
            else:
                if type == "MODECHANGE_NOTICE":
                    nick = prefix
                    messageData["nick"] = nick
                else:
                    server = prefix
                    messageData["server"] = server

        return messageData


    def parseRawMessage(self, msg):
        self.lastActivity = datetime.datetime.now()
        msg = string.rstrip(msg)
        messageType = self.getMessageType(msg)
        messageData = self.getMessageData(msg,messageType)
        if self._bot.debug: print color.cyan + str(self.lastActivity) + " " + color.green + messageType + " " + color.clear + repr(msg)
        else: print msg
        
        msgComponents = string.split(msg)
        if re.match("^.* 366 %s .*:End of /NAMES.*$" % re.escape(self.nick), msg):
            self._channels.joinedTo(msgComponents[3])
        if (messageType == "KICK_NOTICE") and re.match("^.*%s.*$" % re.escape(self.nick), msg):
            self._channels.kickedFrom(msgComponents[2])

        if (messageType == "PING") and len(msgComponents) == 2:
            self.sendPingReply(msgComponents[1])

        if messageType == "NOTICE_MSG" and re.match("^:NickServ!.*? NOTICE %s :.*identify via \x02/msg NickServ identify.*$" % re.escape(self.nick), msg):
            print color.purple + 'Identify request recieved.' + color.clear
            if self.password:
                self.sendMSG(('identify %s' % self.password),'NickServ')
            else:
                print color.red + 'No password specified, not authenticating.' + color.clear

        if (messageType == "MODECHANGE_NOTICE"):
            if (msg == ":" + self.nick + " MODE " + self.nick + " :+i"):
                print color.b_cyan + "Overcast IRC Bot - Connected to irc server\n" + color.clear
                for channel in self._bot.autojoin_channels:
                    self._channels.join(channel)

            if re.match("^:.*? MODE .* \+o %s$" % re.escape(self.nick), msg):
                channel = msgComponents[2]
                print color.b_purple + "Oped in channel: " + color.clear + channel
                self._channels.flagIn("o",channel,True)
            if re.match("^:.*? MODE .* \-o %s$" % re.escape(self.nick), msg):
                channel = msgComponents[2]
                print color.b_purple + "De-Oped in channel: " + color.clear + channel
                self._channels.flagIn("o",channel,False)

            if re.match("^:.*? MODE .* \+v %s$" % re.escape(self.nick), msg):
                channel = msgComponents[2]
                print color.b_purple + "Voiced in channel: " + color.clear + channel
                self._channels.flagIn("v",channel,True)
            if re.match("^:.*? MODE .* \-v %s$" % re.escape(self.nick), msg):
                channel = msgComponents[2]
                print color.b_purple + "De-Voiced in channel: " + color.clear + channel
                self._channels.flagIn("v",channel,False)


        self._bot.parseMessage(msgComponents, messageType, messageData)


    def read(self):
        # Start polling our active state
        self.lastActivity = datetime.datetime.now()
        t = threading.Thread(target = self.pollActiveState)
        startThread(t)

        readbuffer = ""
        # Loop till the readbuffer is nil (i.e. the socket is disconnected)
        while self.read_active == True:
            try:
                read_status = select.select([self._socket], [], [], 2)
            except Exception, e:
                trace = traceback.format_exc()
                print color.red + trace + color.clear
                break;

            if read_status[0]:
                readbuffer = readbuffer+self._socket.recv(512)
                if not readbuffer: break

                temp = string.split(readbuffer, "\n")
                readbuffer = temp.pop( )
                
                for msg in temp:
                    msg.strip()
                    t = threading.Thread(target = self.parseRawMessage, args = (msg,))
                    startThread(t)

        self.poll_activity = False

    def disconnect(self):
        # Check if the socket is still receving data, and if it is shut it down
        # read_status = select.select([self._socket], [], [], 2)
        # if read_status[0]:
        #     self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def quit(self,message="And the sun shines once again."):
        print color.b_cyan + 'Overcast IRC Bot - Quitting "%s"\n' % message.decode('utf-8') + color.clear
        self._bot.intentionalDisconnect = True;
        self.sendRaw("QUIT :%s \r\n" % message)


    def authUser(self, username, nick, realname, password):
        print color.blue + 'IRC Login Info: ' + color.clear + username + ' | ' + realname + ' | ' + password 
        print color.blue + 'IRC Nick: ' + color.clear + nick + '\n'

        self.sendRaw('USER %s %s %s \r\n' % (username, " 0 * :", realname))
        self.sendRaw('NICK %s\r\n' % nick)

        self.ident = username
        self.nick = nick
        self.realname = realname
        self.password = password


    def sendRaw(self, message):
        #print color.blue + 'Sending raw string: ' + color.clear + message
        if len(message) > 512:
            print color.blue + 'Send Raw Warning: Message to long, trimming to 512 chars. (length %s)' % len(message) + color.clear + message
            message = message[:510] + "\r\n"
        
        self._socket.send(message)

    def sendMSG(self, message, recipient):
        if recipient == None:
            print color.red + 'Send MSG Error: No message recipient specified! ' + color.clear
        print color.blue + '@ Sending message: ' + color.clear + message.decode('utf-8') + color.blue + ' Recipient: '+ color.clear + recipient.decode('utf-8')
        
        message = "PRIVMSG %s :%s\r\n" % (recipient, message)
        self.sendRaw(message)

    def sendNoticeMSG(self, message, recipient):
        if recipient == None:
            print color.red + 'Send Notice Error: No message recipient specified! ' + color.clear
        print color.blue + '@ Sending notice message: ' + color.clear + message.decode('utf-8') + color.blue + ' Recipient: '+ color.clear + recipient.decode('utf-8')
        
        message = "NOTICE %s :%s\r\n" % (recipient, message)
        self.sendRaw(message)

    def sendActionMSG(self, message, recipient):
        if recipient == None:
            print color.red + 'Send Action Error: No message recipient specified! ' + color.clear
        print color.blue + '@ Sending action message: ' + color.clear + message.decode('utf-8') + color.blue + ' Recipient: '+ color.clear + recipient.decode('utf-8')
        
        message = "PRIVMSG %s :%cACTION %s%c\r\n" % (recipient, 1, message, 1)
        self.sendRaw(message)

    def sendPingReply(self, server):
        print color.blue + 'Sending ping reply: ' + color.clear + server

        message = "PONG %s\r\n" % server
        self.sendRaw(message)


    # def voiceUser(self, username, channel, auto_voice):


    # def userIsVoiced(self, username, channel, recursive):



    def pollActiveState(self):
        if self.poll_activity:
            time_now = datetime.datetime.now()
            # if self._bot.debug: print color.blue + 'Checking for activity timeout, last activity: ' + color.clear + str(self.lastActivity)
            if self.lastActivity < time_now - datetime.timedelta(minutes = 2):
                self.activity_timeout_count += 1
                if self.activity_timeout_count > 1:
                    print color.red + 'Activity timeout. Disconnecting! ' + color.clear
                    self.read_active = False
                    return

                print color.red + 'No activity in last 2 minutes.' + color.clear
                print color.blue + 'Forcing activity, sending ping to: ' + color.clear + self.nick
                self.sendRaw("PING %s\r\n" % self.nick)
            else:
                self.activity_timeout_count = 0

            threading.Timer(self.poll_activity_interval, self.pollActiveState).start()





