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

    irc_white = '\x03' + '0'
    irc_black = '\x03' + '1'
    irc_darkblue = '\x03' + '2'
    irc_darkgreen = '\x03' + '3'
    irc_red = '\x03' + '4'
    irc_darkred = '\x03' + '5'
    irc_darkviolet = '\x03' + '6'
    irc_orange = '\x03' + '7'
    irc_yellow = '\x03' + '8'
    irc_lightgreen = '\x03' + '9'
    irc_cyan = '\x03' + '10'
    irc_lightcyan = '\x03' + '11'
    irc_blue = '\x03' + '12'
    irc_violet = '\x03' + '13'
    irc_darkgrey = '\x03' + '14'
    irc_lightgrey = '\x03' + '15'

    irc_bold = '\x02'
    irc_italic = '\x09'
    irc_underline = '\x15'
    irc_clear = '\x0f'