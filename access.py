import re
import json
import errno

from logging import log, d


class access:
    bot = None

    groups = {}
    acls = {}

    jsonfile = "acls.json"

    def init(self, bot):
        self.bot = bot
        self.readJSON()
        log("[ACCESS] Init complete")

        if len(self.groups) is 0:
            self.addGroup("%owner")
            self.addGroup("%operators")
            self.addGroup("%moderators")
            self.writeJSON()

    def readJSON(self):
        jsondata = None
        try:
            file = open(self.jsonfile, "r")
            jsondata = file.read()
            file.close()
        except IOError as e:
            if e.errno == errno.ENOENT:
                log("[COMMANDS] file does not exist, creating")
                self.writeJSON()

        try:
            data = json.loads(jsondata)
            self.groups = data['groups']
            self.acls = data['acls']
        except ValueError:
            log("[COMMANDS] commands-file malformed")


    def writeJSON(self):
        jsondata = {"groups": self.groups, "acls": self.acls}
        file = open(self.jsonfile, "w")
        data = json.dumps(jsondata)
        file.write(data)
        file.close()

    def addGroup(self, name, members=[]):
        self.groups[name] = {"members": members}
        self.writeJSON()

    def removeGroup(self, name):
        self.groups.pop(name, None)
        self.writeJSON()

    def addToGroup(self, group, name):
        self.groups[group]['members'].append(name)
        self.writeJSON()

    def removeFromGroup(self, group, name):
        self.groups[group]['members'].pop(name, None)
        self.writeJSON()

    def createAcl(self, acl):
        self.acls[acl] = {}
        self.writeJSON()

    def registerAcl(self, acl, defaults=None):
        self.createAcl(acl)
        if defaults is None:
            self.addGroupToAcl(acl, "%owner")
            self.addGroupToAcl(acl, "%operators")
        self.writeJSON()

    def addGroupToAcl(self, acl, group):
        if not group in self.groups:
            log("[ACCESS] group does not exist")
            return
        self.acls[acl]['groups'].append(group)
        self.writeJSON()

    def addUserToAcl(self, acl, user):
        self.acls[acl]['members'].append(user)
        self.writeJSON()

    def isInAcl(self, acl, user):
        if user in self.acls[acl].members:
            return True

        for group in self.acls[acl].groups:
            if user in self.groups[group]['members']:
                return True

        return False
    