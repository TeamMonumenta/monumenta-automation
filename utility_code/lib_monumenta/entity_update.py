#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import codecs

# The effective working directory for this script must always be the MCEdit-Unified directory
# This is NOT how we should be doing this, but I don't see how to fix pymclevel to be standalone again.
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCEdit-Unified/"))

# Import pymclevel from MCLevel-Unified
from pymclevel import nbt

from lib_monumenta.iter_entity import IterEntities

formatCodes = {
    "colors":u'0123456789abcdef',
    "styles":u'klmnor',
    "list":[
        {"id":u"0","display":u"Black","technical":u"black",},
        {"id":u"1","display":u"Dark Blue","technical":u"dark_blue",},
        {"id":u"2","display":u"Dark Green","technical":u"dark_green",},
        {"id":u"3","display":u"Dark Aqua","technical":u"dark_aqua",},
        {"id":u"4","display":u"Dark Red","technical":u"dark_red",},
        {"id":u"5","display":u"Dark Purple","technical":u"dark_purple",},
        {"id":u"6","display":u"Gold","technical":u"gold",},
        {"id":u"7","display":u"Gray","technical":u"gray",},
        {"id":u"8","display":u"Dark Gray","technical":u"dark_gray",},
        {"id":u"9","display":u"Blue","technical":u"blue",},
        {"id":u"a","display":u"Green","technical":u"green",},
        {"id":u"b","display":u"Aqua","technical":u"aqua",},
        {"id":u"c","display":u"Red","technical":u"red",},
        {"id":u"d","display":u"Light Purple","technical":u"light_purple",},
        {"id":u"e","display":u"Yellow","technical":u"yellow",},
        {"id":u"f","display":u"White","technical":u"white",},

        {"id":u"k","display":u"Obfuscated","technical":u"obfuscated",},
        {"id":u"l","display":u"Bold","technical":u"bold",},
        {"id":u"m","display":u"Strikethrough","technical":u"strikethrough",},
        {"id":u"n","display":u"Underline","technical":u"underlined",},
        {"id":u"o","display":u"Italic","technical":u"italic",},
        {"id":u"r","display":u"Reset","technical":u"reset",},
    ],
}

################################################################################
# Item stack finding code

