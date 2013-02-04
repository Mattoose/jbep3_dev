from srcbase import DMG_CLUB
from core.weapons import WarsWeaponMelee
from entities import entity
from utils import UTIL_ImpactTrace
from te import CEffectData, DispatchEffect

if isserver:
    from utils import UTIL_Remove
    
@entity('weapon_stunstick', networked=True)
class WeaponStunStick(WarsWeaponMelee):
    clientclassname = 'weapon_stunstick' 
    
    STUNSTICK_BEAM_MATERIAL = "sprites/lgtning.vmt"
    STUNSTICK_GLOW_MATERIAL = "sprites/light_glow02_add"
    STUNSTICK_GLOW_MATERIAL2 = "effects/blueflare1"
    STUNSTICK_GLOW_MATERIAL_NOZ = "sprites/light_glow02_add_noz"
    
    class AttackPrimary(WarsWeaponMelee.AttackPrimary):
        damage = 40.0
        maxrange = 64.0
        attackspeed = 0.5
    
    def __init__(self):
        super(WeaponStunStick, self).__init__()
        
        self.minrange2 = 0
        self.maxrange2 = 75.0
        
    def Precache(self):
        super(WeaponStunStick, self).Precache()
        
        self.PrecacheScriptSound("Weapon_StunStick.Activate")
        self.PrecacheScriptSound("Weapon_StunStick.Deactivate")

        self.PrecacheModel(self.STUNSTICK_BEAM_MATERIAL)
        
    def ImpactEffect(self, traceHit):
        data = CEffectData()

        data.normal = traceHit.plane.normal
        data.origin = traceHit.endpos + ( data.normal * 4.0 )

        # TODO
        #DispatchEffect("StunstickImpact", data)

        #FIXME: need new decals
        UTIL_ImpactTrace(traceHit, DMG_CLUB)

    def SetStunState(self, state):
        """ Sets the state of the stun stick """
        self.active = state

        if self.active:
            #FIXME: START - Move to client-side

            vecAttachment = Vector()
            vecAttachmentAngles = QAngle()

            self.GetAttachment(1, vecAttachment, vecAttachmentAngles)
            #g_pEffects.Sparks( vecAttachment )

            #FIXME: END - Move to client-side

            self.EmitSound("Weapon_StunStick.Activate")
        else:
            self.EmitSound("Weapon_StunStick.Deactivate")

    def Deploy(self):
        """ Returns true on success, false on failure. """
        self.SetStunState(True)
        #if isclient:
            #SetupAttachmentPoints()

        return super(WeaponStunStick, self).Deploy()

    def Holster(self, pSwitchingTo):
        if super(WeaponStunStick, self).Holster(pSwitchingTo) == False:
            return false

        self.SetStunState(False)
        self.SetWeaponVisible(False)

        return True

    def Drop(self, vecVelocity):
        self.SetStunState(False)

        if isserver:
            UTIL_Remove(self)
