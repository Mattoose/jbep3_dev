""" This module will store info about the players in the map. """
from srcbase import *
from vmath import *
import srcmgr

from core.dispatch import receiver
from core.signals import prelevelinit
from core.usermessages import usermessage

from collections import defaultdict

from fields import IntegerField, FlagsField
from entities import entity

if isserver:
    from gameinterface import concommand, ConCommand, FCVAR_CHEAT, CSingleUserRecipientFilter, CReliableBroadcastRecipientFilter
    from entities import CPointEntity
    from utils import UTIL_PlayerByIndex, UTIL_GetCommandClient, UTIL_EntityByIndex
    from core.signals import clientactive
else:
    from entities import C_JBPlayer
    
#
# Ownernumber 0 and 1 are reserved for the neutral and enemy side
#
OWNER_NEUTRAL = 0
OWNER_ENEMY = 1
OWNER_LAST = 2

#
# Player info per owner number
#
class PlayerInfo(object):
    def __init__(self, 
                 color = Color(255, 255, 255, 255), 
                 faction = "rebels", 
                 reserved = False):
        super(PlayerInfo, self).__init__()
                
    #def Setup(self, ownernumber):
              
#@receiver(prelevelinit)
#def LevelInit(sender, **kwargs):

    
#
# Some start ents that use the player owner number
#
if isserver:
    @entity('info_player_wars',
            base=['PlayerClass', 'Angles'],
            studio='models/editor/playerstart.mdl')
    class InfoPlayerWars(CPointEntity):
        pass
    @entity('info_start_wars',
            base=['Targetname', 'Parentname', 'Angles'],
            cylinder=['255 255 255', 'targetname', 'target', 'radius', 'targetname', 'targetname', 'radius'],
            color='255 192 0',
            size='16 16 16')
    class InfoStartWars(CPointEntity):
        spawnflags = FlagsField(keyname='spawnflags', flags=
            [('SF_NO_POPULATE', ( 1 << 0 ), False)], 
            cppimplemented=True)
        
#
# Simulated player
#
#class SimulatedPlayer(object):
#    """ Simulated player. Wraps the real player and replaces the mouse data """
#    def __init__(self, ownernumber,
#                mousedata=MouseTraceData(),
#                leftmousepressed=MouseTraceData(),
#                leftmousedoublepressed=MouseTraceData(),
#                leftmousereleased=MouseTraceData(),
#                rightmousepressed_data=MouseTraceData(),
#                rightmousedoublepressed=MouseTraceData(),
#                rightmousereleased=MouseTraceData(),
#                selection=[]):
#        super(SimulatedPlayer, self).__init__()
#        self.ownernumber = ownernumber
#        self.selection = selection
#        if isserver:
#            players = ListPlayersForOwnerNumber(ownernumber)
#            self.player = players[0] if players else None
#        else:
#            self.player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
#            
#        self.mousedata = mousedata
#        self.leftmousepressed = leftmousepressed
#        self.leftmousedoublepressed = leftmousedoublepressed
#        self.leftmousereleased = leftmousereleased
#        self.rightmousepressed_data = rightmousepressed_data
#        self.rightmousedoublepressed = rightmousedoublepressed
#        self.rightmousereleased = rightmousereleased
#            
#    def GetMouseData(self): return self.mousedata
#    def GetMouseDataLeftPressed(self): return self.leftmousepressed
#    def GetMouseDataLeftDoublePressed(self): return self.leftmousedoublepressed
#    def GetMouseDataLeftReleased(self): return self.leftmousereleased
#    def GetMouseDataRightPressed(self): return self.rightmousepressed_data
#    def GetMouseDataRightDoublePressed(self): return self.rightmousedoublepressed
#    def GetMouseDataRightReleased(self): return self.rightmousereleased
#    
#    def IsLeftPressed(self): return False
#    def IsRightPressed(self): return False
#    def ClearMouse(self): pass
#    
#    def GetSelection(self): return self.selection
#    
#    def GetOwnerNumber(self): return self.ownernumber
#    
#    def AddActiveAbility(self, ability): pass
#    def RemoveActiveAbility(self, ability): pass
#    def IsActiveAbility(self, ability): pass
#    def ClearActiveAbilities(self): pass
#    def SetSingleActiveAbility(self, ability): pass
#    def GetSingleActiveAbility(self): pass
#    
#    def __getattribute__(self, name):
#        try:
#            return object.__getattribute__(self, name)
#        except AttributeError:
#            return getattr(self.player, name)
#
#    buttons = 0
        