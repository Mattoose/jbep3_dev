from srcbase import *
from vmath import Vector
import sys
import traceback

from fields import StringField
from gameinterface import ConVar, concommand, AutoCompletion, FCVAR_CHEAT
from utils import UTIL_FindPosition, FindPositionInfo
from core.dispatch import receiver
from core.signals import playerchangedfaction
from core.usermessages import usermessage
from entities import CBaseEntity
if isclient:
    from entities import C_JBPlayer
    from vgui import CHudElementHelper, localize
else:
    from utils import UTIL_PlayerByIndex, UTIL_GetCommandClient

import gamemgr

# Factions db
dbid = 'factions'
dbfactions = gamemgr.dblist[dbid]

# Global ref to hud
faction_hud_helper = None # VGUI version
faction_hud_web = None # Awesomium/webview version

# Factions info entry
class FactionInfoMetaClass(gamemgr.BaseInfoMetaclass):
    def __new__(cls, name, bases, dct):
        newcls = gamemgr.BaseInfoMetaclass.__new__(cls, name, bases, dct)
        
        if isclient:
            if not newcls.displayname:
                newcls.displayname = newcls.name
            if newcls.displayname and newcls.displayname[0] == '#':
                displayname = localize.Find(newcls.displayname)
                newcls.displayname = displayname.encode('ascii') if displayname else newcls.name
                
        return newcls
        
class FactionInfo(gamemgr.BaseInfo):
    __metaclass__ = FactionInfoMetaClass
    donotregister = False
    id = dbid
    displayname = StringField(value='', noreset=True)
    hud_name = StringField(value='hud_invalid')
    faction_hud_cvar = None
    startbuilding = StringField(value='')
    startunit = StringField(value='')
    resources = []
    
    soundcpcaptured = StringField(value='')
    soundcplost = StringField(value='')
    soundunitcomplete = StringField(value='')
    soundresearchcomplete = StringField(value='')
    
    @classmethod
    def Precache(info):
        if info.soundcpcaptured: CBaseEntity.PrecacheSound(info.soundcpcaptured)
        if info.soundcplost: CBaseEntity.PrecacheSound(info.soundcplost)
        if info.soundunitcomplete: CBaseEntity.PrecacheSound(info.soundunitcomplete)
        
    @classmethod
    def PopulateStartSpot(info, gamrules, startspot, ownernumber, playerSteamID=None):
        if not info.startbuilding or not info.startunit:
            PrintWarning('Faction %s has no start building or unit specified! Unable to populate start spot.\n')
            return
            
        from core.units import CreateUnit
        # Spawn start building
        if info.startbuilding:
            CreateUnit(info.startbuilding, startspot.GetAbsOrigin(), startspot.GetAbsAngles(), ownernumber) 
        
        # Spawn a start unit (todo: offset?)
        if info.startunit:
            unit = CreateUnit(info.startunit, startspot.GetAbsOrigin()+Vector(270, 0, 48), startspot.GetAbsAngles(), ownernumber)
            if unit:
                findinfo = UTIL_FindPosition(FindPositionInfo(startspot.GetAbsOrigin()+Vector(270, 0, 48), unit.WorldAlignMins(), unit.WorldAlignMaxs(), 0, 128, ignore=unit))
                unit.SetAbsOrigin(findinfo.position)
        
    @classmethod           
    def OnLoaded(info):        
        name = info.name 
        if isclient:
            # Dynamically create a convar for the hud named like: factionname_hud
            dbfactions[name].faction_hud_cvar = ConVar(dbfactions[name].name+"_hud", dbfactions[name].hud_name, 
                0, "Faction hud", HudConvarChanged)
            
            # If the local player's faction is this hud, initialize it
            player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
            if player and player.GetFaction() == name:
                CreateHud(name)
        
    @classmethod       
    def OnUnLoaded(info):
        name = info.name 
        if isclient:
            dbfactions[name].faction_hud_cvar = None
            DestroyHud()
        
