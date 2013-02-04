from createroom import AbilityCreateRoom, TileRoom

class RoomLibrary(TileRoom):
    type = 'library'
    modelname = 'models/keeper/lair.mdl'

class CreateLibrary(AbilityCreateRoom):
    name = 'createlibrary'
    roomcls = RoomLibrary
    costs = [[('gold', 200)]]