"""
Manages the gamelobby.
Sends messages to the clients to inform them.
Launches game and applies data from the gamelobby.
TODO: Maybe split up in two files: a client and server part.
"""
import traceback
from srcbase import *
from vmath import *
import srcmgr
import playermgr
import readmap
import random
import os

from core.gamerules.info import dbgamerules
from core.gamerules import SetGamerules, GetGamerulesInfo, GamerulesInfo
from core.factions import dbfactions
from core.dispatch import receiver
from core.signals import prelevelinit, postlevelinit
from core.usermessages import usermessage

from collections import defaultdict

from gamelobby_shared import *

from gamerules import CHL2WarsGameRules, GameRules
if isclient:
    from ui.gamelobby import Gamelobby
    from ui.gamelobby_waitingforplayers import wfp
    from ui.gamelobby_loadingpanel import glloadingdialog
    from vgui.musicplayer import musicmanager
else:
    from gameinterface import *
    from utils import UTIL_PlayerByIndex, UTIL_SayTextFilter, UTIL_GetPlayers
    from entities import gEntList
    
# State of gamelobby on client
GAMELOBBY_INACTIVE = 0
GAMELOBBY_ACTIVE = 1
GAMELOBBY_WAITINGFORPLAYERS = 2
state = GAMELOBBY_INACTIVE    
    
# Saved data between maps
gamelobby_gamescheduled = False
gamelobby_gamerule = None
gamelobby_players = []
gamelobby_customfields = []

if isserver:
    def setup_game():
        global gamelobby_gamerule, gamelobby_players, gamelobby_customfields, state
        state = GAMELOBBY_INACTIVE
        SetGamerules(gamelobby_gamerule)
        
        if hasattr(GameRules(), 'SetupGame'):
            # Setup game and start recording stats
            GameRules().SetupGame(gamelobby_players, gamelobby_customfields)
            GameRules().StartRecordStats()
            
    @receiver(prelevelinit)
    def callback_applydata(sender, **kwargs): 
        global gamelobby_gamescheduled
        if not gamelobby_gamescheduled:
            return
        GameRules().state = GAMELOBBY_WAITINGFORPLAYERS
        gamelobby_gamescheduled = False 
        
    gl_usemaplist = ConVar('gl_usemaplist', '0')
    gl_playerloadtimeout = ConVar('gl_playerloadtimeout', '180')
    gl_skipplayercheck = ConVar('gl_skipplayercheck', '0', FCVAR_CHEAT)
else:
    @receiver(postlevelinit)
    def callback_applydata(sender, **kwargs):
        global state
        state = GAMELOBBY_INACTIVE
        
# Usermessages loading panel
def GLLDGetNextPlayer(players):
    if len(players) == 0:
        return None
    return (players.pop(0), players.pop(0))
    
@usermessage()
def GLLDPlayerStatusUpdate(players, **kwargs):
    glloadingdialog.playerlist.RemoveAll()
    player = GLLDGetNextPlayer(players)
    while player:
        data = KeyValues('data')
        data.SetString('name', player[0])
        data.SetString('status', player[1])
        itemID = glloadingdialog.playerlist.AddItem(0, data)    
        glloadingdialog.playerlist.SetItemFgColor( itemID, Color(255, 255, 255, 255) )
        player = GLLDGetNextPlayer(players)
    
@usermessage('gl_wfp')
def GLLDSetStatusWFP(loadtimeout, **kwargs):
    glloadingdialog.playerlist.RemoveAll()
    glloadingdialog.countdowntime = None
    glloadingdialog.loadtimeout = loadtimeout
    glloadingdialog.header.SetText("Waiting for players...")
    
@usermessage('gl_cd')
def GLLDSetStatusCD(countdowntime, **kwargs):
    glloadingdialog.playerlist.RemoveAll()
    glloadingdialog.countdowntime = countdowntime
    
# Usermessages gamelobby
        
# Message types
MGL_GAMEMASTERINDEX = 0
MGL_INDEX       = 1
MGL_TYPE        = 2
MGL_COLOR       = 3
MGL_FACTION     = 4
MGL_TEAM        = 5
MGL_READY       = 6
MGL_POSITION    = 7

MGL_MAPENTRY    = 11
MGL_STARTMAPLIST = 12
MGL_ENDMAPLIST = 13

MGL_SETTINGS = 14
MGL_CUSTOMFIELD = 15

MGL_STATE = 16

# Message processing (TODO: split into separate usermessages)
@usermessage(messagename='glpkg')
def ClientGamelobbyUpdate(msg, **kwargs):
    global state
    mt = msg[0]
    # Misc
    if mt == MGL_GAMEMASTERINDEX:
        GameRules().gamemasterindex = msg[1]   
    elif mt == MGL_STATE:
        state = msg[1]
        
        if type(GameRules()) == GameLobbyRules:
            if state == GAMELOBBY_ACTIVE:
                GameRules().gl.ShowPanel(True)
                wfp.ShowPanel(False)
            elif state == GAMELOBBY_WAITINGFORPLAYERS:
                GameRules().gl.ShowPanel(False)
                wfp.ShowPanel(True)
            else:
                GameRules().gl.ShowPanel(False)
                wfp.ShowPanel(False)        
        
    # Map entry
    elif mt == MGL_MAPENTRY:
        positionavailable = []
        positionorigin = []
        for i in range(0, MAXPLAYERS):
            positionavailable.append( msg[3+(i*2)] )
            positionorigin.append( msg[4+(i*2)] )
        GameRules().maplist[msg[1]] = MapEntry(msg[1], msg[2], positionavailable, positionorigin)
    elif mt == MGL_STARTMAPLIST:
        GameRules().maplist = {}
    elif mt == MGL_ENDMAPLIST:
        GameRules().gl.settingspanel.LoadMapList()
    elif mt == MGL_SETTINGS:
        GameRules().selectedmap = msg[1]
        gameruleschanged = (msg[2] != GameRules().selectedgamerule)
        GameRules().selectedgamerule = msg[2]
        GameRules().gl.SettingsChanged()
        if gameruleschanged:
            GameRules().RefreshCustomFields()
    elif mt == MGL_CUSTOMFIELD:
        cfname = msg[1]
        cfvalue = msg[2]
        if cfname in GameRules().customfields:
            GameRules().customfields[cfname][1] = cfvalue
            GameRules().gl.UpdateCustomField(cfname, cfvalue)
        else:
            PrintWarning('MGL_CUSTOMFIELD: Custom field %s not found for gamerules %s\n' % (cfname, GameRules().selectedgamerule))
            
