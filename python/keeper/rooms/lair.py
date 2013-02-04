from createroom import AbilityCreateRoom, TileRoom

class RoomLair(TileRoom):
    type = 'lair'
    modelname = 'models/keeper/lair.mdl'
    attachedlair = None
    
    if isserver:
        def UpdateOnRemove(self):
            if self.attachedlair:
                self.attachedlair.Remove()
                self.attachedlair = None
            super(RoomLair, self).UpdateOnRemove()
    
class CreateLair(AbilityCreateRoom):
    name = 'createlair'
    roomcls = RoomLair
    costs = [[('gold', 75)]]