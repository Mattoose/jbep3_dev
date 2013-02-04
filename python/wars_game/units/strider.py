from srcbase import *
from vmath import *
import random

from fields import BooleanField, FlagsField
from core.units import UnitInfo, UnitBaseCombat as BaseClass, UnitBaseAirLocomotion, EventHandlerAnimation
from core.abilities import AbilityUpgrade

from entities import entity, Activity, FireBulletsInfo_t, FBEAM_FADEOUT
from unit_helper import UnitAnimConfig, LegAnimType_t
from utils import UTIL_PlayerByIndex, UTIL_TraceLine, trace_t, UTIL_Tracer, TRACER_DONT_USE_ATTACHMENT, UTIL_PointContents
from gamerules import GetAmmoDef
from te import CEffectData, DispatchEffect, te

if isserver:
    from core.units import UnitCombatAirNavigator
    from utils import (UTIL_FindWaterSurface, UTIL_ScreenShake, SHAKE_START, UTIL_YawToVector, UTIL_PrecacheOther, 
                       UTIL_BloodSpray, FX_BLOODSPRAY_ALL, FX_BLOODSPRAY_DROPS, UTIL_Remove)
    from entities import (PropBreakableCreateAll, breakablepropparams_t, PropBreakablePrecacheAll, BCF_NO_ANIMATION_SKIP, 
                          EFL_NO_DISSOLVE, EFL_NO_MEGAPHYSCANNON_RAGDOLL, GetAttachmentPositionInSpaceOfBone,
                          BoneFollowerManager, CreateServerRagdollAttached, CTakeDamageInfo)
    from gameinterface import CPASAttenuationFilter, PrecacheMaterial, CPVSFilter, CBroadcastRecipientFilter
else:
    from te import ClientEffectRegistration
    from gameinterface import C_RecipientFilter
    
# Client side effect
if isclient:
    def MuzzleFlash_Strider(self, hEntity, attachmentIndex):
        # TODO
        pass
           
    def StriderMuzzleFlashCallback(data):
        pass
        #MuzzleFlash_Strider(data.entity, data.attachmentindex)
        
    StriderMuzzleFlash = ClientEffectRegistration('StriderMuzzleFlash', StriderMuzzleFlashCallback)
    
    
