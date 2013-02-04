from srcbase import TEAM_INVALID, TEAM_UNASSIGNED, TEAM_SPECTATOR
from glpkg.gamelobby_shared import *
from playermgr import OWNER_LAST
from core.gamerules import GamerulesInfo, WarsBaseGameRules
from utils import UTIL_GetPlayers
from core.buildings.base import buildinglist
from core.resources import SetResource, RESOURCE_REQUISITION

class Annihilation(WarsBaseGameRules):
    def __init__(self):
        super(Annihilation, self).__init__()

    def CheckGameOver(self):
        if self.gameover:   # someone else quit the game already
            # check to see if we should change levels now
            if self.intermissionendtime < gpGlobals.curtime:
                self.ChangeToGamelobby()  # intermission is over
            return True
        return False
        
    def Think(self):
        super(Annihilation, self).Think()
        if self.gameover:
            return
        
        players = self.GetGamelobbyPlayers()
        if not players:
            players = UTIL_GetPlayers()
          
        # Check winning conditions (only one player or team left alive)
        # Only check the gamelobby players
        counts = set()
        for i, glp in enumerate(self.gamelobby_players):
            if glp[0].type != GLTYPE_CPU and glp[0].type != GLTYPE_HUMAN:
                continue
            if self.IsPlayerDefeated(glp):
                continue
            ownernumber = OWNER_LAST + glp[0].position    
            countunits = len(buildinglist[ownernumber])
            if not countunits:
                self.PlayerDefeated(glp)
                continue
            if glp[0].team is not TEAM_INVALID and glp[0].team is not TEAM_UNASSIGNED and glp[0].team is not TEAM_SPECTATOR:
                counts.add(glp[0].team)
            else:
                counts.add(glp) 
                
        if len(counts) == 1:
            # We got a winner!
            winners, losers = self.CalculateWinnersAndLosers(list(counts)[0])
            self.EndGame(winners, losers)
            
    def SetupGame(self, gamelobby_players, gamelobby_customfields):
        super(Annihilation, self).SetupGame(gamelobby_players, gamelobby_customfields)
        
        for i, glp in enumerate(gamelobby_players):
            if glp[0].position == INVALID_POSITION:
                continue
            ownernumber = OWNER_LAST+glp[0].position
            SetResource(ownernumber, RESOURCE_REQUISITION, 15)
               
    gametimeout_glplayers = True
    
    
class AntlionAnnihilation(Annihilation):
    @classmethod    
    def GetCustomFields(cls):
        """ Return a list of fields that should appear in the settings in the gamelobby """
        return {
                    'grubs' : ['choices', '10', '0', '5', '10', '20'],
               }
        
    def ParseCustomFields(self, fields):
        for name, values in fields.iteritems():
            if name == 'grubs':
                self.startgrubs = values[1]

class AnnihilationInfo(GamerulesInfo):
    name = 'annihilation'
    displayname = '#Annihilation_Name'
    description = '#Annihilation_Description'
    cls = Annihilation
    supportcpu = True
    mappattern = '^hlw_.*$'
    factionpattern = '^(rebels|combine)$'
    minplayers = 2
    allowallsameteam = False
    huds = [
        'core.hud.HudPlayerNames',
    ]

'''
class AntlionWarsAnnihilationInfo(GamerulesInfo):
    name = 'antlion_annihilation'
    displayname = '#AntlionAnnihilation_Name'
    description = '#AntlionAnnihilation_Description'
    cls = AntlionAnnihilation
    mappattern = '^wmp_.*$'
    factionpattern = '^antlions$'
    huds = [
        'core.hud.HudPlayerNames',
    ]
'''