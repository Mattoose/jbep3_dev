from srcbase import FL_FROZEN, MAX_PLAYERS, Color
from vmath import Vector, QAngle, vec3_origin, AngleVectors
from collections import defaultdict
import sys
import traceback
from datetime import datetime
import os
import random
from xml.dom.minidom import Document

import playermgr
import srcmgr

#from glpkg.gamelobby_shared import *

from core.dispatch import receiver
from core.signals import FireSignalRobust, postlevelshutdown
from core.usermessages import usermessage

from info import GetGamerulesInfo
from gamerules import CJBGameRules, GameRules, gamerules, LAST_SHARED_TEAM, TeamRegister
from gameinterface import ConVarRef, engine, ConVar, concommand, FCVAR_CHEAT
if isserver:
    from utils import (UTIL_EntityByIndex, UTIL_PlayerByIndex, UTIL_FindPosition, FindPositionInfo, UTIL_SayTextAll, 
                       UTIL_SayText, UTIL_GetPlayers, UTIL_GetCommandClient)
    from entities import gEntList, DispatchSpawn, CreateEntityByName
    from playermgr import InfoStartWars
    from gameinterface import CRecipientFilter, EAccountType
#else:
#    from vgui import CHudElementHelper
#    from vgui.votedialog import VoteDialog
    
mp_chattime = ConVarRef('mp_chattime')
mp_timelimit = ConVarRef('mp_timelimit')
    
PANEL_SCOREBOARD = "scores"

# Client updating of the vote system
if isclient:
    votedialog = None

    @receiver(postlevelshutdown)
    def OnShutdownCloseDialog(sender, **kwargs):
        global votedialog
        if votedialog:
            votedialog.DeletePanel()
            votedialog = None

@usermessage(messagename='core_startvote')
def ClientStartVote(**kwargs):
    global votedialog
    if votedialog:
        votedialog.DeletePanel()
    votedialog = VoteDialog()
    
@usermessage()
def ClientEndVote(**kwargs):
    global votedialog
    if votedialog:
        votedialog.DeletePanel()
        votedialog = None
        
@usermessage()
def ClientUpdateVotes(yesvotes, novotes, **kwargs):
    global votedialog
    votedialog.yesvotes = yesvotes
    votedialog.novotes = novotes
    votedialog.question.SetText( "Return to lobby? (yes: %d, no: %d)" % (votedialog.yesvotes, votedialog.novotes) )
    

# Base Gamerules
class WarsBaseGameRules(CJBGameRules):
    def __init__(self):
        super(WarsBaseGameRules, self).__init__()
                
    def Precache(self):
        super(WarsBaseGameRules, self).Precache()

    def InitGamerules(self):
        """ Initializes the gamerules.
        
            Sets the default colors for the different players 
            (in case not launched from the gamelobby).
            Initializes the gamerules specific hud elements.
        """
        super(WarsBaseGameRules, self).InitGamerules()
        self.InitTeams()

                
    def ShutdownGamerules(self):
        """ Shutdown gamerules.
        
            Clears the gamerules specific hud elements.
        """
        super(WarsBaseGameRules, self).ShutdownGamerules()
        
    def InitTeams(self):
        super(WarsBaseGameRules, self).InitTeams()
        TeamRegister( LAST_SHARED_TEAM + 1, "TEST TEAM" )


    def Think(self):
        """ Updates the gamerules . """
        
        print("Hello World")
        
        self.UpdateVoiceManager()
    
        if self.CheckGameOver():
            return
            
        self.UpdateGLVoting()
                
        timelimit = mp_timelimit.GetFloat() * 60
                
        if timelimit != 0 and gpGlobals.curtime >= timelimit:
            self.GoToIntermission()
            return
        
    def GoToIntermission(self, showscoreboard=True):
        """ Set gameover to True and start intermission (show scoreboard). """
        if self.gameover:
            return

        self.gameover = True

        self.intermissionendtime = gpGlobals.curtime + mp_chattime.GetInt()

        if showscoreboard:
            for i in range(0, MAX_PLAYERS):
                player = UTIL_PlayerByIndex(i)

                if not player:
                    continue

                player.ShowViewPortPanel(PANEL_SCOREBOARD)
                player.AddFlag(FL_FROZEN)
            
    def EndGame(self, winners, losers, observers=[]):
        """ Goes in intermission and shows appropriate 
            messages to winners and losers."""
        self.GoToIntermission(showscoreboard=False)
                
    def GetPlayerID(self, player):
        steamIDForPlayer = engine.GetClientSteamID(player)
        if steamIDForPlayer:
            return steamIDForPlayer
        return player.GetPlayerName()
        
    def CheckGameOver(self):
        """ If the game is over (self.gameover == True), change to
            the next map after the intermission time. """
        if self.gameover:   # someone else quit the game already
            # check to see if we should change levels now
            if self.intermissionendtime < gpGlobals.curtime:
                self.ChangeLevel()  # intermission is over
            return True
        return False
                
    def ChangeToGamelobby(self):
        print( "CHANGE LEVEL: gamelobby" )
        engine.ChangeLevel( 'gamelobby', None )
        
    def ClientCommand(self, player, args):
        """ Proces hud commands """
        command = args[0]
        
        if command == 'gl_callvote':
            self.CallGLVote(player)
            return True
        elif command == 'gl_vote':
            self.ProcessGLVote(player, args[1])
            return True
            
        return super(WarsBaseGameRules, self).ClientCommand(player, args)
            
    def FindPlayerSpawnSpot(self, player):
        """ Finds a start spot for the player.
        
            By default looks for info_player_wars with the matching ownernumber.
            If there is no such spot look for info_start_wars and then create
            a start spot.
        """
                
        return player.EntSelectSpawnPoint()
                       
    def GetPlayerSpawnSpot(self, player):
        """ Tries to pick a start point according to the ownernumber of the player """  
        # Because the ownernumber is required, we need to setup the player here.
        self.SetupPlayer(player)
        
        spawnspot = self.FindPlayerSpawnSpot(player)
        
        if spawnspot:
            #player.SetLocalOrigin(spawnspot.GetAbsOrigin() + Vector(0,0,1))
            player.SnapCameraTo(spawnspot.GetAbsOrigin() + Vector(0,0,1))
            player.SetAbsVelocity(vec3_origin)
            player.SetLocalAngles(QAngle(65, 135, 0))
            player.SnapEyeAngles(QAngle(65, 135, 0))
            #player.SetLocalAngles(spawnspot.GetLocalAngles())
            #player.SnapEyeAngles(spawnspot.GetLocalAngles())

        return spawnspot
        
    def SetupPlayer(self, player):
        # First try to apply gamelobby data
        # Otherwise use the first free owner numer
        print("SETUP PLAYER")
        player.ChangeTeam(LAST_SHARED_TEAM + 1, "Team Test")
                