def GetFactionInfo(faction_name):
    try:
        return dbfactions[faction_name]
    except KeyError:
        return None        
        
def HudConvarChanged(var, old_value, f_old_value):
    # Retrieve the faction name
    name = var.GetName().rstrip('_hud')
    hud_name = var.GetString()

    # Make sure the old hud is destroyed
    DestroyHud()
    
    # Save the new name. Change hud helper if this faction is the players local faction
    dbfactions[name].hud_name = hud_name
    player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
    if player and player.GetFaction() == name:
        CreateHud(name)
        
# Hud create/destroy methods
def CreateHud(name):
    global faction_hud_helper, faction_hud_web
    DestroyHud()
    
    # Get hud info
    try:
        from core.hud.info import dbhuds # TODO: FIXME, can't import at top since factions is imported before the hud
        info = dbhuds[dbfactions[name].hud_name]
    except KeyError:
        PrintWarning("Default hud " + dbfactions[name].hud_name + " missing. Aborting create hud faction " + name + "\n")
        return 

    try:
        # Create vgui hud if any
        if info.cls:
            faction_hud = info.cls()
            faction_hud_helper = CHudElementHelper(faction_hud)  
    except:
        traceback.print_exc()

    if type(info.wcls) == list:
            for wcls in info.wcls:
                try:
                    # Create webview hud if any
                    if wcls:
                        faction_hud_web.append(wcls())
                except:
                    traceback.print_exc()
    else:
        try:
            # Create webview hud if any
            if info.wcls:
                faction_hud_web.append(info.wcls())
        except:
            traceback.print_exc()
        
def DestroyHud():
    global faction_hud_helper, faction_hud_web
    
    try:
        if faction_hud_helper:
            hud = faction_hud_helper.Get()
            if hud:
                hud.SetVisible(False)
                hud.DeletePanel()
            faction_hud_helper = None
    except:
        traceback.print_exc()
        
    
    if faction_hud_web != None:
        for hud in faction_hud_web:
            try:
                if hud:
                    hud.SetVisible(False)
                    hud.Remove()
                    hud = None
            except:
                traceback.print_exc()
        
    faction_hud_web = []
        
# Play a sound
@usermessage(messagename='playfactionsound')
def PlayFactionSound(factionsoundname, **kwargs):
    player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
    if not player or not player.GetFaction():
        return
    info = GetFactionInfo(player.GetFaction())
    try:
        soundname = getattr(info, factionsoundname)
    except AttributeError:
        PrintWarning('PlayFactionSound: missing sound %s for faction %s' % (factionsoundname, player.GetFaction()))
        return
    
    if not soundname:
        return
    player.EmitAmbientSound(-1, player.GetAbsOrigin(), soundname)
    
# Called when player changed his faction
@receiver(playerchangedfaction)
def PlayerChangedFaction(player, oldfaction, **kwargs):
    if not player:
        return
    faction_name = player.GetFaction()
    
    info = dbfactions.get(faction_name, None)
    if not info:
        PrintWarning("Faction change failed. Invalid faction '" + faction_name+"'\n")
        return 
        
    info.Precache()
    
    if isclient:
        CreateHud(faction_name)
    
# Command to change the players faction
if isserver:
    @concommand('wars_changefaction', 'Change faction \n\tArguments: { faction name }', 
                FCVAR_CHEAT, completionfunc=AutoCompletion(lambda: dbfactions.keys()))
    def cc_wars_changefaction(args):
        player = UTIL_GetCommandClient()
        player.ChangeFaction(args[1])

# When this module is reloaded we must call _changefaction for each player to reinitialize
if isclient:
    player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
    # Not ingame or initialized yet
    if player != None and player.GetFaction() != None:
        PlayerChangedFaction(player, '')
else:
    for i in range(1, gpGlobals.maxClients+1):
        player = UTIL_PlayerByIndex(i)
        if player == None:
            continue
        if player.GetFaction() != None:
            PlayerChangedFaction(player, '')    
            