# Strider class
@entity('unit_strider', networked=True)
class UnitStrider(BaseClass):    
    """ Strider """
    def __init__(self):
        super(UnitStrider, self).__init__()
        self.savedrop = 2048.0
        self.maxclimbheight = 435.0
        self.testroutestartheight = 1024.0

        if isserver:
            self.SetShadowCastDistance(2048.0) # Use a much higher shadow cast distance
            
    # Shared
    if isserver:
        def Precache(self):
            PropBreakablePrecacheAll( self.unitinfo.modelname )
            
            self.PrecacheScriptSound( "NPC_Strider.StriderBusterExplode" )
            self.PrecacheScriptSound( "explode_5" )
            self.PrecacheScriptSound( "NPC_Strider.Charge" )
            self.PrecacheScriptSound( "NPC_Strider.RagdollDetach" )
            self.PrecacheScriptSound( "NPC_Strider.Whoosh" )
            self.PrecacheScriptSound( "NPC_Strider.Creak" )
            self.PrecacheScriptSound( "NPC_Strider.Alert" )
            self.PrecacheScriptSound( "NPC_Strider.Pain" )
            self.PrecacheScriptSound( "NPC_Strider.Death" )
            self.PrecacheScriptSound( "NPC_Strider.FireMinigun" )
            self.PrecacheScriptSound( "NPC_Strider.Shoot" )
            self.PrecacheScriptSound( "NPC_Strider.OpenHatch" )
            self.PrecacheScriptSound( "NPC_Strider.Footstep" )
            self.PrecacheScriptSound( "NPC_Strider.Skewer" )
            self.PrecacheScriptSound( "NPC_Strider.Hunt" )
            PrecacheMaterial( "effects/water_highlight" )
            self.impacteffecttexture = self.PrecacheModel( "sprites/physbeam.vmt" )
            PrecacheMaterial( "sprites/bluelaser1" )
            PrecacheMaterial( "effects/blueblacklargebeam" )
            PrecacheMaterial( "effects/strider_pinch_dudv" )
            PrecacheMaterial( "effects/blueblackflash" )
            PrecacheMaterial( "effects/strider_bulge_dudv" )
            PrecacheMaterial( "effects/strider_muzzle" )

            self.PrecacheModel( "models/chefhat.mdl" )

            #UTIL_PrecacheOther( "sparktrail" )

            super(UnitStrider, self).Precache()
    else:
        def Precache(self):
            self.impacteffecttexture = self.PrecacheModel( "sprites/physbeam.vmt" )
            super(UnitStrider, self).Precache()
        
    def Spawn(self):
        if isserver:
            self.EnableServerIK()
        
        self.minigunammo = GetAmmoDef().Index("StriderMinigun")
        self.minigundirectammo = GetAmmoDef().Index("StriderMinigunDirect")

        super(UnitStrider, self).Spawn()
        
        self.locomotion.desiredheight = 450.0
        self.locomotion.flynoiserate = 48.0
        self.locomotion.flynoisez = 24.0
        
        if isserver:
            self.SetDefaultEyeOffset()
            
            self.AddEFlags(EFL_NO_DISSOLVE|EFL_NO_MEGAPHYSCANNON_RAGDOLL)
            
            # Don't allow us to skip animation setup because our attachments are critical to us!
            self.SetBoneCacheFlags(BCF_NO_ANIMATION_SKIP)

            origin = self.GetLocalOrigin()
            origin.z += self.locomotion.desiredheight
            
            self.SetLocalOrigin(origin)
            
    def Weapon_ShootPosition(self):
        vecShootPos = Vector()
        self.GetAttachment(self.animstate.canonattachment, vecShootPos)

        return vecShootPos

    def MakeTracer(self, vecTracerSrc, tr, iTracerType):
        self.GetAttachment(self.animstate.minigunattachment, vecTracerSrc)
        UTIL_Tracer(vecTracerSrc, tr.endpos, self.entindex(), self.animstate.minigunattachment, 5000, True, "StriderTracer")
        
    def AdjustIdealHeight(self):
        self.SetPoseParameter(self.animstate.bodyheight, self.locomotion.desiredheight)
        
    def UnitThink(self):
        super(UnitStrider, self).UnitThink()
        
        #print 'forward: %f, sideward: %f' % (self.mv.forwardmove, self.mv.sidemove)
        
        self.AdjustIdealHeight()
        
        if self.ragdoll:
            self.bonefollowermanager.UpdateBoneFollowers(self)

    if isclient:
        def DoImpactEffect(self, tr, nDamageType):
            super(UnitStrider, self).DoImpactEffect(tr, nDamageType)

            # Add a halo
            #filter = CBroadcastRecipientFilter()
            filter = C_RecipientFilter()
            te.BeamRingPoint(filter, 0.0, 
                tr.endpos,							#origin
                0,									#start radius
                64,									#end radius
                self.impacteffecttexture,			#texture
                0,									#halo index
                0,									#start frame
                0,									#framerate
                0.2,								#life
                10,									#width
                0,									#spread
                0,									#amplitude
                255,								#r
                255,								#g
                255,								#b
                50,									#a
                0,									#speed
                FBEAM_FADEOUT
                )

            #filter = CPVSFilter(tr.endpos)
            filter = C_RecipientFilter()
            te.EnergySplash(filter, 0.0, tr.endpos, tr.plane.normal, False)
            
            # Punch the effect through?
            if tr.ent and not tr.ent.IsUnit():
                vecDir = tr.endpos - tr.startpos
                VectorNormalize( vecDir )

                retrace = trace_t()

                vecReTrace = tr.endpos + vecDir * 12

                if UTIL_PointContents( vecReTrace, MASK_ALL ) == CONTENTS_EMPTY:
                    UTIL_TraceLine( vecReTrace, vecReTrace - vecDir * 24, MASK_SHOT, None, COLLISION_GROUP_NONE, retrace )

                    super(UnitStrider, self).DoImpactEffect( retrace, nDamageType )
                
    def DoMuzzleFlash(self):
        super(UnitStrider, self).DoMuzzleFlash()
        
        data = CEffectData()
        
        data.attachmentindex = self.animstate.minigunattachment
        data.entindex = self.entindex()
        DispatchEffect( "StriderMuzzleFlash", data )
        
    def DispatchShootMinigun(self):
        if self.enemy:
            self.ShootMinigun(self.enemy.GetAbsOrigin(), 0.0, vec3_origin)
        elif self.controlledbyplayer:
            player = UTIL_PlayerByIndex(self.controlledbyplayer)
            if not player:
                return
            
            forward = Vector()
            AngleVectors(player.GetAbsAngles(), forward)
            start = player.Weapon_ShootPosition()
        
            tr = trace_t()
            UTIL_TraceLine(start, start+forward*MAX_TRACE_LENGTH, MASK_SHOT, self, COLLISION_GROUP_NONE, tr)
    
            self.ShootMinigun(tr.endpos, 0.0, vec3_origin)
    
    def ShootMinigun(self, target, aimError, vecSpread):
        if target:
            muzzlePos = Vector()
            muzzleAng = QAngle()
            
            self.GetAttachment( "minigun", muzzlePos, muzzleAng )
            
            vecShootDir = target - muzzlePos
            VectorNormalize( vecShootDir )
            
            info = FireBulletsInfo_t()
            info.shots = 1
            info.vecsrc = muzzlePos
            info.vecdirshooting = vecShootDir
            info.vecspread = vecSpread
            info.distance = MAX_TRACE_LENGTH
            info.tracerfreq = 0
            info.damage = self.unitinfo.AttackRange.damage
    
            if self.minigunusedirectfire:
                # exactly on target w/tracer
                info.ammotype = self.minigundirectammo
            else:
                # exactly on target w/tracer
                info.ammotype = self.minigunammo
            self.FireBullets(info)

            #g_pEffects.MuzzleFlash(muzzlePos, muzzleAng, random.uniform(2.0, 4.0) , MUZZLEFLASH_TYPE_STRIDER)
            self.DoMuzzleFlash()

            self.EmitSound('NPC_Strider.FireMinigun')
            
    def StartRangeAttack(self):
        self.DoAnimation(self.ANIM_RANGE_ATTACK1) 
        self.nextattacktime = gpGlobals.curtime + self.unitinfo.AttackRange.attackspeed
        return False
        
    # Server only
    if isserver:
        def InitBoneFollowers(self):
            self.bonefollowermanager = BoneFollowerManager()
            
            # Don't do this if we're already loaded
            if self.bonefollowermanager.GetNumBoneFollowers() != 0:
                return;

            # Init our followers
            self.bonefollowermanager.InitBoneFollowers(self, self.followerbonenames)
            
        def CreateVPhysics(self):
            # The strider has bone followers for every solid part of its body, 
            # so there's no reason for the bounding box to be solid.
            #super(UnitStrider, self).CreateVPhysics();

            if not self.disablebonefollowers:
                self.InitBoneFollowers()

            return True

        def UpdateOnRemove(self):
            if self.bonefollowermanager:
                self.bonefollowermanager.DestroyBoneFollowers()
            
            super(UnitStrider, self).UpdateOnRemove()
            
        def Explode(self):
            velocity = vec3_origin
            angVelocity = RandomAngularImpulse( -150, 150 )

            # Break into pieces
            params = breakablepropparams_t( self.EyePosition(), self.GetAbsAngles(), velocity, angVelocity )
            params.impactEnergyScale = 1.0
            params.defBurstScale = 600.0
            params.defCollisionGroup = COLLISION_GROUP_NPC
            PropBreakableCreateAll( self.GetModelIndex(), None, params, self, -1, True, True )

            # Go away
            self.lifestate = LIFE_DEAD

            self.SetThink( self.SUB_Remove )
            self.SetNextThink( gpGlobals.curtime + 0.1 )

            self.AddEffects( EF_NODRAW )
            
            self.StopSmoking()

            self.bonefollowermanager.DestroyBoneFollowers()

        def Event_Killed(self, info):
            super(UnitStrider, self).Event_Killed(info)
            
            self.bonefollowermanager.DestroyBoneFollowers()
            
        def StartSmoking(self):
            if self.smoke != None:
                return

            # TODO: Add smoke trail to python
            #self.smoke = SmokeTrail.CreateSmokeTrail()
            
            if self.smoke:
                self.smoke.m_SpawnRate = 32
                self.smoke.m_ParticleLifetime = 3.0
                self.smoke.m_StartSize = 16
                self.smoke.m_EndSize = 64
                self.smoke.m_SpawnRadius = 20
                self.smoke.m_MinSpeed = 8
                self.smoke.m_MaxSpeed = 64
                self.smoke.m_Opacity = 0.3
                
                self.smoke.m_StartColor.Init( 0.25, 0.25, 0.25 )
                self.smoke.m_EndColor.Init( 0, 0, 0 )
                self.smoke.SetLifetime( 500.0 )
                self.smoke.FollowEntity( self, "MiniGunBase" )
                
        def StopSmoking(self, delay=0.1):
            if self.smoke:
                self.smoke.SetLifetime(delay)
                
        def LeftFootHit(self, eventtime):
            footPosition = Vector()
            angles = QAngle()

            self.GetAttachment( "left foot", footPosition, angles )

            filter = CPASAttenuationFilter( self, "NPC_Strider.FootstepEverywhere" )
            self.EmitSoundFilter( filter, 0, "NPC_Strider.FootstepEverywhere", footPosition, eventtime )

            self.FootFX( footPosition )

            return footPosition

        def RightFootHit(self, eventtime):
            footPosition = Vector()

            self.GetAttachment( "right foot", footPosition )
            
            filter = CPASAttenuationFilter( self, "NPC_Strider.FootstepEverywhere" )
            self.EmitSoundFilter( filter, 0, "NPC_Strider.FootstepEverywhere", footPosition, eventtime )

            self.FootFX( footPosition )

            return footPosition

        def BackFootHit(self, eventtime):
            footPosition = Vector()

            self.GetAttachment( "back foot", footPosition )

            filter = CPASAttenuationFilter( self, "NPC_Strider.FootstepEverywhere" )
            self.EmitSoundFilter( filter, 0, "NPC_Strider.FootstepEverywhere", footPosition, eventtime )

            self.FootFX( footPosition )

            return footPosition
            
        def FootFX(self, origin):
            tr = trace_t()
            UTIL_TraceLine( origin + Vector(0, 0, 48), origin - Vector(0,0,100), MASK_SOLID_BRUSHONLY, self, COLLISION_GROUP_NONE, tr )
            yaw = random.randint(0,120)
            
            if UTIL_PointContents( tr.endpos + Vector( 0, 0, 1 ), MASK_WATER ) & MASK_WATER:
                flWaterZ = UTIL_FindWaterSurface( tr.endpos, tr.endpos.z, tr.endpos.z + 100.0 )

                data = CEffectData()
                data.flags = 0
                data.origin = tr.endpos
                data.origin.z = flWaterZ
                data.normal = Vector( 0, 0, 1 )
                data.scale = random.uniform( 10.0, 14.0 )

                DispatchEffect( "watersplash", data )
            else:
                filter = CPVSFilter( origin )
                for i in range(0, 3):
                    dir = UTIL_YawToVector( yaw + i*120 ) * 10
                    VectorNormalize( dir )
                    dir.z = 0.25
                    VectorNormalize( dir )
                    te.Dust(filter, 0.0, tr.endpos, dir, 12, 50)

            UTIL_ScreenShake( tr.endpos, 4.0, 1.0, 0.5, 1000, SHAKE_START, False )
            
            #if npc_strider_shake_ropes_radius.GetInt():
            #    CRopeKeyframe.ShakeRopes( tr.endpos, npc_strider_shake_ropes_radius.GetFloat(), npc_strider_shake_ropes_magnitude.GetFloat() )

            #
            # My feet are scary things! NOTE: We might want to make danger sounds as the feet move
            # through the air. Then soldiers could run from the feet, which would look cool.
            #
            #CSoundEnt.InsertSound( SOUND_DANGER|SOUND_CONTEXT_EXCLUDE_COMBINE, tr.endpos, 512, 1.0, self )
            
        def CalculateStompHitPosition(self, enemy):
            skewerPosition = Vector()
            footPosition = Vector()
            self.GetAttachment("left skewer", skewerPosition)
            self.GetAttachment("left foot", footPosition)
            vecStabPos = (enemy.WorldSpaceCenter() + enemy.EyePosition()) * 0.5

            return vecStabPos - skewerPosition + footPosition
            
        def StompHit(self, followerboneindex):
            self.bonefollowermanager.UpdateBoneFollowers(self)
            
            pStudioHdr = self.GetModelPtr()
            bone = self.bonefollowermanager.GetBoneFollower(followerboneindex)

            if not bone.follower:
                return

            pBoneNames = ["left skewer", "right skewer"]
            nameIndex = 0 if followerboneindex == self.STRIDER_LEFT_LEG_FOLLOWER_INDEX else 1
            localHit = GetAttachmentPositionInSpaceOfBone(pStudioHdr, pBoneNames[nameIndex], bone.boneindex)
            pLegPhys = bone.follower.VPhysicsGetObject()

            # now transform into the worldspace of the current position of the leg's physics
            legToWorld = matrix3x4_t()
            pLegPhys.GetPositionMatrix(legToWorld)
            hitPosition = Vector()
            VectorTransform(localHit, legToWorld, hitPosition)

            #NDebugOverlay::Box( hitPosition, Vector(-16,-16,-16), Vector(16,16,16), 0, 255, 0, 255, 1.0 )
            enemy = self.stomptarget
            if not enemy:
                enemy = self.enemy
            pNPC = enemy if enemy.IsUnit() else None
            bIsValidTarget = pNPC and pNPC.GetModelPtr()
            if self.HasSpawnFlags(self.SF_CAN_STOMP_PLAYER):
                bIsValidTarget = bIsValidTarget or (enemy and enemy.IsPlayer())

            if not bIsValidTarget:
                return

            delta = Vector()
            VectorSubtract(enemy.GetAbsOrigin(), hitPosition, delta)
            if delta.LengthSqr() > (self.STRIDER_STOMP_RANGE * self.STRIDER_STOMP_RANGE):
                return

            # DVS E3 HACK: Assume we stab our victim midway between their eyes and their center.
            vecStabPos = (enemy.WorldSpaceCenter() + enemy.EyePosition()) * 0.5
            hitPosition = enemy.GetAbsOrigin()

            footPosition = Vector()
            self.GetAttachment("left foot", footPosition)

            filter = CPASAttenuationFilter(self, "NPC_Strider.Skewer")
            self.EmitSoundFilter(filter, 0, "NPC_Strider.Skewer", hitPosition)

            damageInfo = CTakeDamageInfo(self, self, 500, DMG_CRUSH)
            forward = Vector()
            enemy.GetVectors(forward, None, None)
            damageInfo.SetDamagePosition(hitPosition)
            damageInfo.SetDamageForce(forward * -50 * 300)
            enemy.TakeDamage( damageInfo )

            if not pNPC or pNPC.IsAlive():
                return

            vecBloodDelta = footPosition - vecStabPos
            vecBloodDelta.z = 0 # effect looks better 
            VectorNormalize(vecBloodDelta)
            UTIL_BloodSpray(vecStabPos + vecBloodDelta * 4, vecBloodDelta, BLOOD_COLOR_RED, 8, FX_BLOODSPRAY_ALL)
            UTIL_BloodSpray(vecStabPos + vecBloodDelta * 4, vecBloodDelta, BLOOD_COLOR_RED, 11, FX_BLOODSPRAY_DROPS)
            pRagdoll = CreateServerRagdollAttached(pNPC, vec3_origin, -1, COLLISION_GROUP_DEBRIS, pLegPhys, self, bone.boneindex, vecStabPos, -1, localHit)
            if pRagdoll:
                # the strider might drag this through the world
                pRagdoll.AddSolidFlags(FSOLID_NOT_SOLID)

                self.ragdoll = pRagdoll
                self.ragdolltime = gpGlobals.curtime + 10
                UTIL_Remove(pNPC)
            
        # Event handlers
        def DieHandler(self, event):
            self.Explode()
            
        def LeftFootHitHandler(self, event):
            self.LeftFootHit(event.eventtime)
        def RightFootHitHandler(self, event):
            self.RightFootHit(event.eventtime)
        def BackFootHitHandler(self, event):
            self.BackFootHit(event.eventtime)
            
        def StompLHandler(self, event):
            self.StompHit(self.STRIDER_LEFT_LEG_FOLLOWER_INDEX)
        def StompRHandler(self, event):
            self.StompHit(self.STRIDER_RIGHT_LEG_FOLLOWER_INDEX)
        
        # Animation Events
        # Good thing the strider ones are hard coded...
        STRIDER_AE_FOOTSTEP_LEFT = 1
        STRIDER_AE_FOOTSTEP_RIGHT = 2
        STRIDER_AE_FOOTSTEP_BACK = 3
        STRIDER_AE_FOOTSTEP_LEFTM = 4
        STRIDER_AE_FOOTSTEP_RIGHTM = 5
        STRIDER_AE_FOOTSTEP_BACKM = 6
        STRIDER_AE_FOOTSTEP_LEFTL = 7
        STRIDER_AE_FOOTSTEP_RIGHTL = 8
        STRIDER_AE_FOOTSTEP_BACKL = 9
        STRIDER_AE_WHOOSH_LEFT = 11
        STRIDER_AE_WHOOSH_RIGHT = 12
        STRIDER_AE_WHOOSH_BACK = 13
        STRIDER_AE_CREAK_LEFT = 21
        STRIDER_AE_CREAK_RIGHT = 22
        STRIDER_AE_CREAK_BACK = 23
        STRIDER_AE_SHOOTCANNON = 100
        STRIDER_AE_CANNONHIT = 101
        STRIDER_AE_SHOOTMINIGUN = 105
        STRIDER_AE_STOMPHITL = 110
        STRIDER_AE_STOMPHITR = 111
        STRIDER_AE_FLICKL = 112
        STRIDER_AE_FLICKR = 113
        STRIDER_AE_WINDUPCANNON = 114

        STRIDER_AE_DIE = 999
        
        aetable = {
            STRIDER_AE_DIE : DieHandler,
            STRIDER_AE_SHOOTCANNON : None,
            STRIDER_AE_WINDUPCANNON : None,
            STRIDER_AE_CANNONHIT : None,
            STRIDER_AE_SHOOTMINIGUN : None,
            STRIDER_AE_STOMPHITL : StompLHandler,
            STRIDER_AE_STOMPHITR : StompRHandler,
            STRIDER_AE_FLICKL : None,
            STRIDER_AE_FLICKR : None,
            STRIDER_AE_FOOTSTEP_LEFT : LeftFootHitHandler,
            STRIDER_AE_FOOTSTEP_LEFTM : LeftFootHitHandler,
            STRIDER_AE_FOOTSTEP_LEFTL : LeftFootHitHandler,
            STRIDER_AE_FOOTSTEP_RIGHT : RightFootHitHandler,
            STRIDER_AE_FOOTSTEP_RIGHTM : RightFootHitHandler,
            STRIDER_AE_FOOTSTEP_RIGHTL : RightFootHitHandler,
            STRIDER_AE_FOOTSTEP_BACK : BackFootHitHandler,
            STRIDER_AE_FOOTSTEP_BACKM : BackFootHitHandler,
            STRIDER_AE_FOOTSTEP_BACKL : BackFootHitHandler,
        }
        
    # These bones have physics shadows
    # It allows a one-way interaction between the strider and
    # the physics world
    followerbonenames = [
        # Head
        "Combine_Strider.Body_Bone",
        "Combine_Strider.Neck_Bone",
        "Combine_Strider.Gun_Bone1",
        "Combine_Strider.Gun_Bone2",

        # lower legs
        "Combine_Strider.Leg_Left_Bone1",
        "Combine_Strider.Leg_Right_Bone1",
        "Combine_Strider.Leg_Hind_Bone1",
        
        # upper legs
        "Combine_Strider.Leg_Left_Bone",
        "Combine_Strider.Leg_Right_Bone",
        "Combine_Strider.Leg_Hind_Bone",
    ]

    # NOTE: These indices must directly correlate with the above list!
    STRIDER_BODY_FOLLOWER_INDEX = 0
    STRIDER_NECK_FOLLOWER_INDEX = 1
    STRIDER_GUN1_FOLLOWER_INDEX = 2
    STRIDER_GUN2_FOLLOWER_INDEX = 3
    
    STRIDER_LEFT_LEG_FOLLOWER_INDEX = 4
    STRIDER_RIGHT_LEG_FOLLOWER_INDEX = 5
    STRIDER_BACK_LEG_FOLLOWER_INDEX = 6

    STRIDER_LEFT_UPPERLEG_FOLLOWER_INDEX = 7
    STRIDER_RIGHT_UPPERLEG_FOLLOWER_INDEX = 8
    STRIDER_BACK_UPPERLEG_FOLLOWER_INDEX = 9

    aiclimb = False
    LocomotionClass = UnitBaseAirLocomotion
    if isserver:
        NavigatorClass = UnitCombatAirNavigator
    
    # Animation state
    animconfig = UnitAnimConfig(
        maxbodyyawdegrees=90.0,
        leganimtype=LegAnimType_t.LEGANIM_8WAY,
        useaimsequences=False,
    )
    class AnimStateClass(BaseClass.AnimStateClass):
        def __init__(self, *args, **kwargs):
            super(UnitStrider.AnimStateClass, self).__init__(*args, **kwargs)
            self.playfallactinair = False
            
        def OnNewModel(self):
            super(UnitStrider.AnimStateClass, self).OnNewModel()
            
            studiohdr = self.outer.GetModelPtr()
            
            self.bodyheight = self.outer.LookupPoseParameter(studiohdr, "body_height")
            self.yawcontrol = self.outer.LookupPoseParameter(studiohdr, "yaw")
            self.pitchcontrol = self.outer.LookupPoseParameter(studiohdr, "pitch")
            self.canonattachment = self.outer.LookupAttachment("BigGun")
            self.minigunattachment = self.outer.LookupAttachment("MiniGun")
            
            # Bind minigun yaw/pitch to body yaw/pitch.
            # This way the pose parameters will be adjusted to the eye angles
            self.bodyyaw = self.outer.LookupPoseParameter("minigunYaw")
            self.bodypitch = self.outer.LookupPoseParameter("minigunPitch")
            
            self.outer.SetPoseParameter(self.bodyheight, self.outer.locomotion.desiredheight)
            
    def EventHandlerRangeAttack1(self, data):
        self.DispatchShootMinigun()
            
    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_RANGE_ATTACK1' : EventHandlerRangeAttack1,
        'ANIM_STOMPL' : EventHandlerAnimation('ACT_STRIDER_STOMPL'),
        'ANIM_STOMPR' : EventHandlerAnimation('ACT_STRIDER_STOMPR'),
    } )
    
    # Activities
    activitylist = list(BaseClass.activitylist)
    activitylist.extend([
        "ACT_STRIDER_LOOKL",
        "ACT_STRIDER_LOOKR",
        "ACT_STRIDER_DEPLOYRA1",
        "ACT_STRIDER_AIMRA1",
        "ACT_STRIDER_FINISHRA1",
        "ACT_STRIDER_DODGER",
        "ACT_STRIDER_DODGEL",
        "ACT_STRIDER_STOMPL",
        "ACT_STRIDER_STOMPR",
        "ACT_STRIDER_FLICKL",
        "ACT_STRIDER_FLICKR",
        "ACT_STRIDER_CARRIED",
        "ACT_STRIDER_DEPLOY",
        "ACT_STRIDER_GESTURE_DEATH",
        'ACT_STRIDER_SLEEP',
    ])

    # Spawn flags
    spawnflags = FlagsField(keyname='spawnflags', flags=
        [('SF_CAN_STOMP_PLAYER', 0x10000, False), 
         ('SF_TAKE_MINIMAL_DAMAGE_FROM_NPCS', 0x20000, False)], 
        cppimplemented=True)
            
    # Vars
    smoke = None
    minigunusedirectfire = False
    stomptarget = None
    bonefollowermanager = None
    ragdoll = None
    
    # Settings
    scaleprojectedtexture = 3.5
    projectedtexturedist = 600.0
    maxspeed = 133.0 #365.0 #500.0
    yawspeed = 10.0
    jumpheight = 0.0
    
    disablebonefollowers = BooleanField(value=False, keyname='disablephysics')
    
    STRIDER_STOMP_RANGE = 260

class StriderUnlock(AbilityUpgrade):
    name = 'strider_unlock'
    displayname = '#CombStriderUnlock_Name'
    description = '#CombStriderUnlock_Description'
    image_name = "vgui/combine/abilities/strider_unlock"
    buildtime = 300.0
    costs = [[('requisition', 20), ('power', 30)], [('kills', 5)]]
    
class StriderInfo(UnitInfo):
    name = 'unit_strider'
    cls_name = 'unit_strider'
    displayname = '#CombStrider_Name'
    description = '#CombStrider_Description'
    image_name = 'vgui/combine/units/unit_strider'
    costs = [('requisition', 30), ('power', 20)]
    buildtime = 120.0
    modelname = 'models/combine_strider.mdl'
    hulltype = 'HULL_LARGE_CENTERED'
    techrequirements = ['strider_unlock']
    health = 2000
    population = 6
    attributes = ['synth', 'bullet']
    sound_death = 'NPC_Strider.Death'
    abilities = {
        0 : 'impale',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    class AttackRange(UnitInfo.AttackRange):
        damage = 10
        maxrange = 950.0
        attackspeed = 0.1
    attacks = 'AttackRange'
    