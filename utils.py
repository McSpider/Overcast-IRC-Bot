#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


# Setup logging, probably should use a rotating log file with a size limit
# - Accepts two logging levels, one for the log file and the other for the console
def setupLogging(log_level, console_level):
    logging.basicConfig(level=log_level,
                        format='%(asctime)s: %(lineno)4d:%(name)-20s %(levelname)+8s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='bot.log',
                        filemode='w')
    c_handler = logging.StreamHandler()
    c_handler.setLevel(console_level)
    c_formatter = logging.Formatter('%(name)-20s %(levelname)+8s: %(message)s')
    c_handler.setFormatter(c_formatter)
    logging.getLogger('').addHandler(c_handler)


def startThread(thread, daemon = True, join = False):
    thread.daemon = daemon
    thread.start()
    if join == True:
        thread.join()

class color():
    red = '\033[0;31m'
    b_red = '\033[1;31m'
    green = '\033[0;32m'
    b_green = '\033[1;32m'
    yellow = '\033[0;33m'
    b_yellow = '\033[1;33m'
    blue = '\033[0;34m'
    b_blue = '\033[1;34m'
    purple = '\033[0;35m'
    b_purple = '\033[1;35m'
    cyan = '\033[0;36m'
    b_cyan = '\033[1;36m'
    clear = '\033[0m'
    bold = '\033[1m'

    irc_boldwhite = '\x03' + '00'
    irc_black = '\x03' + '01'
    irc_blue = '\x03' + '02'
    irc_green = '\x03' + '03'
    irc_boldred = '\x03' + '04'
    irc_red = '\x03' + '05'
    irc_violet = '\x03' + '06'
    irc_yellow = '\x03' + '07'
    irc_boldyellow = '\x03' + '08'
    irc_boldgreen = '\x03' + '09'
    irc_cyan = '\x03' + '10'
    irc_boldcyan = '\x03' + '11'
    irc_boldblue = '\x03' + '12'
    irc_boldviolet = '\x03' + '13'
    irc_boldblack = '\x03' + '14'
    irc_white = '\x03' + '15'

    irc_bold = '\x02'
    irc_italic = '\x09'
    irc_underline = '\x15'
    irc_clear = '\x0f'

    # Underline2 = 0x1f
    # Reverse = 0x16
    # StrikeThrough = 0x13


def timedstr(delta, short = False):
    s = delta.seconds
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)

    output = ""

    days = delta.days
    if days > 1: output += "%i days" % days
    elif days == 1: output += "%i day" % days

    if days > 0 and (hours > 0 or minutes > 0 or seconds > 0):
        output += ", "

    if hours > 1: output += "%i%s " % (hours, "h" if short else " hours")
    elif hours == 1: output += "%i%s " % (hours, "h" if short else " hour")
    if minutes > 1: output += "%i%s " % (minutes, "m" if short else " minutes")
    elif minutes == 1: output += "%i%s " % (minutes, "m" if short else " minute")

    if seconds == 1: output += "%i%s " % (seconds, "s" if short else " second")
    elif seconds > 1 or (seconds == 0 and hours == 0 and minutes == 0 and days == 0): output += "%i%s " % (seconds, "s" if short else " seconds")

    return output

def strFromBool(boolean):
    return "Yes" if boolean else "No"

