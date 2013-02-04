from srcbase import *
import sys
import traceback 

from fields import StringField, BooleanField
from gamerules import InstallGameRules, GameRules, CJBGameRules, gamerules
from core.usermessages import usermessage
if isserver:
    from core.usermessages import CSingleUserRecipientFilter
    from gameinterface import concommand, FCVAR_CHEAT, AutoCompletion
    from utils import UTIL_GetCommandClient, UTIL_SayTextAll
    
    from core.dispatch import receiver
    from core.signals import clientactive
    
#if isclient:
#    from vgui import localize
    
import gamemgr
import re
    
prev_gamerules_name = None
cur_gamerules_name = None   
next_gamerules_name = "sandbox" 
 
# Gamerules db
dbid = 'gamerules'
dbgamerules = gamemgr.dblist[dbid]

# Gamerules entry
class GamerulesInfoMetaClass(gamemgr.BaseInfoMetaclass):
    def __new__(cls, name, bases, dct):
        newcls = gamemgr.BaseInfoMetaclass.__new__(cls, name, bases, dct)
        
        newcls.mapfilter = re.compile(newcls.mappattern)
        newcls.factionfilter = re.compile(newcls.factionpattern)
        
        if isclient:
            # Localize fields 
            if not newcls.displayname:
                newcls.displayname = newcls.name
            if newcls.displayname and newcls.displayname[0] == '#':
#                displayname = localize.Find(newcls.displayname)
                displayname = newcls.displayname
                newcls.displayname = displayname.encode('ascii') if displayname else newcls.name
                
            if newcls.description and newcls.description[0] == '#':
#                description = localize.Find(newcls.description)
                description = newcls.description
                displayname = newcls.displayname
                if description:
                    newcls.description = description.encode('ascii')
        
        return newcls
            
class GamerulesInfo(gamemgr.BaseInfo):
    __metaclass__ = GamerulesInfoMetaClass
    donotregister = False
    id = dbid
    
    #: Reference to the gamerules class
    cls = None
    
    #: Name shown in hud.
    #: In case the name starts with #, it is considered a localized string.
    displayname = StringField(value='', noreset=True)
    #: Description shown in hud.
    #: In case the name starts with #, it is considered a localized string.
    description = StringField(value='Put some description here', noreset=True)
    
    #: Package + class name of huds that are created when this gamerule becomes active. Only for WarsBaseGameRules derived classes.
    huds = []
    
    #: 
    allowplayerjoiningame = False

    # REGEX patterns to control options in the gamelobby
    #: REGEX pattern to restrict the map choices
    mappattern = StringField(value='^.*$', noreset=True) # By default allow all maps
    #: REGEX pattern to restrict the faction choices
    factionpattern = StringField(value='^.*$', noreset=True)
    #: If True, allow teams in the gamelobby
    useteams = BooleanField(value=True)
    #: If True, support cpu
    supportcpu = BooleanField(value=True)
    #: If True, support factions
    supportfactions = BooleanField(value=True)
    #: If True, hide start spots in the gamelobby
    hidestartspots = BooleanField(value=False)
    #: Minimum number of players required to start a game with this rules from the gamelobby
    minplayers = 0
    #: Allow all players to be on the same team.
    allowallsameteam = BooleanField(value=True)
    
class GameRulesFallBackInfo(GamerulesInfo):
    name = 'gamerules_unknown'
    donotregister = True
    
def GetGamerulesInfo(gamerules_name):
    # Get info
    try:
        return dbgamerules[gamerules_name]
    except KeyError: 
        return None          

def _LevelInitInstallGamerules():
    global next_gamerules_name
    if next_gamerules_name != None:
        SetGamerules(next_gamerules_name)
    
def SetGamerules(gamerules_name, setnext = True):
    global prev_gamerules_name, cur_gamerules_name, next_gamerules_name
    if gamerules_name is None:
        ClearGamerules()
        return

    try:
        info = dbgamerules[gamerules_name]
    except KeyError:
        PrintWarning("core.gamerules.info.SetGamerules: No registered gamerule named " + gamerules_name + "\n" )
        return
    
    prev_gamerules_name = cur_gamerules_name
    cur_gamerules_name = gamerules_name
    InstallGameRules(info.cls)
    
    if GameRules() == None:
        ClearGamerules()
        return

    if isserver and setnext:
        next_gamerules_name = cur_gamerules_name
        
def _PreInitGamerules():
    # Bind info object to gamerules to make it easy to retrieve
    info = GetGamerulesInfo(cur_gamerules_name)
    if info:
        GameRules().info = info
        
    # Set proxy
    gamerules.gamerules = GameRules()
    
    if isserver:
        # Inform clients about the change
        ClientSetGamerules(cur_gamerules_name)        
        
def ClearGamerules():    
    InstallGameRules(None)
    #GameRules().info = GameRulesFallBackInfo
    cur_gamerules_name = None        
    
    if isserver:
        # Inform clients about the change
        ClientClearGamerules()

#
# Set gamerules
#
if isserver:
    @concommand('wars_setgamerules', 'Set the gamerules', FCVAR_CHEAT, completionfunc=AutoCompletion(lambda: dbgamerules.keys()))
    def cc_wars_setgamerules(args):
        SetGamerules(args[1])
        UTIL_SayTextAll('Gamerules changed to %s' % (args[1]))
    
    @concommand('wars_cleargamerules', 'Clear the gamerules', FCVAR_CHEAT)
    def cc_wars_cleargamerules(args):
        ClearGamerules()
        
# Give a full update
if isserver:
    @receiver(clientactive)
    def NewClientActive(sender, client, **kwargs):
        if cur_gamerules_name != None:
            filter = CSingleUserRecipientFilter(client)
            filter.MakeReliable()
            ClientSetGamerules(cur_gamerules_name, filter=filter)
        
@usermessage()
def ClientSetGamerules(gamerulesname, **kwargs):
    SetGamerules(gamerulesname)
    
@usermessage()
def ClientClearGamerules(**kwargs):
    ClearGamerules()