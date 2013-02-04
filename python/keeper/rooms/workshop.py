from createroom import AbilityCreateRoom, TileRoom

class RoomWorkshop(TileRoom):
    type = 'workshop'
    modelname = 'models/keeper/lair.mdl'

class CreateWorkshop(AbilityCreateRoom):
    name = 'createworkshop'
    roomcls = RoomWorkshop
    costs = [[('gold', 125)]]