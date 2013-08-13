import json
import errno

import tools
from log import log

class commands:
    bot = None

    commands = []
    jsonfile = "commands.json"

    def init(self, bot):
        self.bot = bot
        self.readJSON()
        bot.eventlistener.registerMessage(self)
        log("[COMMANDS] Init complete")

    def handleMessage(self, data, user, msg):
        msg = tools.stripPrefix(msg)
        args = msg.split()

        if args[0] == "!commands":
            self.setupCommands(user, args)
        else:
            self.runCommands(user, args)

    def setupCommands(self, user, args):
        if len(args) > 1:
            if args[1] == "list":
                self.listCommands()

            if args[1] == "add":
                self.addCommand(args)

            if args[1] == "set":
                self.setCommand(args)

            if args[1] == "remove":
                self.removeCommand(args)

    def runCommands(self, user, args):
        for command in self.commands:
            if "!" + command['name'] == args[0]:
                self.runCommand(command, args, user)

    def runCommand(self, command, args, user):
        if self.bot.accessmanager.isInAcl(user, "commands.!" + command['name']):
            self.bot.sendMessage(command['value'])
            log("[COMMANDS] Running command " + command['name'] + ": " + command['value'])

    def readJSON(self):
        jsondata = ""
        try:
            file = open(self.jsonfile, "r")
            jsondata = file.read()
            file.close()
        except IOError as e:
            if e.errno == errno.ENOENT:
                log("[COMMANDS] file does not exist, creating")
                self.writeJSON()

        try:
            self.commands = json.loads(jsondata)
        except ValueError:
            log("[COMMANDS] commands-file malformed")

    def writeJSON(self):
        file = open(self.jsonfile, "w")
        data = json.dumps(self.commands, sort_keys=True, indent=4, separators=(',', ': '))
        file.write(data)
        file.close()

    def existsCommand(self, cmd):
        """
        :param cmd: Name of a command
        :type cmd: str
        :return: does command exist
        :rtype: bool

        Check if a command exists
        """
        for command in self.commands:
            if command == cmd:
                return True
        return False

    def addCommand(self, args):
        cmd = args[2]

        if not self.existsCommand(cmd):
            self.commands.append({"name": cmd})
            self.bot.accessmanager.registerAcl("commands.!" + cmd)
            self.writeJSON()
            self.bot.sendMessage("Added command " + cmd)
            log("[ACCESS] Added new command:" + cmd)
        else:
            self.bot.sendMessage("Command " + cmd + " already exists")
            log("[ACCESS] Tried to create a command " + cmd + " that already exists")

    def setCommand(self, args):
        cmd = args[2]
        text = ' '.join(args[3:])

        for command in self.commands:
            if command['name'] == cmd:
                command['value'] = text
                self.writeJSON()
                self.bot.sendMessage("New message for command " + cmd + ": " + text)
                log("[COMMANDS] Modified the value of command " + cmd + " to: " + text)
                return
        self.bot.sendMessage("Command " + cmd + " not found")
        log("[COMMANDS] tried to change the text of a nonexisting command: " + cmd)

    def listCommands(self):
        cmds = ""
        for command in self.commands:
            if cmds is "":
                cmds += command["name"]
            else:
                cmds += ", " + command["name"]

        self.bot.sendMessage("Available commands: " + cmds)