class UpdateEntities(object):
    """
    Entity update util; give it an uncompiled
    list of entities to update, then tell it where
    to update things.

    debug is a list of strings:
    "init" - displays each update's description as it is loaded
    "global count" - counts the occurances of all entities
    """
    def __init__(self,debug=[],updateList=None):
        if "init" in debug:
            print u"  New entity update list loading..."
        if updateList is None:
            self.updates = None
            if "init" in debug:
                print u"  ┗╸Dummy list, does nothing."
            return
        self.log_data = {}
        self.log_data["debug"] = debug
        self.log_data["global"] = {}
        self.updates = allUpdates(updateList,self.log_data)
        if "global count" in debug:
            self.enableGlobalCount()
        self.entityIter = IterEntities(
            [
                "block entities",
                "entities",
                "search spawners"
            ],
            self._OnEntities,
            None
        )

    def enableGlobalCount(self):
        if "global count" not in self.log_data["debug"]:
            self.log_data["debug"].append("global count")
        if "global count" not in self.log_data["global"]:
            self.log_data["global"]["global count"] = {}
            self.log_data["global"]["global count"]["entities"] = {}
            self.log_data["global"]["global count"]["block entities"] = {}

    def InChunkTag(self,chunkTag):
        if self.updates is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InChunkTag(chunkTag)

    def InChunk(self,chunk):
        if self.updates is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InChunk(chunk)

    def InWorld(self,world):
        if self.updates is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InWorld(world)

    def InSchematic(self,schematic):
        if self.updates is None:
            return
        self.log_data["current"] = {}
        self.entityIter.InSchematic(schematic)

    def OnPlayers(self,worldDir):
        if self.updates is None:
            return
        self.log_data["current"] = {}
        self.entityIter.OnPlayers(worldDir)

    def PrintGlobalLog(self):
        if "global count" in self.log_data["global"]:
            print u"Entities found:"
            for entity in sorted(self.log_data["global"]["global count"]["entities"].keys()):
                line = u"{}\t{}\n".format(
                    self.log_data["global"]["global count"]["entities"][entity],
                    entity
                )
                print line
            print u"Block entities found:"
            for entity in sorted(self.log_data["global"]["global count"]["block entities"].keys()):
                line = u"{}\t{}\n".format(
                    self.log_data["global"]["global count"]["block entities"][entity],
                    entity
                )
                print line

    def SaveGlobalLog(self,logPath=None):
        if logPath is None:
            print u"! Global Entity Update log path not specified"
            return
        if "global count" in self.log_data["global"]:
            with codecs.open(logPath,'w',encoding='utf8') as f:
                f.write(u"Entities found:\n")
                for entity in sorted(self.log_data["global"]["global count"]["entities"].keys()):
                    line = u"{}\t{}\n".format(
                        self.log_data["global"]["global count"]["entities"][entity],
                        entity
                    )
                    f.write(line)
                f.write(u"Block entities found:\n")
                for entity in sorted(self.log_data["global"]["global count"]["block entities"].keys()):
                    line = u"{}\t{}\n".format(
                        self.log_data["global"]["global count"]["block entities"][entity],
                        entity
                    )
                    f.write(line)
                f.close()

    def _OnEntities(self,dummyArg,entityDetails):
        entity = entityDetails["entity"]
        entityType = entityDetails["entity type"]
        self.log_data["entity"] = entity
        self.log_data["player file"] = entityDetails["player file"]

        # The entity exists in the world/schematic directly,
        # not inside something.
        if entityDetails["root entity"] is True:
            self.rootEntity = entityDetails["entity"]
        else:
            self.rootEntity = entityDetails["root entity"]
            self.log_data["rootEntity"] = self.rootEntity

        self.updates.run(entityDetails,self.log_data)
        if "global count" in self.log_data["debug"]:
            globalCounts = self.log_data["global"]["global count"][entityType]
            entityJson = entity.json(['CustomName','id','Tags'])
            if entityJson not in globalCounts:
                globalCounts[entityJson] = count
            else:
                globalCounts[entityJson] += count


################################################################################
# Update list optimizer

class allUpdates(list):
    def __init__(self,updateList,log_data):
        self._updates = []
        for anUpdate in updateList:
            if type(anUpdate) is UpdateEntities:
                if "init" in log_data["debug"]:
                    print u"  ┣╸Adding an entity update list"
                    print u"  ┃ ╙╴No code to track which one it is, sorry."
                self._updates.append(anUpdate.updates)
            else:
                self._updates.append(update(anUpdate,log_data))
        print u"  Found " + unicode(len(self._updates)) + u" entity updates."

    def run(self,entityDetails,log_data):
        for anUpdate in self._updates:
            anUpdate.run(entityDetails,log_data)

class update(object):
    def __init__(self,updatePair,log_data):
        matches = updatePair[0]
        actions = updatePair[1]

        if "init" in log_data["debug"]:
            print u"  ┣╸Adding an entity update:"

        # matches is the list of uncompiled matches
        # self._matches is the list of compiled matches
        if (
            "any" in matches and
            len(matches.keys()) == 1
        ):
            # If is level only contains an OR, skip to it
            self._matches = matchAny(matches["any"])
        else:
            self._matches = matchAll(matches)
        if "init" in log_data["debug"]:
            print self._matches.str(u"  ┃ ")

        if "init" in log_data["debug"]:
            print u"  ┃ ╙╴Then do these in order:"

        # actions is the uncompiled list of actions
        # self._actions is the list of compiled actions
        self._actions = []
        while len(actions):
            action = actions.pop(0)
            if action == "id":
                newAction = actID(actions)
            if action == "name":
                newAction = actName(actions)
            if action == "nbt":
                newAction = actNBT(actions)
            if action == "print":
                newAction = actPrint(actions)
            if action == "print entity":
                newAction = actPrintEntity(actions)
            if action == "print location":
                newAction = actPrintLocation(actions)
            if action == "remove":
                newAction = actRemove(actions)
            if action == "tag":
                newAction = actTag(actions)

            self._actions.append(newAction)
            if "init" in log_data["debug"]:
                print newAction.str(u"  ┃   ")

    def run(self,entityDetails,log_data):
        if self._matches == entityDetails:
            for action in self._actions:
                action.run(entityDetails,log_data)

