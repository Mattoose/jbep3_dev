from srcbase import (SOLID_BBOX, MOVETYPE_FLYGRAVITY, MOVECOLLIDE_FLY_BOUNCE, MOVETYPE_FLY,
                     DAMAGE_YES, DAMAGE_EVENTS_ONLY, DAMAGE_NO, DONT_BLEED, FL_OBJECT, FSOLID_NOT_SOLID, MASK_SHOT, SURF_SKY,
                     DMG_MISSILEDEFENSE, DMG_AIRBOAT, MAX_TRACE_LENGTH, EF_NOSHADOW, FSOLID_TRIGGER,
                     FSOLID_VOLUME_CONTENTS, COLLISION_GROUP_WEAPON, COLLISION_GROUP_NONE, SOLID_NONE)
from vmath import Vector, QAngle, VectorAngles, AngleVectors, VectorNormalize, VectorSubtract, vec3_origin
from math import sqrt
import random
from entities import entity, WeaponSound
from core.weapons import WarsWeaponBase
from core.ents.homingprojectile import HomingProjectile
if isserver:
    from entities import CBaseCombatCharacter, CBaseEntity, RocketTrail
    from utils import (UTIL_SetSize, UTIL_Remove, ExplosionCreate, SF_ENVEXPLOSION_NOSPARKS, SF_ENVEXPLOSION_NODLIGHTS, SF_ENVEXPLOSION_NOSMOKE,
                       UTIL_TraceLine, trace_t, UTIL_PrecacheOther)
    from te import DispatchEffect, CEffectData
    from gameinterface import ConVar
    
RPG_SPEED = 1500
    
