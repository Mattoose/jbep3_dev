from gamerules import CJBGameRules, LAST_SHARED_TEAM, TeamRegister
from gameinterface import ConVarRef

mp_timelimit = ConVarRef('mp_timelimit')
    
# Base Gamerules
class BaseGamerules(CJBGameRules):
    def __init__(self):
        super(BaseGamerules, self).__init__()
                
    def Precache(self):
        super(BaseGamerules, self).Precache()

    def InitGamerules(self):
        super(BaseGamerules, self).InitGamerules()

    def ShutdownGamerules(self):
        super(BaseGamerules, self).ShutdownGamerules()
        
    def InitTeams(self):
        super(BaseGamerules, self).InitTeams() ## Init our standard teams, unassigned, spectator
        TeamRegister( LAST_SHARED_TEAM + 1, "TEST TEAM" )
        
    def SelectDefaultTeam(self):
        return LAST_SHARED_TEAM + 1

    def Think(self):
        """ Updates the gamerules . """
        if isserver:
            print "SERVER"
        else:
            print "CLIENT"
            
        self.UpdateVoiceManager()
    
        timelimit = mp_timelimit.GetFloat() * 60
                
        if timelimit != 0 and gpGlobals.curtime >= timelimit:
            self.GoToIntermission()
            return