@usermessage(messagename='glpkgslot')
def SendUpdateSlot(mt, slot, data, **kwargs):
    global state
    # Slot updating
    s = GameRules().slots[slot]
    if mt == MGL_INDEX:
        s.index = data
    elif mt == MGL_TYPE:
        s.type = data
    elif mt == MGL_COLOR:
        s.color = data
    elif mt == MGL_FACTION:
        s.faction = data
    elif mt == MGL_TEAM:
        s.team = data
    elif mt == MGL_READY:
        s.ready = data
    elif mt == MGL_POSITION:
        GameRules().gl.PositionChanged(s.slot, s.position, data)   
        s.position = data       
        
# Slot entry
class Slot(object):
    def __init__(self, slot):
        super(Slot, self).__init__()
        self.slot = slot
        self.player = None
    
    # Automatically send a message when a field changed
    __index = -1
    def __GetIndex(self):
        return self.__index
    def __SetIndex(self, index):
        if isserver and index != self.__index:
            SendUpdateSlot(MGL_INDEX, self.slot, index)
        self.__index = index
    index = property(__GetIndex, __SetIndex, None, "...")

    __type = GLTYPE_OPEN
    def __GetType(self):
        return self.__type
    def __SetType(self, type):
        if isserver and type != self.__type:
            SendUpdateSlot(MGL_TYPE, self.slot, type)
            GameRules().InvalidateReady()
        self.__type = type
    type = property(__GetType, __SetType, None, "...")
    
    __color = None
    def __GetColor(self):
        return self.__color
    def __SetColor(self, color):
        if isserver and color != self.__color:
            SendUpdateSlot(MGL_COLOR, self.slot, color)
        if self.__color != None:
            GameRules().colorfree[self.__color] = True
        self.__color = color
        if self.__color != None:
            GameRules().colorfree[color] = False
    color = property(__GetColor, __SetColor, None, "...")

    __faction = '-'
    def __GetFaction(self):
        return self.__faction
    def __SetFaction(self, faction):
        if isserver and faction != self.__faction:
            SendUpdateSlot(MGL_FACTION, self.slot, faction)
            GameRules().InvalidateReady()
        self.__faction = faction
    faction = property(__GetFaction, __SetFaction, None, "...")

    __team = 0
    def __GetTeam(self):
        return self.__team
    def __SetTeam(self, team):
        if isserver and team != self.__team:
            SendUpdateSlot(MGL_TEAM, self.slot, team)
            GameRules().InvalidateReady()
        self.__team = team
    team = property(__GetTeam, __SetTeam, None, "...")

    __ready = False
    def __GetReady(self):
        return self.__ready
    def __SetReady(self, ready):
        if isserver and ready != self.__ready:
            SendUpdateSlot(MGL_READY, self.slot, ready)
        self.__ready = ready
    ready = property(__GetReady, __SetReady, None, "...")
    
    __position = INVALID_POSITION
    def __GetPosition(self):
        return self.__position
    def __SetPosition(self, position):
        if isserver and position != self.__position:
            SendUpdateSlot(MGL_POSITION, self.slot, position)
        self.__position = position
    position = property(__GetPosition, __SetPosition, None, "...")    
    
    
# Map entry
class MapEntry(object):
    def __init__(self, mapname, numberpositions, positionavailable, positionorigin):
        super(MapEntry, self).__init__()
        
        self.mapname = mapname
        self.numberpositions = numberpositions
        self.positionavailable = positionavailable
        self.positionorigin = positionorigin
        