if isserver:
    rpg_missle_use_custom_detonators = ConVar("rpg_missle_use_custom_detonators", "1")

    @entity('rpg_missile')
    class Missile(HomingProjectile):
        """ Python implementation of the missile entity """
        def Precache(self):
            super(Missile, self).Precache()
        
            self.PrecacheModel('models/weapons/w_missile.mdl')
            self.PrecacheModel('models/weapons/w_missile_launch.mdl')
            self.PrecacheModel('models/weapons/w_missile_closed.mdl')
            
        def Spawn(self):
            super(Missile, self).Spawn()
            
            self.SetCollisionGroup(self.CalculateIgnoreOwnerCollisionGroup())

            self.SetSolid(SOLID_BBOX)
            self.SetModel('models/weapons/w_missile_launch.mdl')
            UTIL_SetSize(self, -Vector(4,4,4), Vector(4,4,4))

            self.SetTouch(self.MissileTouch)
            
            self.SetThink(self.IgniteThink, gpGlobals.curtime + 0.3, 'IgniteThink')
            
            #self.SetMoveType(MOVETYPE_FLYGRAVITY, MOVECOLLIDE_FLY_BOUNCE)
            self.damage = 150.0

            self.takedamage = DAMAGE_YES
            self.health = self.maxhealth = 100
            self.bloodColor = DONT_BLEED
            self.graceperiodendsat = 0

            self.AddFlag(FL_OBJECT)
            
        def UpdateOnRemove(self):
            self.StopSound("Missile.Ignite") # Just to be sure, in case we are removed some other way.
            
            super(Missile, self).UpdateOnRemove()
        
        '''
        def Event_Killed(self, info):
            self.takedamage = DAMAGE_NO

            self.ShotDown()

        def OnTakeDamage_Alive(self, info):
            if info.GetDamageType() & (DMG_MISSILEDEFENSE|DMG_AIRBOAT) == False:
                return 0

            if self.health <= self.AugerHealth():
                # self missile is already damaged (i.e., already running AugerThink)
                isdamaged = True
            else:
                # self missile isn't damaged enough to wobble in flight yet
                isdamaged = False
            
            nRetVal = super(Missile, self).OnTakeDamage_Alive( info )

            if not isdamaged:
                if self.health <= self.AugerHealth():
                    self.ShotDown()

            return nRetVal
        '''
        
        def DumbFire(self):
            """ Stops any kind of tracking and shoots dumb """
            self.SetThink(None)
            self.SetMoveType(MOVETYPE_FLY)

            self.SetModel('models/weapons/w_missile.mdl')
            UTIL_SetSize(self, vec3_origin, vec3_origin)

            self.EmitSound("Missile.Ignite")

            # Smoke trail.
            self.CreateSmokeTrail()

        def SetGracePeriod(self, flGracePeriod):
            self.graceperiodendsat = gpGlobals.curtime + flGracePeriod

            # Go non-solid until the grace period ends
            self.AddSolidFlags(FSOLID_NOT_SOLID)
        
        def AccelerateThink(self):
            vecForward = Vector()

            # !!!UNDONE - make self work exactly the same as HL1 RPG, lest we have looping sound bugs again!
            self.EmitSound('Missile.Accelerate')

            # SetEffects( EF_LIGHT )

            AngleVectors(self.GetLocalAngles(), vecForward)
            self.SetAbsVelocity(vecForward * RPG_SPEED)

            self.SetThink(self.SeekThink)
            self.SetNextThink(gpGlobals.curtime + 0.1)

        AUGER_YDEVIANCE = 20.0
        AUGER_XDEVIANCEUP = 8.0
        AUGER_XDEVIANCEDOWN = 1.0

        def AugerThink(self):
            # If we've augered long enough, then just explode
            if self.augertime < gpGlobals.curtime:
                self.Explode()
                return
            
            if self.markdeadtime < gpGlobals.curtime:
                self.lifeState = LIFE_DYING

            angles = self.GetLocalAngles()

            angles.y += random.uniform(-self.AUGER_YDEVIANCE,self.AUGER_YDEVIANCE)
            angles.x += random.uniform(-self.AUGER_XDEVIANCEDOWN, self.AUGER_XDEVIANCEUP)

            self.SetLocalAngles(angles)

            vecForward = Vector()

            AngleVectors(self.GetLocalAngles(), vecForward)
            
            self.SetAbsVelocity(vecForward * 1000.0)

            self.SetNextThink(gpGlobals.curtime + 0.05)

        def ShotDown(self):
            """ Causes the missile to spiral to the ground and explode, due to damage """
            data = CEffectData()
            data.origin = self.GetAbsOrigin()

            DispatchEffect("RPGShotDown", data)

            if self.rockettrail != None:
                self.rockettrail.damaged = True

            self.SetThink(self.AugerThink)
            self.SetNextThink(gpGlobals.curtime)
            self.augertime = gpGlobals.curtime + 1.5
            self.markdeadtime = gpGlobals.curtime + 0.75

            # Let the RPG start reloading immediately
            if self.owner != None:
                self.owner.NotifyRocketDied()
                self.owner = None
                
        EXPLOSION_RADIUS = 192
        def DoExplosion(self):
            """ The actual explosion  """
            # Explode
            ExplosionCreate(self.GetAbsOrigin(), self.GetAbsAngles(), self.GetOwnerEntity(), int(self.damage), self.EXPLOSION_RADIUS, 
                SF_ENVEXPLOSION_NOSPARKS|SF_ENVEXPLOSION_NODLIGHTS|SF_ENVEXPLOSION_NOSMOKE, 0.0, self)

        def Explode(self):
            # Don't explode against the skybox. Just pretend that 
            # the missile flies off into the distance.
            forward = Vector()
            self.GetVectors(forward, None, None)

            tr = trace_t()
            UTIL_TraceLine(self.GetAbsOrigin(), self.GetAbsOrigin() + forward * 16, MASK_SHOT, self, COLLISION_GROUP_NONE, tr)

            self.takedamage = DAMAGE_NO
            self.SetSolid(SOLID_NONE)
            if tr.fraction == 1.0 or not (tr.surface.flags & SURF_SKY):
                self.DoExplosion()

            if self.rockettrail:
                self.rockettrail.SetLifetime(0.1)
                self.rockettrail = None

            if self.owner != None:
                self.owner.NotifyRocketDied()
                self.owner = None

            self.StopSound("Missile.Ignite")
            UTIL_Remove(self)

        def MissileTouch(self, pOther):
            assert( pOther )
            
            # Don't touch triggers (but DO hit weapons)
            if pOther.IsSolidFlagSet(FSOLID_TRIGGER|FSOLID_VOLUME_CONTENTS) and pOther.GetCollisionGroup() != COLLISION_GROUP_WEAPON:
                # Some NPCs are triggers that can take damage (like antlion grubs). We should hit them.
                if (pOther.takedamage == DAMAGE_NO) or (pOther.takedamage == DAMAGE_EVENTS_ONLY):
                    return

            self.Explode()

        def CreateSmokeTrail(self):
            if self.rockettrail:
                return

            # Smoke trail.
            self.rockettrail = RocketTrail.CreateRocketTrail()
            if self.rockettrail:
                self.rockettrail.opacity = 0.2
                self.rockettrail.spawnrate = 100
                self.rockettrail.particlelifetime = 0.5
                self.rockettrail.startcolor = Vector( 0.65, 0.65 , 0.65 )
                self.rockettrail.endcolor = Vector( 0.0, 0.0, 0.0 )
                self.rockettrail.startsize = 8
                self.rockettrail.endsize = 32
                self.rockettrail.spawnradius = 4
                self.rockettrail.minspeed = 2
                self.rockettrail.maxspeed = 16
                
                self.rockettrail.SetLifetime( 999 )
                self.rockettrail.FollowEntity( self, "0" )
            
        def IgniteThink(self):
            self.SetMoveType(MOVETYPE_FLY)
            self.SetModel('models/weapons/w_missile.mdl')
            UTIL_SetSize(self, vec3_origin, vec3_origin)
            self.RemoveSolidFlags(FSOLID_NOT_SOLID)

            #TODO: Play opening sound

            vecForward = Vector()

            self.EmitSound( "Missile.Ignite" )

            AngleVectors(self.GetLocalAngles(), vecForward)
            #self.SetAbsVelocity(vecForward * RPG_SPEED)
            self.velocity = RPG_SPEED

            # TODO: Make this optional. Shouldn't be needed in hl2wars
            #self.SetThink(self.SeekThink)
            #self.SetNextThink(gpGlobals.curtime)

            '''
            if self.owner and self.owner.GetOwner():
                owner = self.owner.GetOwner()
                if owner.IsPlayer():
                    white = color32(255,225,205,64)
                    UTIL_ScreenFade(owner, white, 0.1f, 0.0f, FFADE_IN)

                    owner.RumbleEffect(RUMBLE_RPG_MISSILE, 0, RUMBLE_FLAG_RESTART)
            '''
            
            self.CreateSmokeTrail()

        def GetShootPosition(self, pLaserDot):
            """ Gets the shooting position """
            if pLaserDot.GetOwnerEntity() != None:
                #FIXME: Do we care self isn't exactly the muzzle position?
                return pLaserDot.GetOwnerEntity().WorldSpaceCenter()
            return pLaserDot.GetChasePosition()

        RPG_HOMING_SPEED = 0.125
        def ComputeActualDotPosition(self, pLaserDot):
            pHomingSpeed = self.RPG_HOMING_SPEED
            if pLaserDot.GetTargetEntity():
                pActualDotPosition = pLaserDot.GetChasePosition()
                return pActualDotPosition, pHomingSpeed

            vLaserStart = self.GetShootPosition(pLaserDot)

            #Get the laser's vector
            vLaserDir = Vector()
            VectorSubtract(pLaserDot.GetChasePosition(), vLaserStart, vLaserDir)
            
            #Find the length of the current laser
            flLaserLength = VectorNormalize(vLaserDir)
            
            #Find the length from the missile to the laser's owner
            flMissileLength = GetAbsOrigin().DistTo( vLaserStart )

            #Find the length from the missile to the laser's position
            vecTargetToMissile = Vector()
            VectorSubtract(self.GetAbsOrigin(), pLaserDot.GetChasePosition(), vecTargetToMissile) 
            flTargetLength = VectorNormalize(vecTargetToMissile)

            # See if we should chase the line segment nearest us
            if (flMissileLength < flLaserLength) or (flTargetLength <= 512.0):
                pActualDotPosition = UTIL_PointOnLineNearestPoint(vLaserStart, pLaserDot.GetChasePosition(), GetAbsOrigin())
                pActualDotPosition += vLaserDir * 256.0
            else:
                # Otherwise chase the dot
                pActualDotPosition = pLaserDot.GetChasePosition()

        #	NDebugOverlay::Line( pLaserDot.GetChasePosition(), vLaserStart, 0, 255, 0, True, 0.05f )
        #	NDebugOverlay::Line( GetAbsOrigin(), *pActualDotPosition, 255, 0, 0, True, 0.05f )
        #	NDebugOverlay::Cross3D( *pActualDotPosition, -Vector(4,4,4), Vector(4,4,4), 255, 0, 0, True, 0.05f )
            return pActualDotPosition, pHomingSpeed
        
        def SeekThink(self):
            pBestDot = None
            flBestDist = MAX_TRACE_LENGTH

            # If we have a grace period, go solid when it ends
            if self.graceperiodendsat:
                if self.graceperiodendsat < gpGlobals.curtime:
                    self.RemoveSolidFlags(FSOLID_NOT_SOLID)
                    self.graceperiodendsat = 0

            #Search for all dots relevant to us
            for pEnt in laserdotlist:
                if not pEnt.IsOn():
                    continue

                if pEnt.GetOwnerEntity() != GetOwnerEntity():
                    continue

                dotDist = (self.GetAbsOrigin() - pEnt.GetAbsOrigin()).Length()

                #Find closest
                if dotDist < flBestDist:
                    pBestDot = pEnt
                    flBestDist = dotDist

            #if flBestDist <= (self.GetAbsVelocity().Length() * 2.5) and self.FVisible(pBestDot.GetAbsOrigin()):
            #    # Scare targets
            #    CSoundEnt.InsertSound( SOUND_DANGER, pBestDot.GetAbsOrigin(), CMissile.EXPLOSION_RADIUS, 0.2, pBestDot, SOUNDENT_CHANNEL_REPEATED_DANGER, None )

            if rpg_missle_use_custom_detonators.GetBool():
                for i in range(len(detonator)-1, -1, -1):
                    detonator = self.gm_CustomDetonators[i]
                    if not detonator.entity:
                        del self.gm_CustomDetonators[i]
                    else:
                        vPos = detonator.entity.CollisionProp().WorldSpaceCenter()
                        if detonator.halfHeight > 0:
                            if abs(vPos.z - GetAbsOrigin().z) < detonator.halfHeight:
                                if (GetAbsOrigin().AsVector2D() - vPos.AsVector2D()).LengthSqr() < detonator.radiusSq:
                                    self.Explode()
                                    return
                        else:
                            if (self.GetAbsOrigin() - vPos).LengthSqr() < detonator.radiusSq:
                                self.Explode()
                                return

            #If we have a dot target
            if pBestDot == None:
                #Think as soon as possible
                SetNextThink(gpGlobals.curtime)
                return

            pLaserDot = pBestDot
            targetPos = Vector()

            vecLaserDotPosition, flHomingSpeed = self.ComputeActualDotPosition(pLaserDot)

            if self.IsSimulatingOnAlternateTicks():
                flHomingSpeed *= 2

            vTargetDir = Vector()
            VectorSubtract(targetPos, GetAbsOrigin(), vTargetDir)
            flDist = VectorNormalize(vTargetDir)

            if pLaserDot.GetTargetEntity() != None and flDist <= 240.0:
                # Prevent the missile circling the Strider like a Halo in ep1_c17_06. If the missile gets within 20
                # feet of a Strider, tighten up the turn speed of the missile so it can break the halo and strike. (sjb 4/27/2006)
                if pLaserDot.GetTargetEntity().ClassMatches( "npc_strider" ):
                    flHomingSpeed *= 1.75

            vDir = self.GetAbsVelocity()
            flSpeed = VectorNormalize(vDir)
            vNewVelocity = vDir
            if gpGlobals.frametime > 0.0:
                if flSpeed != 0:
                    vNewVelocity = (flHomingSpeed * vTargetDir) + ( (1 - flHomingSpeed) * vDir )

                    # self computation may happen to cancel itself out exactly. If so, slam to targetdir.
                    if VectorNormalize( vNewVelocity ) < 1e-3:
                        vNewVelocity = vTargetDir if (flDist != 0) else vDir
                else:
                    vNewVelocity = vTargetDir

            finalAngles = QAngle()
            self.VectorAngles(vNewVelocity, finalAngles)
            self.SetAbsAngles(finalAngles)

            vNewVelocity *= flSpeed
            self.SetAbsVelocity(vNewVelocity)

            if self.GetAbsVelocity() == vec3_origin:
                # Strange circumstances have brought self missile to halt. Just blow it up.
                self.Explode()
                return

            # Think as soon as possible
            self.SetNextThink(gpGlobals.curtime)

            # Don't need this
            #if self.createdangersounds == True:
            #    tr = trace_t()
            #    UTIL_TraceLine(self.GetAbsOrigin(), self.GetAbsOrigin() + self.GetAbsVelocity() * 0.5, MASK_SOLID, self, COLLISION_GROUP_NONE, tr)
            #
            #    CSoundEnt.InsertSound(SOUND_DANGER, tr.endpos, 100, 0.2, self, SOUNDENT_CHANNEL_REPEATED_DANGER)
        
        @classmethod
        def Create(cls, vecOrigin, vecAngles, owner=None, damage=150):
            missile = CBaseEntity.Create("rpg_missile", vecOrigin, vecAngles, owner)
            missile.SetOwnerEntity(owner)
            if owner: missile.SetOwnerNumber(owner.GetOwnerNumber())
            
            missile.dietime = gpGlobals.curtime + 6.0
            missile.velocity = 320
            
            missile.Spawn()
            missile.AddEffects(EF_NOSHADOW)
            missile.damage = damage
            
            vecForward = Vector()
            AngleVectors(vecAngles, vecForward)

            missile.SetTargetAndFire(owner.enemy)
            #missile.SetAbsVelocity(vecForward * 300 + Vector(0,0, 128))

            return missile
        
        gm_CustomDetonators = []
        def AddCustomDetonator(self, pEntity, radius, height):
            self.gm_CustomDetonators.append(object())
            self.gm_CustomDetonators[-1].entity = pEntity
            self.gm_CustomDetonators[-1].radiusSq = sqrt(radius)
            self.gm_CustomDetonators[-1].halfHeight = height * 0.5

        def RemoveCustomDetonator(self, pEntity):
            for customdetonator in self.gm_CustomDetonators:
                if customdetonator.entity == pEntity:
                    self.gm_CustomDetonators.remove(customdetonator)
                    break
                    
        rockettrail = None
        damage = 200.0
        
