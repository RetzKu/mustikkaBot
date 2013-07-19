#!/usr/bin/env python
#
# Main class for twitch/irc bot MustikkaBot
#
# Author: Esa Varemo
#

import re
import socket
import json
import threading
import sys
import os
import errno
import imp
from time import sleep

from logging import d, log

class botti:

    ircsock = None
    modules = {}

    def parse_config(self):
        try:
            settings_f = open("config.txt")
        except IOError:
            print("Config not found, please make a copy of \"config.txt.template\" as \"config.txt\"")
            sys.exit()

        host = None
        username = None
        passwd = None
        channel = None

        try:
            for line in settings_f:
                line = line.strip("\n\r")
                if line.find('host') != -1:
                    host = line.split(":")[1]
                if line.find('user') != -1:
                    username = line.split(":")[1]
                if line.find('pass') != -1:
                    passwd = line.split(":")[1]
                if line.find('chnl') != -1:
                    channel = line.split(":")[1]
        except IndexError:
            print("Malformed config file, please fix")
            sys.exit()

        settings_f.close()

        passwd_hidden = ""

        i = 0
        while i < len(passwd):
            passwd_hidden += "*"
            i += 1

        log("PARAMETERS: Host: %s, username: %s, password: %s, channel: %s" % (host, username, passwd_hidden, channel))
        return (host, username, passwd, channel)


    def connect(self, params):
            global ircsock
            
            ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            ircsock.connect((params[0], 6667))
            
            ircsock.setblocking(0)

            ircsock.send("Pass %s\n" % (params[2]))
            ircsock.send("NICK %s\n" % (params[1]))
            ircsock.send("JOIN %s\n" % (params[3]))

    def getData(self):
        global ircsock
        data = None
        
        try:
            data = ircsock.recv(1024)
            data = data.strip('\r\n')
            return data
        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                return "" # no data
                
        

    def loadModule(self, file):
        fpath = os.path.normpath(os.path.join(os.path.dirname(__file__), file))
        dir, fname = os.path.split(fpath)
        mname, ext = os.path.splitext(fname)

        (file, filename, data) = imp.find_module(mname, [dir])
        return imp.load_module(mname, file, filename, data)

    def getModules(self):        
        files = os.listdir("modules/")
        for file in files:
            if not file.find(".py") == -1:
                module = self.loadModule("modules/" + file)
                id = module.getId()
                self.modules[id] = module

    def initModules(self):
        for name, module in self.modules.iteritems():
            module.init()

    def main(self):
        settings = self.parse_config()

        self.getModules()
        self.initModules()

        try:
            self.connect(settings)
        except Exception as e:
            print e

        sleep(1)

        while True:
            ircmsg = self.getData()

            if not len(ircmsg) == 0:
                log(ircmsg)

                if ircmsg.find('PING ') != -1:
                    ircsock.send('PING :Pong\n')

                result = re.search(':(.*)!.* JOIN #herramustikka', ircmsg)
                if not result == None:
                    nick = result.group(1)
                    print("Found a viewer joining: " + nick + "\n")
                    msg = 'PRIVMSG #herramustikka :Tervetuloa ' + nick + "\n"
                    print("SENDING: " + msg)
                    #ircsock.send(msg)
                    
                if ircmsg.find(' PRIVMSG ') != -1:
                    nick = ircmsg.split('!')[0][1:]
                    msg = ircmsg.split(' PRIVMSG ')[-1].split(' :')[1]
b = botti()
b.main()