# A gamerule as manager    
class GameLobbyRules(CHL2WarsGameRules):
    def InitGamerules(self):
        global gamelobby_gamescheduled, state

        # Gamemaster, the one who decides the map and gamerules
        # Launches the game when everybody is ready
        self.gamemaster = None
        
        # Create slots
        self.slots = []
        for i in range(MAXPLAYERS):
            self.slots.append(Slot(i))
        self.colorfree = defaultdict( lambda : True )
        self.positionfree = [True]*MAXPLAYERS
        
        if isclient:
            self.gl = Gamelobby()  
        
        if state == GAMELOBBY_INACTIVE:
            self.state = GAMELOBBY_ACTIVE
        else:
            self.state = state
            
        if isserver:
            self.ReBuildMapList()
            self.SelectDefaultSettings()
        else:
            self.RefreshCustomFields()
            
        # Add players to slots
        # Might have initialized in the middle of the game, so we missed the connects
        if isserver:
            for i in range(1, gpGlobals.maxClients+1):
                player = UTIL_PlayerByIndex(i)
                if player == None:
                    continue
                self.ClientActive(player) 
                
        if isclient:
            # Changes playlist if specified by the new gamerules
            musicmanager.LoadPlayList(self.musicplaylist)

    def ShutdownGamerules(self):
        super(GameLobbyRules, self).ShutdownGamerules()

        if isclient:
            if self.gl:
                self.gl.ShowPanel(False) # Ensure it shuts down properly (unregister call backs)
                self.gl.DeletePanel()
                self.gl = None
            if wfp:
                wfp.ShowPanel(False)
        self.slots = [] # Make sure we don't modify this after shutdown
        
    def Precache(self):
        if self.state == GAMELOBBY_WAITINGFORPLAYERS:
            info = GetGamerulesInfo(gamelobby_gamerule)
            if info:
                gamerules = info.cls()
                gamerules.gamelobby_players = gamelobby_players
                gamerules.ParseCustomFields(gamelobby_customfields)
                gamerules.Precache()
          
        super(GameLobbyRules, self).Precache()
    
    # Update
    def Think(self): 
        if self.state == GAMELOBBY_WAITINGFORPLAYERS:
            self.UpdateWaitingForPlayers()
        else:
            self.UpdateGamelobby()
            
    def GetPlayerLobbyData(self, gamelobby_players, player):
        steamIDForPlayer = engine.GetClientSteamID(player)
        
        for i, glp in enumerate(gamelobby_players):
            if glp[0].type != GLTYPE_HUMAN:
                continue

            if steamIDForPlayer and glp[1]:
                return glp
            elif player.GetPlayerName() == glp[2]:
                return glp
        return None
        
    def UpdateWaitingForPlayers(self):
        global gamelobby_players
        if not srcmgr.levelinit:
            return
            
        if not self.waitforplayers_timeout:
            self.waitforplayers_timeout = gpGlobals.curtime + gl_playerloadtimeout.GetFloat()
                
        if self.waitforplayers_nextupdate > gpGlobals.curtime:
            return
            
        readylist = []
        
        counthumanplayers = 0
        for i, glp in enumerate(gamelobby_players):
            if glp[0].type != GLTYPE_HUMAN:
                continue        
            counthumanplayers += 1

        # Create ready list
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if player == None or not player.IsConnected():
                continue    
            glp = self.GetPlayerLobbyData(gamelobby_players, player)
            if glp:
                readylist.append(glp)
        
        if self.waitforplayers_timeout < gpGlobals.curtime:
            self.state = GAMELOBBY_INACTIVE 
            setup_game()
        elif len(readylist) == counthumanplayers:
            if self.waitforplayers_isready:
                if self.waitforplayers_start < gpGlobals.curtime:
                    self.state = GAMELOBBY_INACTIVE 
                    setup_game() 
            else:
                self.waitforplayers_isready = True
                self.waitforplayers_start = gpGlobals.curtime + 5.0
                GLLDSetStatusCD(self.waitforplayers_start)
        else:
            self.waitforplayers_isready = False
            GLLDSetStatusWFP(self.waitforplayers_timeout)
        
        # Send message with updated status of all players
        gamelobby_status = []
        for i, glp in enumerate(gamelobby_players):
            gamelobby_status.append(glp[2])
            if glp[0].type != GLTYPE_HUMAN:
                gamelobby_status.append('Ready')
                continue
            if glp in readylist:
                gamelobby_status.append('Ready')
            else:
                gamelobby_status.append('Loading...')

        GLLDPlayerStatusUpdate(gamelobby_status)
        
        self.waitforplayers_nextupdate = gpGlobals.curtime + 0.25

    def UpdateGamelobby(self):
        # Update player indices
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if player == None or not player.IsConnected():
                continue       
            playerslot = self.FindSlotPlayer(player)
            if playerslot != -1:
                self.slots[playerslot].index = player.entindex()
        
        # Invalidate gamemaster if the player goes None
        if self.gamemaster == None:
            self.AssignGameMaster()
        
        # Count down when a launch is scheduled
        if self.launchgamescheduled:
            if not self.IsEverybodyReady():
                self.launchgamescheduled = False
                self.ConsoleMsg('Game launch canceled')
                return
            if self.nextlaunchgamecountdecrement < gpGlobals.curtime:
                self.launchgamecountdown -= 1
                self.ConsoleMsg(str(self.launchgamecountdown)+'...')
                if self.launchgamecountdown == 0:
                    self.LaunchGame()
                self.nextlaunchgamecountdecrement = gpGlobals.curtime + 1.0
 
    def SendFullUpdateSlot(self, slotref, filter=None):
        SendUpdateSlot(MGL_INDEX, slotref.slot, slotref.index, filter=filter)
        SendUpdateSlot(MGL_TYPE, slotref.slot, slotref.type, filter=filter)
        SendUpdateSlot(MGL_COLOR, slotref.slot, slotref.color, filter=filter)
        SendUpdateSlot(MGL_FACTION, slotref.slot, slotref.faction, filter=filter)
        SendUpdateSlot(MGL_TEAM, slotref.slot, slotref.team, filter=filter)
        SendUpdateSlot(MGL_READY, slotref.slot, slotref.ready, filter=filter)
        
    def ClientActive(self, client):
        super(GameLobbyRules, self).ClientActive(client)
        
        self.UpdateHudPlayers()
        
        # Send full update
        filter = CSingleUserRecipientFilter(client)
        filter.MakeReliable()
        for s in self.slots:
            self.SendFullUpdateSlot(s, filter)
        self.SendMapList(filter)
        self.SendFullSettingsUpdate(filter)
        self.SendGamemaster(filter)
        self.SendState(filter)
        
        # Assign player to slot, fallback to spectating.
        if not self.AssignPlayerToFreeSlot(client):
            self.GLPlayerSpectate(client)
   
    def ClientDisconnected(self, client):
        super(GameLobbyRules, self).ClientDisconnected(client)
        idx = self.FindSlotPlayer(client)
        if idx != -1:
            self.ClearSlot(idx)
            
    # CHAT
    def ConsoleMsg(self, message):
        filter = CReliableBroadcastRecipientFilter()
        UTIL_SayTextFilter(filter, message, None, True)
             
    # Player slots
    def GLType(self, player, playerslot, args):
        if args.ArgC() < 3:
            return
            
        slotidx = int(args[2])  # Change requested for this slot
        type = int(args[1])
        
        if type == GLTYPE_OPEN:
            if player == self.gamemaster:
                if self.slots[slotidx].type == GLTYPE_CLOSED:
                    self.slots[slotidx].type = GLTYPE_OPEN
                elif self.slots[slotidx].type == GLTYPE_CPU:
                    self.ClearSlot(slotidx)
                    self.slots[slotidx].type = GLTYPE_OPEN
            else:
                PrintWarning("Player trying to open slot it is not allowed to do!\n")
        elif type == GLTYPE_CLOSED:
            # Only the gamemaster can close a slot if there is no player in the slot or we are the gamemaster the player is a CPU
            if self.gamemaster == player:
                if ( self.slots[slotidx].type == GLTYPE_OPEN or
                        (self.slots[slotidx].type == GLTYPE_CPU and 
                        self.gamemaster == player)):
                    self.ClearSlot( slotidx )
                    self.slots[slotidx].type = GLTYPE_CLOSED
            else:
                PrintWarning("Player trying to close slot it is not allowed to do!\n")
        elif type == GLTYPE_HUMAN:
            # We can only take the slot if it is open or if it is closed and we are the gamemaster
            if( self.slots[slotidx].type == GLTYPE_OPEN or 
                    (self.slots[slotidx].type == GLTYPE_CLOSED and self.gamemaster == player)):
                if playerslot != -1:
                    self.ClearSlot( playerslot )
                self.AddPlayerToSlot(player, slotidx)
            else:
                PrintWarning("Player trying to occupy a slot that is already taken or closed!\n")  
        elif type == GLTYPE_CPU:
            #self.ConsoleMsg("Adding a CPU is not supported yet")
            if self.gamemaster != player:
                PrintWarning("Player trying to close slot it is not allowed to do!\n")
                return
            # Only the gamemaster can add a cpu (if the slot is open or closed)
            if self.slots[slotidx].type == GLTYPE_OPEN or self.slots[slotidx].type == GLTYPE_CLOSED:
                self.AddCPUToSlot(slotidx)
            else:
                PrintWarning("Gamemaster trying to add a cpu to a slot that is already taken!\n")              

    def GLColor(self, player, playerslot, args):
        if args.ArgC() < 3:
            return
    
        slotidx = int(args[2])  # Change requested for this slot
        colorname = args[1]

        # Check valid
        # Can only change the color of my own slot
        # Additionaly if we are the gamemaster we can change the cpu's color
        if playerslot == -1:
            PrintWarning("GLColor: Player has no slot.\n")
            return  
        if slotidx != playerslot and player != self.gamemaster and self.slots[slotidx].type != GLTYPE_HUMAN:
            PrintWarning("GLColor: Player requesting color for a slot the player is not allowed to do!\n")
            return    

        # Check color free
        if self.IsColorFree(colorname) == False:
            PrintWarning("GLColor: Player requesting color that is already in use!\n")
            return
        
        # Take color
        self.slots[slotidx].color = colorname

    def GLFaction(self, player, playerslot, args):
        if args.ArgC() < 3:
            return
    
        slotidx = int(args[2])  # Change requested for this slot
        if playerslot == -1:
            PrintWarning("GLFaction: Player has no slot.\n")
            return  
        if slotidx != playerslot and player != self.gamemaster and self.slots[slotidx].type != GLTYPE_HUMAN:
            PrintWarning("Player requesting team for a slot the player is not allowed to do!\n")
            return
        self.slots[slotidx].faction = args[1]  
        self.CheckFaction(slotidx)
            
    def GLTeam(self, player, playerslot, args):
        if args.ArgC() < 3:
            return
    
        slotidx = int(args[2])  # Change requested for this slot
        if playerslot == -1:
            PrintWarning("GLTeam: Player has no slot.\n")
            return   
        if slotidx != playerslot and player != self.gamemaster and self.slots[slotidx].type != GLTYPE_HUMAN:
            PrintWarning("GLTeam: Player requesting team for a slot the player is not allowed to do!\n")
            return
        self.slots[slotidx].team = int(args[1]) 
         
    def GLReady(self, player, playerslot, args):
        if args.ArgC() < 3 or player == None:
            return

        slotidx = int(args[2])  # Change requested for this slot     
        if playerslot == -1:
            PrintWarning("GLReady: Player has no slot.\n")
            return        
        if slotidx != playerslot:
            PrintWarning("GLReady: Player requesting ready for a slot the player is not allowed to do!\n")
            return
        if player == self.gamemaster:
            PrintWarning('GLReady: The gamemaster is ALWAYS ready\n')
            return
        self.slots[slotidx].ready = int(args[1])
        
    def FindUnsetCPUPositionSlot(self):
        for i in range(0, MAXPLAYERS):
            if self.slots[i].type == GLTYPE_CPU and self.slots[i].position == INVALID_POSITION:
                return i
        return -1
        
    def FindSlotForPosition(self, position):
        for i in range(0, MAXPLAYERS):
            if self.slots[i].position == position:
                return i
        return -1
        
    def GLPosition(self, player, playerslot, args):
        if args.ArgC() < 3 or player == None:
            return        
            
        position = int(args[1])
        slotidx = int(args[2])  # Change requested for this slot
        if playerslot == -1:
            PrintWarning("GLPosition: Player has no slot.\n")
            return
        if slotidx != playerslot:
            PrintWarning("GLPosition: Player requesting position for a slot the player is not allowed to do!\n")
            return
        if self.maplist[self.selectedmap].positionavailable[position] == False:
            PrintWarning("GLPosition: Player requesting a not available position\n")
            return        
            
        if self.positionfree[position] == False:
            # Position is mine: free it
            if self.slots[slotidx].position == position:
                self.SetPosition(slotidx, INVALID_POSITION)   # Release my position
                return
            
            # Position is of a cpu player and we are the gamemaster: free it
            positionslot = self.FindSlotForPosition(position)
            if positionslot != -1 and player == self.gamemaster and self.slots[positionslot].type == GLTYPE_CPU:
                self.SetPosition(positionslot, INVALID_POSITION)   # Release cpu position
                return
        else:
            # We have no position
            if self.slots[slotidx].position == INVALID_POSITION:
                self.SetPosition(slotidx, position)
                return
                
            # We already got a position. Try to find one for a cpu in case we are the gamemaster.
            cpuslotidx = self.FindUnsetCPUPositionSlot()
            if player == self.gamemaster and cpuslotidx != -1:
                self.SetPosition(cpuslotidx, position)
                return
                
            # Change our own position to the free slot
            self.SetPosition(slotidx, position)
        
    # Schedule a game launch
    def GLScheduleLaunchGame(self, player):
        # Player must be gamemaster
        if player != self.gamemaster:
            PrintWarning("Player trying to launch the game while not allowed to do so.\n")
            return     
            
        info = GetGamerulesInfo(self.selectedgamerule)
            
        # Must have a minimum number of players
        if not gl_skipplayercheck.GetBool() and self.CountPlayers() < info.minplayers:
            self.ConsoleMsg('This gamemode requires at least %d players' % (info.minplayers))
            return
            
        # Does this gamemode allow all players on the same team?
        if not info.allowallsameteam:
            teams = set([])
            for i in range(0, MAXPLAYERS):
                if self.slots[i].type == GLTYPE_HUMAN or self.slots[i].type == GLTYPE_CPU:
                    teams.add(self.slots[i].team)
                    
            if len(teams) == 1 and list(teams)[0] != TEAM_UNASSIGNED:
                self.ConsoleMsg('This gamemode does not allow all players on the same team')
                return
            
        # Make sure everybody has a position
        for i in range(0, MAXPLAYERS):
            if self.slots[i].type == GLTYPE_HUMAN or self.slots[i].type == GLTYPE_CPU:
                if self.slots[i].position == INVALID_POSITION:
                    self.SetPosition(i, self.FindFirstFreePosition())
                    
        # Everybody must be ready
        if not self.IsEverybodyReady():
            self.ConsoleMsg('Some players are not ready yet.')
            return
            
        # If there is only one player we can directly launch the game!
        players = UTIL_GetPlayers()
        if len(players) == 1:
            self.LaunchGame()
            return
 
        self.launchgamescheduled = True
        self.launchgamecountdown = 3
        self.nextlaunchgamecountdecrement = gpGlobals.curtime + 1.0
        self.ConsoleMsg(str(self.launchgamecountdown)+'...')    
 
    def GLSettings(self, player, playerslot, args):
        # Player must be gamemaster
        if player != self.gamemaster:
            PrintWarning("Player trying to apply settings while not allowed to do so.\n")
            return    
            
        self.selectedmap = args[1]
        gameruleschanged = args[2] != self.selectedgamerule
        self.selectedgamerule = args[2]
        GameLobbyRules.prevselectedgamerule = self.selectedgamerule
        self.InvalidateReady()
        if gameruleschanged:
            self.RefreshCustomFields()
            self.InvalidatePlayers()
        filter = CReliableBroadcastRecipientFilter()
        self.SendSettings(filter)  
        
    def GLSelectLeader(self, player, playerslot, args):
        # Player must be gamemaster
        if player != self.gamemaster:
            PrintWarning("Player trying to select a new gamemaster while not allowed to do so.\n")
            return  
            
        # Find the new selected gamemaster
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if not player:
                continue
            if player.GetPlayerName() == args.ArgS():
                self.gamemaster = player
                self.ConsoleMsg('Player %s is now gamemaster' % (player.GetPlayerName()))
                break
        
        
    def GLCustom(self, player, playerslot, args):
        # Player must be gamemaster
        if player != self.gamemaster:
            PrintWarning("Player trying to apply settings while not allowed to do so.\n")
            return  
        cfname = args[1]
        cfvalue = args[2]
        
        if cfname not in self.customfields:
            PrintWarning('GLCustom: Custom field %s not found for gamerules %s\n' % (cfname, self.selectedgamerule))
            return
            
        cf = self.customfields[cfname]
        cf[1] = cfvalue
        filter = CReliableBroadcastRecipientFilter()
        self.SendCustomField(cfname, filter)  
        
    def ClientCommand(self, player, args):
        # Here we will proces the actions of the players ( selecting a different slot, color, position, etc )
        # Client can send commands with src_gameinterface.ServerCommand
        # Return 'True' if you handled the command
        
        slotplayer = self.FindSlotPlayer(player)    # The slot of the player executing the command
        if args[0] == 'gl_type':
            self.GLType(player, slotplayer, args)
            return True
        elif args[0] == 'gl_color':
            self.GLColor(player, slotplayer, args)
            return True
        elif args[0] == 'gl_faction':
            self.GLFaction(player, slotplayer, args)
            return True
        elif args[0] == 'gl_team':
            self.GLTeam(player, slotplayer, args)
            return True   
        elif args[0] == 'gl_ready':
            self.GLReady(player, slotplayer, args)
            return True
        elif args[0] == 'gl_position':
            self.GLPosition(player, slotplayer, args)
            return True 
        elif args[0] == 'gl_spectate':
            self.GLPlayerSpectate(player)
            return True
        elif args[0] == 'gl_launch':
            self.GLScheduleLaunchGame(player)
            return True
        elif args[0] == 'gl_settings':
            self.GLSettings(player, slotplayer, args)
            return True
        elif args[0] == 'gl_selectleader':
            self.GLSelectLeader(player, slotplayer, args)
            return True
        elif args[0] == 'gl_custom':
            self.GLCustom(player, slotplayer, args)
            return True
            
        return super(GameLobbyRules, self).ClientCommand(player, args)
    
    if isserver:
        # Map list
        def ReBuildMapList(self):
            self.maplist = {}
            
            # Make a list of all maps
            if gl_usemaplist.GetBool():
                try:
                    f = open('maplist.txt')
                    maplist = f.readlines()
                    maplist = map(str.rstrip, maplist)
                    f.close()
                except:
                    PrintWarning('ReBuildMapList: Failed to open maplist.txt\n')
                    return
            else:
                maplist = []
                for f in os.listdir("maps"):
                    if os.path.isdir(f):
                        continue
                    base, ext = os.path.splitext(f)
                    if ext != '.bsp':
                        continue
                    maplist.append(base)

            for mapname in maplist:
                mapname = mapname.rstrip()
                
                # Init list with info about positions
                positionavailable = [False]*MAXPLAYERS
                positionorigin = [None]*MAXPLAYERS
                
                # Get entities
                maplocation = 'maps\\'+mapname+'.bsp'
                try:
                    blocks, blocksbyclass = readmap.ParseMapEntitiesToBlocks( maplocation )
                except:
                    PrintWarning('Invalid map ' + maplocation + ' in maplist.txt\n')
                    continue
                    
                # Parse locations
                numberpositions = 0
                for i, startent in enumerate(blocksbyclass['info_start_wars']):
                    if not positionavailable[i]:
                        numberpositions += 1
                        positionavailable[i] = True
                        positionorigin[i] = startent['origin'][0]   # Just keep it in string form for sending to the client
                
                # Add to list
                self.maplist[mapname] = MapEntry( mapname, numberpositions, positionavailable, positionorigin )

            # Inform client
            filter = CReliableBroadcastRecipientFilter()
            self.SendMapList(filter)
            
        def SendMapList(self, filter):
            ClientGamelobbyUpdate([MGL_STARTMAPLIST], filter=filter)
            for k, mapentry in self.maplist.iteritems():
                message = [MGL_MAPENTRY, mapentry.mapname, mapentry.numberpositions] 
                for i in range(0, MAXPLAYERS):
                    message.extend([mapentry.positionavailable[i], mapentry.positionorigin[i]])
                ClientGamelobbyUpdate(message, filter=filter)
            ClientGamelobbyUpdate([MGL_ENDMAPLIST], filter=filter)
            
    __selectedmap = None
    def __GetSelectedMap(self):
        return self.__selectedmap
    def __SetSelectedMap(self, selectedmap):
        if self.__selectedmap == selectedmap or selectedmap not in self.maplist.keys():
            return
        self.__selectedmap = selectedmap
        if isclient:
            return
        # Close too many slots. Move players in those slots to spectators
        for i, slot in enumerate(self.slots):
            if i < self.maplist[selectedmap].numberpositions:
                if slot.type == GLTYPE_NOTAVAILABLE:
                    slot.type = GLTYPE_OPEN
            else:
                if slot.type == GLTYPE_HUMAN:
                    self.GLPlayerSpectate(slot.player)
                    slot.type = GLTYPE_NOTAVAILABLE
                elif slot.type != GLTYPE_NOTAVAILABLE:
                    self.ClearSlot(i)
                    slot.type = GLTYPE_NOTAVAILABLE
        
    selectedmap = property(__GetSelectedMap, __SetSelectedMap, None, "Set the selected map")  
            
    def SelectDefaultMap(self):
        info = GetGamerulesInfo(self.selectedgamerule)
        for k, v in self.maplist.iteritems():
            if not info.mapfilter.match(v.mapname):
                continue
            return k
        return None
            
    def SelectDefaultSettings(self):
        rules = dbgamerules.keys()
        rules.remove('gamelobbyrules')
        if not rules:
            raise Exception('No gamerules')
            
        if GameLobbyRules.prevselectedgamerule and GameLobbyRules.prevselectedgamerule in rules:
            self.selectedgamerule = GameLobbyRules.prevselectedgamerule
        else:
            GameLobbyRules.prevselectedgamerule = self.selectedgamerule
            self.selectedgamerule = rules[0]

        self.RefreshCustomFields()
        self.selectedmap = self.SelectDefaultMap()
        self.InvalidateReady()
        self.InvalidatePlayers()
        
        filter = CReliableBroadcastRecipientFilter()
        self.SendFullSettingsUpdate(filter)

    def RefreshCustomFields(self):
        """ Given the selected gamerules update our current custom fields
            Set the default values """
        # Each element in the custom field list has the following format:
        # (type, name, value, type specific... )
        self.customfields = {}  # TODO: merge old settings
        info = GetGamerulesInfo(self.selectedgamerule)
        if not info:
            return
            
        try:
            GetCustomFields = info.cls.GetCustomFields
        except:
            return
        self.customfields = dict(GetCustomFields())
        
    def SendFullSettingsUpdate(self, filter):
        self.SendSettings(filter)
        self.SendFullCustomFieldsUpdate(filter)
        
    def SendSettings(self, filter):
        ClientGamelobbyUpdate([MGL_SETTINGS, self.selectedmap, self.selectedgamerule], filter=filter)
        
    def SendFullCustomFieldsUpdate(self, filter):
        for name in self.customfields.iterkeys():
            self.SendCustomField(name, filter)

    def SendCustomField(self, cfname, filter):
        if cfname not in self.customfields:
            PrintWarning('SendCustomField: Custom field %s not found for gamerules %s' % (cfname, self.selectedgamerule))
            return

        ClientGamelobbyUpdate([MGL_CUSTOMFIELD, cfname, self.customfields[cfname][1]], filter=filter)
        
    # Slot manage methods
    def AssignPlayerToFreeSlot(self, player):
        for i, s in enumerate(self.slots):
            if s.type == GLTYPE_OPEN:
                self.AddPlayerToSlot(player, i)
                return True
        return False
        
    def ClearSlot(self, idxslot):
        self.slots[idxslot].player = None
        self.slots[idxslot].index = -1
        self.slots[idxslot].type = GLTYPE_OPEN   
        self.slots[idxslot].color = None
        self.slots[idxslot].team = TEAM_UNASSIGNED
        self.slots[idxslot].ready = 0
        self.SetPosition(idxslot, INVALID_POSITION)
        
    def AddPlayerToSlot(self, player, idxslot):
        player.ChangeTeam( TEAM_UNASSIGNED )
        self.slots[idxslot].player = player
        self.slots[idxslot].index = player.entindex()
        self.slots[idxslot].type = GLTYPE_HUMAN
        self.slots[idxslot].color = self.FindFreeColor()
        self.slots[idxslot].faction = self.SelectDefaultFaction()
        
        if self.gamemaster == None:
            self.gamemaster = player
        if self.gamemaster == player:
            self.slots[idxslot].ready = True
            
    def AddCPUToSlot(self, idxslot):
        self.slots[idxslot].player = None
        self.slots[idxslot].index = -1
        self.slots[idxslot].type = GLTYPE_CPU
        self.slots[idxslot].color = self.FindFreeColor()
        self.slots[idxslot].faction = self.SelectDefaultFaction()  
        self.slots[idxslot].ready = True        
        
    def FindSlotPlayer(self, player):
        for i, s in enumerate(self.slots):
            if s.player == player:
                return i
        return -1
        
    def FindSlotPlayerByIndex(self, index):
        for i, s in enumerate(self.slots):
            if s.index == index:
                return i
        return -1
        
    def CloseSlot(self, idxslot):
        if self.slots[idxslot].player:
            self.GLPlayerSpectate(self.slots[idxslot].player)
        self.slots[idxslot].type = GLTYPE_CLOSED
        
    def InvalidatePlayers(self):
        """ Called when the gamerules or gamepackages changed.
            Need to check if the settings of each player is still valid. """
        # Slam factions to allowed factions
        for i in range(MAXPLAYERS):
            self.CheckFaction(i)
            
        # Clear slot if cpu while cpus are not supported
        info = GetGamerulesInfo(self.selectedgamerule)
        if not info.supportcpu:
            for i in range(MAXPLAYERS):
                if self.slots[i].type == GLTYPE_CPU:
                    self.ClearSlot(i)
        
    def SelectDefaultFaction(self):
        info = GetGamerulesInfo(self.selectedgamerule)
        for faction in dbfactions.keys():
            if not info.factionfilter.match(faction):
                continue
            return faction
        return None

    def CheckFaction(self, idx):
        """ Checks if the faction exists and if the factions is not filtered away by the gamerules """
        info = GetGamerulesInfo(self.selectedgamerule)
        if not info.factionfilter.match(self.slots[idx].faction) or self.slots[idx].faction not in dbfactions.keys():
            self.slots[idx].faction = self.SelectDefaultFaction()
        
    def GLPlayerSpectate(self, player):
        player.ChangeTeam( TEAM_SPECTATOR )
        slotidx = self.FindSlotPlayer(player)
        if slotidx != -1:
            self.ClearSlot(slotidx)
        #if player == self.gamemaster:
        #    self.gamemaster = None
           
    # Color management
    def IsColorFree(self, colorname):
        # Valid color?
        if GL_COLORS.get(colorname, None) == None:
            return False
        
        # Check free
        return self.colorfree[colorname]
        
    def FindFreeColor(self):
        freecolors = []
        for colorname, color in GL_COLORS.iteritems():
            if self.colorfree[colorname]:
                freecolors.append(colorname)
        if len(freecolors) == 0:
            return None     # <- Should not happen
        return freecolors[random.randint(0, len(freecolors)-1)]

    # Ready?
    def IsEverybodyReady(self):
        if gl_skipplayercheck.GetBool():
            return True
        for i in range(MAXPLAYERS):
            if self.slots[i].type != GLTYPE_HUMAN:
                continue
            if self.slots[i].player and self.slots[i].player.IsBot():
                return True
            if self.slots[i].ready == False:
                return False
        return True
        
    def InvalidateReady(self):
        for i in range(MAXPLAYERS):
            if self.slots[i].type == GLTYPE_CPU or self.slots[i].player == self.gamemaster:
                continue
            self.slots[i].ready = False
            
    def CountPlayers(self):
        c = 0
        for i in range(MAXPLAYERS):
            if self.slots[i].type != GLTYPE_HUMAN and self.slots[i].type != GLTYPE_CPU:
                continue
            c += 1
        return c
            
    # Position
    def SetPosition(self, idxslot, newposition, invalidateready=True):
        oldposition = self.slots[idxslot].position
        if oldposition == newposition:
            return
            
        # Two cases: new position is INVALID_POSITION -> clear old position. Otherwise try to take new position if valid
        if newposition == INVALID_POSITION:
            assert( self.positionfree[oldposition] == False )
            self.positionfree[oldposition] = True
            self.slots[idxslot].position = INVALID_POSITION
        else:
            if self.positionfree[newposition] == False:
                return
            if self.maplist[self.selectedmap].positionavailable[newposition] == False:
                return
            if oldposition >= 0 and oldposition < MAXPLAYERS:
                assert( self.positionfree[oldposition] == False )
                self.positionfree[oldposition] = True
                self.slots[idxslot].position = INVALID_POSITION
            self.positionfree[newposition] = False
            self.slots[idxslot].position = newposition
            
        if invalidateready:
            self.InvalidateReady()
        
    def FindFirstFreePosition(self):
        for i in range(0, MAXPLAYERS):
            if not self.maplist[self.selectedmap].positionavailable[i]:
                continue
            if self.positionfree[i]:
                return i
        return INVALID_POSITION
        
    # Launch
    def LaunchGame(self):
        if self.selectedmap == None:
            PrintWarning("Trying to launch game without a valid map selected!\n")
            return
        self.SaveData()
        
        # Only update the client state variable for the loading screen
        #self.state = GAMELOBBY_WAITINGFORPLAYERS
        ClientGamelobbyUpdate([MGL_STATE, GAMELOBBY_WAITINGFORPLAYERS])
        
        # Send list of players to all clients
        gamelobby_players = []
        for i in range(MAXPLAYERS):
            if self.slots[i].type == GLTYPE_HUMAN:     
                gamelobby_players.append(self.slots[i].player.GetPlayerName())
                gamelobby_players.append('Loading...')
            elif self.slots[i].type == GLTYPE_CPU:
                gamelobby_players.append('CPU')
                gamelobby_players.append('Ready')
        
        GLLDSetStatusWFP(self.waitforplayers_timeout)
        GLLDPlayerStatusUpdate(gamelobby_players)
        
        print('Launching map from gamelobby: %s' % (self.selectedmap))
        engine.ChangeLevel(self.selectedmap)
        
    def SaveData(self):
        global gamelobby_gamescheduled, gamelobby_gamerule, gamelobby_players, gamelobby_customfields
        gamelobby_gamescheduled = True
        gamelobby_gamerule = self.selectedgamerule
        gamelobby_customfields = self.customfields

        # For each player save the steam ID with the slot settings
        saveplayerdata = True
        gamelobby_players = []
        for i in range(MAXPLAYERS):
            if self.slots[i].type == GLTYPE_HUMAN and saveplayerdata:
                steamIDForPlayer = engine.GetClientSteamID(self.slots[i].player)
                if not steamIDForPlayer:
                    PrintWarning("Failed to retrieve SteamID for player %s.\n" % self.slots[i].player.GetPlayerName())
                #print 'Saving steamid of player %s (id: %d)' % (self.slots[i].player.GetPlayerName(), steamIDForPlayer.GetAccountID())
                gamelobby_players.append( (self.slots[i], steamIDForPlayer, self.slots[i].player.GetPlayerName()) )
            elif self.slots[i].type == GLTYPE_CPU:
                gamelobby_players.append( (self.slots[i], None, 'CPU %d' % (i+1)) )
                
    # Gamemaster
    def SendGamemaster(self, filter):
        ClientGamelobbyUpdate([MGL_GAMEMASTERINDEX, self.gamemasterindex], filter=filter)
            
    __gamemaster = None
    def __GetGameMaster(self):
        return self.__gamemaster
    def __SetGameMaster(self, gamemaster):
        if gamemaster == self.__gamemaster:
            return
        self.__gamemaster = gamemaster
        if gamemaster:
            self.gamemasterindex = gamemaster.entindex()   
            slotidx = self.FindSlotPlayer(gamemaster)
            #assert(slotidx != -1)
            if slotidx != -1:
                self.slots[slotidx].ready = True
        else:
            self.gamemasterindex = None
            
        if isserver:
            filter = CReliableBroadcastRecipientFilter()
            self.SendGamemaster(filter)

    gamemaster = property(__GetGameMaster, __SetGameMaster, None, "...")  
    gamemasterindex = None
         
    def AssignGameMaster(self):
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if not player:# or self.FindSlotPlayer(player) == -1:
                continue   
            self.gamemaster = player
            return
            
    def UpdateHudPlayers(self):
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if not player:
                continue  
            if GAMELOBBY_ACTIVE == self.state:
                player.AddHudHiddenBits(HIDEHUD_ALL)
            elif GAMELOBBY_WAITINGFORPLAYERS == self.state:
                player.RemoveHudHiddenBits(HIDEHUD_ALL)
                player.AddHudHiddenBits(HIDEHUD_STRATEGIC)
            else:
                player.RemoveHudHiddenBits(HIDEHUD_ALL)
                player.RemoveHudHiddenBits(HIDEHUD_STRATEGIC)
            
    # State
    __state = 0
    def __GetState(self):
        return self.__state
    def __SetState(self, state):
        if state == self.__state:
            return
        self.__state = state
     
        if isserver:
            self.UpdateHudPlayers()
            filter = CReliableBroadcastRecipientFilter()
            self.SendState(filter)

    state = property(__GetState, __SetState, None, "...")  
    
    def SendState(self, filter):
        ClientGamelobbyUpdate([MGL_STATE, self.state], filter=filter)
    
    gl = None  
    maplist = {}
    launchgamescheduled = False
    launchgamecountdown = 3
    nextlaunchgamecountdecrement = 0.0
    
    waitforplayers_timeout = None
    waitforplayers_start = 0.0
    waitforplayers_isready = False
    waitforplayers_nextupdate = 0.0
    
    customfields = {}
    prevselectedgamerule = None
    selectedgamerule = None
    
    musicplaylist = [
        'music/Atmospheric Disturbances.mp3',
    ]
              
class GLPKGInfo(GamerulesInfo):
    name = "gamelobbyrules"
    cls = GameLobbyRules
