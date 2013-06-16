#!/usr/bin/env python
import socket, threading
import string, re
import datetime

from utils import *
from channels import *


class irc:
    def __init__(self, delegate):
        self._socket = socket.socket()
        self._channels = channels(self)
        self._delegate = delegate;

    def connectToServer(self, server, port):
        print color.b_blue + 'Connecting to server: ' + color.clear + server + ':' + str(port)
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
        elif re.match("^:.*? QUIT :.*$", msg):
            return "QUIT_NOTICE"
        elif re.match("^PING.*?$", msg):
            return "PING"

        return "GENERIC_MESSAGE"

    def parseRawMessage(self, msg):
        msg = string.rstrip(msg)
        messageType = self.getMessageType(msg)
        if config.debug: print color.cyan + str(datetime.datetime.now()) + " " + color.green + messageType + " " + color.clear + msg
        else: print msg
        
        msgComponents = string.split(msg)
        if re.match("^.* 366 %s .*:End of /NAMES.*$" % (config.nick), msg):
            self._channels.joinedTo(msgComponents[3])
        if (messageType == "KICK_NOTICE") and re.match("^.*%s.*$" % (config.nick), msg):
            self._channels.kickedFrom(msgComponents[2])

        if (messageType == "PING") and len(msgComponents) == 2:
            self.sendPingReply(msgComponents[1])

        if (messageType == "PING") and len(msgComponents) == 2:
            self.sendPingReply(msgComponents[1])

        if (messageType == "MODECHANGE_NOTICE"):
            if (msg == ":" + config.nick + " MODE " + config.nick + " :+i"):
                print color.b_cyan + "Overcast IRC Bot - Connected to irc server\n" + color.clear
                for channel, data in config.channels.items():
                    self._channels.join(channel)

            #:McSpider!~McSpider@192.65.241.17 MODE ##mcspider +o Overcast1
            if re.match("^:.*? MODE .* \+o %s$" % config.nick, msg):
                channel = msgComponents[2]
                print color.b_purple + "Oped in channel: " + color.clear + channel
                self._channels.setOpedInChannel(channel,True)

        self._delegate.parseMessage(msgComponents, messageType)


    def read(self):
        readbuffer = ""
        while 1:
            readbuffer = readbuffer+self._socket.recv(1024)
            if not readbuffer: break

            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop( )
            
            for msg in temp:
                msg.strip()
                t = threading.Thread(target = self.parseRawMessage, args = (msg,))
                startThread(t)

    def disconnect(self):
        # Check if the socket is still receving data, and if it is shut it down
        if self._socket.recv(128): self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def quit(self):
        print color.b_cyan + 'Overcast IRC Bot - Quitting\n' + color.clear
        self.sendRaw("QUIT :%s \r\n" % "And the sun shines once again.")


    def authUser(self, username, nick, realname, password):
        print color.blue + 'IRC Login Info: ' + color.clear + username + ' | ' + realname + ' | ' + password 
        print color.blue + 'IRC Nick: ' + color.clear + nick + '\n'

        self.sendRaw('USER %s %s %s \r\n' % (username, " 0 * :", realname))
        self.sendRaw('NICK %s\r\n' % nick)

        if password:
            self.sendRaw(('PASS %s \r\n' % password))
            self.sendMSG(('identify %s' % password),'NickServ')
        else:
            print color.red + 'No password specified, not authenticating.' + color.clear


    def sendRaw(self, message):
        #print color.blue + 'Sending raw string: ' + color.clear + message
        self._socket.send(message)

    def sendMSG(self, message, recipient):
        if recipient == None:
            print color.red + 'No message recipient specified! ' + color.clear
        print color.blue + 'Sending message: ' + color.clear + message + color.blue + ' Recipient: '+ color.clear + recipient
        self._socket.send("PRIVMSG %s :%s\r\n" % (recipient, message))

    def sendPingReply(self, server): 
        print color.blue + 'Sending ping reply: ' + color.clear + server
        self.sendRaw("PONG %s\r\n" % server)