RPG_BEAM_SPRITE = "effects/laser1_noz.vmt"
RPG_LASER_SPRITE = "sprites/redglow1.vmt"

@entity('weapon_rpg', networked=True)
class WeaponRPG(WarsWeaponBase):
    clientclassname = 'weapon_rpg'
    
    if isserver:
        def Precache(self):
            super(WeaponRPG, self).Precache()

            self.PrecacheScriptSound('Missile.Ignite')
            self.PrecacheScriptSound('Missile.Accelerate')

            # Laser dot...
            self.PrecacheModel('sprites/redglow1.vmt')
            self.PrecacheModel(RPG_LASER_SPRITE)
            self.PrecacheModel(RPG_BEAM_SPRITE)

            UTIL_PrecacheOther('rpg_missile')

    def PrimaryAttack(self):
        owner = self.GetOwner()

        owner.DoMuzzleFlash()
        
        self.SendWeaponAnim(self.GetPrimaryAttackActivity())

        #self.clip1 = self.clip1 - 1

        vecShootOrigin, vecShootDir = self.GetShootOriginAndDirection()
        
        # NOTE: Do not use nextprimaryattack for attack time sound, otherwise it fades out too much.
        self.WeaponSound(WeaponSound.SINGLE, gpGlobals.curtime)
        self.nextprimaryattack = gpGlobals.curtime + self.firerate
        
        vecAngles = QAngle()
        VectorAngles(vecShootDir, vecAngles)
    
        if isserver:
            missile = Missile.Create(vecShootOrigin, vecAngles, self.GetOwner(), self.AttackPrimary.damage)
            missile.owner = self.GetHandle()
            
    def NotifyRocketDied(self): pass
    
    class AttackPrimary(WarsWeaponBase.AttackRange):
        maxrange = 820.0
        attackspeed = 4.0
        damage = 120
        