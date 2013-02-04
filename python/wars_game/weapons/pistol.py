from entities import entity
from core.weapons import WarsWeaponMachineGun, VECTOR_CONE_3DEGREES

@entity('weapon_pistol', networked=True)
class WeaponPistol(WarsWeaponMachineGun):
    def __init__(self):
        super(WeaponPistol, self).__init__()
        
        self.bulletspread = VECTOR_CONE_3DEGREES

    clientclassname = 'weapon_pistol'
    muzzleoptions = 'PISTOL MUZZLE'

    class AttackPrimary(WarsWeaponMachineGun.AttackPrimary):
        minrange = 24.0
        maxrange = 820.0
        attackspeed = 0.5