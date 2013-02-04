from entities import entity, Activity
from core.weapons import WarsWeaponMachineGun, VECTOR_CONE_5DEGREES

@entity('weapon_smg1', networked=True)
class WeaponSmg1(WarsWeaponMachineGun):
    def __init__(self):
        super(WeaponSmg1, self).__init__()
        
        self.bulletspread = VECTOR_CONE_5DEGREES

    clientclassname = 'weapon_smg1'
    muzzleoptions = 'SMG1 MUZZLE'
    
    class AttackPrimary(WarsWeaponMachineGun.AttackPrimary):
        maxrange = 820.0
        attackspeed = 0.2 # Fire rate