# Matching optimizers

class match(object):
    def __init__(self,matchOptions):
        pass

    def _grab_matches(self,matchOptions):
        for key in matchOptions:
            newMatch = None
            if key == "any":
                newMatch = matchAny(matchOptions[key])
            if key == "all":
                newMatch = matchAll(matchOptions[key])
            if key == "id":
                newMatch = matchID(matchOptions[key])
            if key == "name":
                newMatch = matchName(matchOptions[key])
            if key == "name_format":
                newMatch = matchNameFormat(matchOptions[key])
            if key == "nbt":
                newMatch = matchNBT(matchOptions[key])
            if key == "none":
                newMatch = matchNone(matchOptions[key])
            if key == "tag":
                newMatch = matchTag(matchOptions[key])
            if newMatch is not None:
                self._matches.append(newMatch)

    def __eq__(self,entityDetails):
        return False

    def str(self,prefix=u''):
        return prefix + u'└╴Undefined matching pattern (returns False)'

class matchAll(match):
    """
    Logical AND
    Match if all sub matches are true;
    If no sub matches exist, always false;
    This is the default case
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,entityDetails):
        if self._matches is None:
            return False
        else:
            return all(rule == entityDetails for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴False'
        else:
            result = prefix + u'╟╴If all of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result

class matchAny(match):
    """
    Logical OR
    Match if any of the sub matches are true;
    If no sub matches exist, always true
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,entityDetails):
        if self._matches is None:
            return True
        else:
            return any(rule == entityDetails for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴True'
        else:
            result = prefix + u'╟╴If any of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result

class matchID(match):
    """
    This stores an ID to match later
    """
    def __init__(self,matchOptions):
        self._id = matchOptions

    def __eq__(self,entityDetails):
        try:
            return self._id == entityDetails["entity"]["id"].value
        except:
            return False

    def str(self,prefix=u''):
        return prefix + u'└╴Entity ID is "' + self._id + u'"'

class matchName(match):
    """
    This stores a name to match later without color
    """
    def __init__(self,matchOptions):
        self._name = matchOptions
        if type(self._name) == str:
            self._name = unicode(self._name)

    def __eq__(self,entityDetails):
        if ( "CustomName" not in entityDetails["entity"] ):
            return self._name is None
        elif self._name is None:
            return False
        else:
            nameNoFormat = entityDetails["entity"]["CustomName"].value
            while u'§' in nameNoFormat:
                i = nameNoFormat.find(u'§')
                nameNoFormat = nameNoFormat[:i]+nameNoFormat[i+2:]
            return nameNoFormat == self._name

    def str(self,prefix=u''):
        if self._name == None:
            return prefix + u'└╴Entity has no name'
        else:
            return prefix + u'└╴Entity name matches "' + self._name + '" regardless of color'

class matchNameFormat(match):
    """
    This stores the formatting of a name to match later
    Expects the color id, like u'a' for green
    """
    def __init__(self,matchOptions):
        self._nameFormat = None
        color = matchOptions
        if type(color) == int:
            # assumes color is a number from 0-15
            self._nameFormat = formatCodes["list"][color]
        elif (
            (type(color) == str) or
            (type(color) == unicode)
        ):
            # assumes color is a name or character like '7' as in '§7'
            # use '' to mean "no color"
            for formatCode in formatCodes["list"]:
                if (
                    (color.lower() == formatCode["id"].lower()) or
                    (color.lower() == formatCode["display"].lower()) or
                    (color.lower() == formatCode["technical"].lower())
                ):
                    self._nameFormat = formatCode
        # If self._color is None by here, assume it should be no color

    def __eq__(self,entityDetails):
        if ( "CustomName" not in entityDetails["entity"] ):
            return False
        elif self._nameFormat is None:
            return False

        nameNoFormat = entityDetails["entity"]["CustomName"].value
        nameFormatOnly = u''
        while (
            ( len(nameNoFormat) != 0 ) and
            ( u'§' == nameNoFormat[0] )
        ):
            nameFormatOnly += nameNoFormat[1]
            nameNoFormat = nameNoFormat[2:]

        return (
            ( len(nameNoFormat) != 0 ) and
            ( nameFormatOnly == self._nameFormat["id"] )
        )

    def str(self,prefix=u''):
        if self._nameFormat == None:
            return prefix + u'└╴Entity has no name formatting'
        else:
            return prefix + u'└╴Entity name format matches {} regardless of text'.format(self._nameFormat["display"])

class matchNBT(match):
    """
    This stores NBT to match later
    """
    def __init__(self,matchOptions):
        json = matchOptions

        self._exact = False
        if "strict" == json[:6]:
            self._exact = True
            json = json[6:]
        self._nbt = nbt.json_to_tag(json)

    def __eq__(self,entityDetails):
        if self._exact:
            return self._nbt.eq(entityDetails["entity"])
        else:
            return self._nbt.issubset(entityDetails["entity"])

    def str(self,prefix=u''):
        if self._exact:
            return prefix + u'└╴Entity NBT exactly matches ' + self._nbt.json()
        else:
            return prefix + u'└╴Entity NBT loosely matches ' + self._nbt.json()

class matchNone(match):
    """
    Logical NOR/NOT
    Match if none of the sub matches are true;
    If no sub matches exist, defaults to false;
    This is a special case to never match anything;
    used to invalidate item replacements
    """
    def __init__(self,matchOptions):
        self._matches = None
        if type(matchOptions) is list:
            self._matches = []
            for i in matchOptions:
                if len(i.keys()) == 1:
                    self._grab_matches(i)
                else:
                    subMatch=matchAll(i)
                    self._matches.append(subMatch)
        elif type(matchOptions) is dict:
            self._matches = []
            self._grab_matches(matchOptions)

    def __eq__(self,entityDetails):
        if self._matches is None:
            return False
        else:
            return all(rule != entityDetails for rule in self._matches)

    def str(self,prefix=u''):
        if self._matches is None:
            return prefix + u'└╴False'
        else:
            result = prefix + u'╟╴If none of these are true:'
            subprefix = prefix + u'║ '
            for match in self._matches:
                result += u'\n' + match.str(subprefix)
            return result

class matchTag(match):
    """
    Match scoreboard tags (supports "!tag" to find entities without "tag")
    """
    def __init__(self,matchOptions):
        self._tags = matchOptions
        self._hasTags = []
        self._notTags = []
        for scoreTag in self._tags:
            if scoreTag[0] == '!':
                # Doesn't have this tag
                self._notTags.append(scoreTag[1:])
            else:
                # Has this tag
                self._hasTags.append(scoreTag)

    def __eq__(self,entityDetails):
        if "Tags" not in entityDetails["entity"]:
            if len(self._hasTags) > 0:
                return False
            else:
                return True
        entityTags = entityDetails["entity"]["Tags"]
        if any(entityTag.value in self._notTags for entityTag in entityTags):
            return False
        for scoreTag in self._hasTags:
            if not any(entityTag.value == scoreTag for entityTag in entityTags):
                return False
        return True

    def str(self,prefix=u''):
        return prefix + u'└╴Entity matches scoreboard tags ' + self._tags


# Action optimizers

class actID(object):
    """
    Stores an ID to apply later
    """
    def __init__(self,actionOptions):
        self._id = actionOptions.pop(0)

    def run(self,entityDetails,log_data):
        entityDetails["entity"]["id"].value = self._id

    def str(self,prefix=u''):
        return prefix + u'└╴Change ID to "' + self._id + u'"'

class actPrintLocation(object):
    """
    Print the player file or location of the root entity
    """
    def __init__(self,actionOptions):
        return

    def run(self,entityDetails,log_data):
        if log_data["player file"] is not None:
            print u"Entity is in player file " + log_data["player file"]
        elif "Pos" in log_data["rootEntity"]:
            print u"Entity is on {} at {},{},{}".format(
                log_data["rootEntity"]["id"].value,
                round(log_data["rootEntity"]["Pos"][0].value,3),
                round(log_data["rootEntity"]["Pos"][1].value,3),
                round(log_data["rootEntity"]["Pos"][2].value,3)
            )
        elif "x" in log_data["rootEntity"]:
            print u"Entity is in {} at {},{},{}".format(
                log_data["rootEntity"]["id"].value,
                log_data["rootEntity"]["x"].value,
                log_data["rootEntity"]["y"].value,
                log_data["rootEntity"]["z"].value
            )
        else:
            print u"Entity is on an entity without location? " + log_data["rootEntity"].json()

    def str(self,prefix=u''):
        return prefix + u'└╴Print the player file name or location of the root entity'

class actName(object):
    """
    Modify an entity name
    """
    def __init__(self,actionOptions):
        self._cmd = actionOptions.pop(0)
        if self._cmd == "color":
            self._color = None
            color = actionOptions.pop(0)
            if type(color) == int:
                # assumes color is a number from 0-15
                self._color = formatCodes["list"][color]
            elif (
                (type(color) == str) or
                (type(color) == unicode)
            ):
                # assumes color is a name or character like '7' as in '§7'
                # use '' to mean "no color"
                for formatCode in formatCodes["list"]:
                    if (
                        (color.lower() == formatCode["id"].lower()) or
                        (color.lower() == formatCode["display"].lower()) or
                        (color.lower() == formatCode["technical"].lower())
                    ):
                        self._color = formatCode
            # If self._color is None by here, assume it should be no color
        elif self._cmd == "set":
            self._setName = None
            name = actionOptions.pop(0)
            if (
                (type(name) == str) or
                (type(name) == unicode)
            ):
                self._setName = name
            # If self._setName is None by here, assume it should be no name
        else:
            print u"!!! Unknown subcommand for actName: {}".format(self._cmd)
            # put the subcommand back
            actionOptions.insert(0,self._cmd)
            self._cmd = None

    def run(self,entityDetails,log_data):
        if self._cmd == "color":
            if "CustomName" not in entityDetails["entity"]:
                # not applicable (unless default name is obtained)
                return
            formatList = u""
            name = entityDetails["entity"]["CustomName"].value
            while (
                ( len(name) != 0 ) and
                ( name[0] == u'§' )
            ):
                formatList += name[1]
                name = name[2:]
            if len(name) == 0:
                entityDetails["entity"].pop("CustomName")
            else:
                while len(formatList):
                    color = formatList[-1]
                    formatList = formatList[:-1]
                    if color not in formatCodes["colors"]:
                        name = u'§' + color + name
                if self._color is not None:
                    name = u'§' + self._color["id"] + name
                entityDetails["entity"]["CustomName"].value = name

        elif self._cmd == "set":
            if self._setName is None:
                # delete the item name
                if "CustomName" in entityDetails["entity"]:
                    entityDetails["entity"].pop("CustomName")
            else:
                # set the item name
                if "CustomName" not in entityDetails["entity"]:
                    entityDetails["entity"]["CustomName"] = nbt.TAG_String(self._setName)
                else:
                    entityDetails["entity"]["CustomName"].value = self._setName

    def str(self,prefix=u''):
        if self._cmd == "color":
            if self._color is None:
                return prefix + u'└╴Remove name color if name exists'
            else:
                return prefix + u'└╴Update name color to {} if name exists'.format(self._color["display"])
        elif self._cmd == "set":
            if self._setName is None:
                return prefix + u'└╴Remove entity name'
            else:
                return prefix + u'└╴Set name to "{}"'.format(self._setName)
        else:
            return prefix + u'└╴Invalid color subcommand; does nothing'

class actNBT(object):
    """
    Stores an NBT action to apply later
    """
    def __init__(self,actionOptions):
        self._operation = actionOptions.pop(0)
        if (
                (self._operation == "update")
                or (self._operation == "replace")
        ):
            self._nbt = nbt.json_to_tag( actionOptions.pop(0) )

    def run(self,entityDetails,log_data):
        entity = entityDetails["entity"]

        tagsToRestore = nbt.TAG_Compound()
        # common to entities and block entities
        if "id" in entity:
            tagsToRestore["id"] = entity["id"]

        # block entities
        if "x" in entity:
            tagsToRestore["x"] = entity["x"]
        if "y" in entity:
            tagsToRestore["y"] = entity["y"]
        if "z" in entity:
            tagsToRestore["z"] = entity["z"]

        # entities
        if "Pos" in entity:
            tagsToRestore["Pos"] = entity["Pos"]
        if "Motion" in entity:
            tagsToRestore["Motion"] = entity["Motion"]
        if "Rotation" in entity:
            tagsToRestore["Rotation"] = entity["Rotation"]
        if "FallDistance" in entity:
            tagsToRestore["FallDistance"] = entity["FallDistance"]
        if "Fire" in entity:
            tagsToRestore["Fire"] = entity["Fire"]
        if "Air" in entity:
            tagsToRestore["Air"] = entity["Air"]
        if "OnGround" in entity:
            tagsToRestore["OnGround"] = entity["OnGround"]
        if "PortalCooldown" in entity:
            tagsToRestore["PortalCooldown"] = entity["PortalCooldown"]
        if "UUIDMost" in entity:
            tagsToRestore["UUIDMost"] = entity["UUIDMost"]
        if "UUIDLeast" in entity:
            tagsToRestore["UUIDLeast"] = entity["UUIDLeast"]

        ########################################
        # Clear NBT if needed
        if self._operation == "replace":
            for key in entity.keys():
                entity.pop(key)

        ########################################
        # Set NBT if needed
        if (
                (self._operation == "update")
                or (self._operation == "replace")
        ):
            entity.update(self._nbt)

        # Restore nbt that may be missing or invalid
        entity.update(tagsToRestore)

    def str(self,prefix=u''):
        if self._operation == "update":
            return prefix + u'└╴Update existing NBT with ' + self._nbt.json()
        if self._operation == "replace":
            return prefix + u'└╴Replace NBT with ' + self._nbt.json()

class actPrint(object):
    """
    Print a constant string to the terminal
    """
    def __init__(self,actionOptions):
        self._msg = actionOptions.pop(0)

    def run(self,entityDetails,log_data):
        print self._msg

    def str(self,prefix=u''):
        return prefix + u'└╴Print "' + self._msg + '"'

class actPrintEntity(object):
    """
    Print the entity to the terminal as json
    """
    def __init__(self,actionOptions):
        return

    def run(self,entityDetails,log_data):
        print entityDetails["entity"].json()

    def str(self,prefix=u''):
        return prefix + u'└╴Print the entity details as json'

class actRemove(object):
    """
    Stores an entity removal action to apply later
    """
    def __init__(self,actionOptions):
        return

    def run(self,entityDetails,log_data):
        entity = entityDetails["entity"]
        for key in entity.keys():
            entity.pop(key)

    def str(self,prefix=u''):
        return prefix + u'└╴Delete the entity'

class actTag(object):
    """
    Apply tags to an entity
    """
    def __init__(self,actionOptions):
        self._tags = actionOptions.pop(0)

    def run(self,entityDetails,log_data):
        entity = entityDetails["entity"]
        if "Tags" not in entity:
            entity["Tags"] = nbt.TAG_List()
        entityTags = entity["Tags"]
        for scoreTag in self._tags:
            if scoreTag[0] == '!':
                # Remove tag
                for i in range(len(entityTags)-1,-1,-1):
                    toRemove = scoreTag[1:]
                    if entityTags[i].value == toRemove:
                        entityTags.pop(i)
            else:
                # Add tag
                scoreTagNBT = nbt.TAG_String(scoreTag)
                if not any(scoreTagNBT.value == entityTag.value for entityTag in entityTags):
                    entityTags.append(scoreTagNBT)

    def str(self,prefix=u''):
        return prefix + u'└╴Apply these tags: ' + repr(self._tags)

