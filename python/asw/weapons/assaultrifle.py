from entities import entity, Activity
from core.weapons import WarsWeaponMachineGun, VECTOR_CONE_5DEGREES

@entity('asw_weapon_rifle', networked=True)
class WeaponAssaultRifle(WarsWeaponMachineGun):
    def __init__(self):
        super(WeaponAssaultRifle, self).__init__()
        
        self.minrange1 = 0.0
        self.maxrange1 = 1024.0
        self.firerate = 0.075
        self.bulletspread = VECTOR_CONE_5DEGREES
        
    clientclassname = 'asw_weapon_rifle'
    

