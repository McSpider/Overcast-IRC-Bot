#!/usr/bin/env python

def startThread(thread):
    thread.daemon = True
    thread.start()
    thread.join()

class color():
    red = '\033[0;31m'
    b_red = '\033[1;31m'
    green = '\033[0;32m'
    b_green = '\033[1;32m'
    blue = '\033[0;34m'
    b_blue = '\033[1;34m'
    purple = '\033[0;35m'
    b_purple = '\033[1;35m'
    cyan = '\033[0;36m'
    b_cyan = '\033[1;36m'
    clear = '\033[0m'

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

    # irc_bold = '\x02'
    # irc_italic = '\x09'
    # irc_underline = '\x15'
    irc_clear = '\x0f'