#        if player.GetOwnerNumber() == 0:
#            if self.gamelobby_players:
#                if not self.ApplyGamelobbyDataToPlayer(self.gamelobby_players, player):
#                    if self.info.allowplayerjoiningame:
#                        player.ChangeTeam(TEAM_UNASSIGNED)
#                    else:
#                        player.SetOwnerNumber(0)
#                        player.ChangeTeam(TEAM_SPECTATOR)
#            else:
#                player.ChangeTeam(TEAM_UNASSIGNED)
           
        
    def RenderSteamID(self, steamid):
        type = steamid.GetEAccountType()
        if type == EAccountType.k_EAccountTypeInvalid or type == EAccountType.k_EAccountTypeIndividual:
            return 'STEAM_0:%u:%u' % (1 if (steamid.GetAccountID() % 2) else 0, steamid.GetAccountID()/2)
        return '%llu' % (steamid.ConvertToUint64())
      
    
    #
    # Voting
    #
    def CallGLVote(self, player):
        if self.voting:
            return
        if self.nextvoteallow > gpGlobals.curtime:
            UTIL_SayText("Can't call to gamelobby vote for another %d seconds!" % (int(self.nextvoteallow-gpGlobals.curtime)), player)
            return
    
        self.votes = defaultdict( lambda : 0 )
        self.voted = []
        self.totalvotes = 0
        
        self.voting = True
        self.endvoting = gpGlobals.curtime + 30.0
        
        UTIL_SayTextAll('Gamelobby vote initiated by %s' % (player.GetPlayerName()))
        
        ClientStartVote()
                
    def EndGLVote(self):
        self.voting = False
        self.nextvoteallow = gpGlobals.curtime + 60.0
        
        ClientEndVote()
            
        if self.votes['yes'] > self.votes['no']:
            UTIL_SayTextAll('Vote succeeded (%d voted yes). Changing to gamelobby...' % (self.votes['yes']))
            self.changetogamelobby = True
            self.nextchangetogamelobby = gpGlobals.curtime + 3.0
        else:
            UTIL_SayTextAll('Vote failed (%d voted no)' % (self.votes['no']))
            
    def ProcessGLVote(self, player, vote):
        if not self.voting:
            return
        # TODO: Deal with the situation when the player has no steamid. 
        steamIDForPlayer = engine.GetClientSteamID(player)
        if not steamIDForPlayer or steamIDForPlayer in self.voted:
            return
        self.votes[vote] += 1
        self.voted.append(steamIDForPlayer)
        self.totalvotes += 1
        
        UTIL_SayTextAll('%s voted %s' % (player.GetPlayerName(), vote))
        
        ClientUpdateVotes(self.votes['yes'], self.votes['no'])
            
    def UpdateGLVoting(self):
        if self.changetogamelobby:
            if self.nextchangetogamelobby < gpGlobals.curtime:
                self.ChangeToGamelobby()
            return
        
        if not self.voting:
            return
        
        players = 0
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex( i )
            if not player or not player.IsConnected():
                continue
            players += 1
        
        if self.endvoting < gpGlobals.curtime or players == self.totalvotes:
            self.EndGLVote()
            return
            
    # Vars
    voting = False
    nextvoteallow = 0.0
    changetogamelobby = False
    nextchangetogamelobby = 0.0
    
    gametimeout = 0.0
    hasplayers = True
    gametimeout_glplayers = False
    activeplayers = 0
    
    spectateondefeat = True
    
    crates = False
    nextrandomcratetime = 0
       
        
    @classmethod    
    def GetCustomFields(cls):
        fields = {
            'crates' : ['choices', 'yes', 'yes', 'no'],
        }
        return fields
        
    def ParseCustomFields(self, fields):
        for name, values in fields.iteritems():
            if name == 'crates':
                self.crates = values[1] == 'yes'
                
    spawnstartbuildings = True
    startgrubs = 10 # TODO: move to antlion gamerules
    hudrefs = {}
    musicplaylist = None
    
if isserver:
  @concommand('wars_crates_force_spawn', flags=FCVAR_CHEAT)
  def CCForceSpawnCrate(args):
    player = UTIL_GetCommandClient()
    player.ChangeTeam(LAST_SHARED_TEAM + 1)