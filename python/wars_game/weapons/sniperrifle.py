from srcbase import MAX_TRACE_LENGTH, DMG_BULLET, MASK_SOLID, COLLISION_GROUP_NONE
from entities import entity, FireBulletsInfo_t, WeaponSound, MouseTraceData
from core.weapons import WarsWeaponBase, VECTOR_CONE_1DEGREES
from wars_game.abilities.marksmanshot import AbilityMarkmanShot
if isserver:
    from entities import CBeam
    from utils import UTIL_TraceLine, trace_t
    
@entity('weapon_sniperrifle', networked=True)
class WeaponSniperRifle(WarsWeaponBase):
    def __init__(self):
        super(WeaponSniperRifle, self).__init__()
        
        self.minrange1 = 0.0
        self.maxrange1 = 2048.0
        self.minrange2 = 0.0
        self.maxrange2 = 2048.0
        self.firerate = 2.5
        self.bulletspread = VECTOR_CONE_1DEGREES
        
    def Precache(self):
        super(WeaponSniperRifle, self).Precache()
        
        self.sHaloSprite = self.PrecacheModel("sprites/light_glow03.vmt")
        
    def PrimaryAttack(self):
        owner = self.GetOwner()

        owner.DoMuzzleFlash()
        
        self.SendWeaponAnim(self.GetPrimaryAttackActivity())

        #self.clip1 = self.clip1 - 1

        vecShootOrigin, vecShootDir = self.GetShootOriginAndDirection()
        
        # NOTE: Do not use nextprimaryattack for attack time sound, otherwise it fades out too much. (since this is not per frame)
        self.WeaponSound(WeaponSound.SINGLE, gpGlobals.curtime)
        self.nextprimaryattack = gpGlobals.curtime + self.firerate

        info = FireBulletsInfo_t()
        info.shots = 1
        info.vecsrc = vecShootOrigin
        info.vecdirshooting = vecShootDir
        info.vecspread = self.bulletspread
        info.distance = self.maxbulletrange
        info.ammotype = self.primaryammotype
        info.tracerfreq = 0
        info.damage = self.AttackPrimary.damage
        
        if isserver:
            self.CreateTrail(vecShootOrigin, vecShootOrigin + vecShootDir * self.maxrange1)
            
        owner.FireBullets(info)

    def MakeTracer(self, vectracersrc, tr, tracertype):
        pass # Tracer is already created in PrimaryAttack
        
    def CreateTrail(self, start, end):
        tr = trace_t()
        UTIL_TraceLine(start, end, MASK_SOLID, self.GetOwner(), COLLISION_GROUP_NONE, tr)
        
        beam = CBeam.BeamCreate("effects/bluelaser1.vmt", 1.0)
        beam.SetColor(0, 100, 255)

        beam.PointsInit(start, tr.endpos)
        beam.SetBrightness( 255 )
        beam.SetNoise( 0 )
        beam.SetWidth( 1.0 )
        beam.SetEndWidth( 0 )
        beam.SetScrollRate( 0 )
        beam.SetFadeLength( 0 )
        beam.SetHaloTexture( self.sHaloSprite )
        beam.SetHaloScale( 4.0 )

        beam.LiveForTime(5.0)
    
    clientclassname = 'weapon_sniperrifle'
    muzzleoptions = 'SHOTGUN MUZZLE'

    class AttackPrimary(WarsWeaponBase.AttackBase):
        damage = 100
        damagetype = DMG_BULLET
        minrange = 0.0
        maxrange = 2000.0
        cone = 0.7
        attackspeed = AbilityMarkmanShot.rechargetime
        
        @staticmethod
        def CanAttack(unit, enemy):
            return unit.CanRangeAttack(enemy.WorldSpaceCenter()) and AbilityMarkmanShot.CanDoAbility(None, unit=unit)
            
        @staticmethod
        def Attack(unit, enemy):
            leftpressed = MouseTraceData()
            leftpressed.ent = unit.enemy
            unit.markmanshot = True
            unit.DoAbility(AbilityMarkmanShot.name, [('leftpressed', leftpressed)])
            unit.markmanshot = False
            return True
            