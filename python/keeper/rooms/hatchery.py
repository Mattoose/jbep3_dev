from createroom import AbilityCreateRoom, TileRoom, RoomController
from entities import entity
import random

if isserver:
    from core.units import CreateUnit

@entity('dk_hatchery_controller', networked=True)
class HatcheryController(RoomController):
    if isserver:
        def Spawn(self):
            super(HatcheryController, self).Spawn()
            
            self.grubs = []
            self.SetThink(self.HatcheryThink, gpGlobals.curtime + random.uniform(self.minrate, self.maxrate))
            
        def HatcheryThink(self):
            self.grubs = filter(None, self.grubs)
            
            # Allow one grub per tile for now
            if self.tiles :
                if len(self.grubs) < len(self.tiles):
                    tile = self.RandomTile()
                    grub = CreateUnit('unit_dk_grub', tile.GetAbsOrigin(), owner_number=self.GetOwnerNumber())
                    grub.hatchery = self.GetHandle()
                    self.grubs.append(grub)
            else:
                PrintWarning("Room controller without tiles!\n")
                
            self.SetNextThink(gpGlobals.curtime + random.uniform(self.minrate, self.maxrate))
            
        def GetRandomGrub(self):
            self.grubs = filter(None, self.grubs)
            return random.sample(self.grubs, 1)[0] if self.grubs else None 
            
    minrate = 5.0
    maxrate = 15.0

class RoomHatchery(TileRoom):
    type = 'hatchery'
    modelname = 'models/keeper/hatchery.mdl'
    roomcontrollerclassname = 'dk_hatchery_controller'
    
class CreateHatchery(AbilityCreateRoom):
    name = 'createhatchery'
    roomcls = RoomHatchery
    costs = [[('gold', 100)]]