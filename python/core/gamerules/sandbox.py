from base import BaseGamerules
from info import GamerulesInfo

class Sandbox(BaseGamerules):
    def SetupGame(self, gamelobby_players, gamelobby_customfields):
        super(Sandbox, self).SetupGame(gamelobby_players, gamelobby_customfields)
 
class SandBoxInfo(GamerulesInfo):
    name = 'sandbox'
    displayname = '#Sandbox_Name'
    description = '#Sandbox_Description'
    cls = Sandbox
    huds = [
    ]
    allowplayerjoiningame = True