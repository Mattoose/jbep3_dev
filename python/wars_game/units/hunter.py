from srcbase import *
from vmath import Vector, QAngle, VectorNormalize, AngleVectors, DotProduct, RandomVector, VectorAngles
from entities import entity
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass
from core.abilities import AbilityUpgrade
from core.ents.homingprojectile import HomingProjectile
from unit_helper import UnitAnimConfig, LegAnimType_t
from particles import PrecacheParticleSystem, DispatchParticleEffect, StopParticleEffects, PATTACH_ABSORIGIN_FOLLOW, PATTACH_POINT_FOLLOW

if isserver:
    from entities import (CPhysicsProp, FClassnameIs, PropBreakablePrecacheAll, ClearMultiDamage, CTakeDamageInfo,
                          CalculateMeleeDamageForce, ApplyMultiDamage, RadiusDamage, CLASS_NONE,
                          CreateEntityByName)
    from utils import (UTIL_PrecacheOther, UTIL_SetOrigin, UTIL_SetSize, 
                       UTIL_ImpactTrace, UTIL_Remove, trace_t, UTIL_TraceLine, UTIL_PointContents)
    from te import CEffectData, DispatchEffect
    from gameinterface import ConVar, PrecacheMaterial
    from unit_helper import BaseAnimEventHandler, EmitSoundAnimEventHandler
    
if isserver:
    hunter_cheap_explosions = ConVar("hunter_cheap_explosions", "1")
    
    s_szHunterFlechetteBubbles = "HunterFlechetteBubbles"
    s_szHunterFlechetteSeekThink = "HunterFlechetteSeekThink"
    s_szHunterFlechetteDangerSoundThink = "HunterFlechetteDangerSoundThink"
    s_szHunterFlechetteSpriteTrail = "sprites/bluelaser1.vmt"
    s_nHunterFlechetteImpact = -2
    s_nFlechetteFuseAttach = -1

    FLECHETTE_AIR_VELOCITY = 2500

    HUNTER_FOV_DOT = 0.0 # 180 degree field of view
    HUNTER_CHARGE_MIN = 256
    HUNTER_CHARGE_MAX = 1024
    HUNTER_FACE_ENEMY_DIST = 512.0
    HUNTER_MELEE_REACH = 80
    HUNTER_BLOOD_LEFT_FOOT = 0
    HUNTER_IGNORE_ENEMY_TIME = 5 # How long the hunter will ignore another enemy when distracted by the player.

    HUNTER_FACING_DOT = 0.8 # The angle within which we start shooting
    HUNTER_SHOOT_MAX_YAW_DEG = 60.0 # Once shooting, clamp to +/- these degrees of yaw deflection as our target moves
    HUNTER_SHOOT_MAX_YAW_COS = 0.5 # The cosine of the above angle

    HUNTER_FLECHETTE_WARN_TIME = 1.0

    HUNTER_SEE_ENEMY_TIME_INVALID = -1

    NUM_FLECHETTE_VOLLEY_ON_FOLLOW = 4

    HUNTER_SIEGE_MAX_DIST_MODIFIER = 2.0
        
    @entity('hunter_flechette')
    class HunterFlechette(HomingProjectile):
        @staticmethod
        def FlechetteCreate(vecOrigin, angAngles, owner, damage=4.0, velocity=320):
            # Create a new entity with CHunterFlechette private data
            flechette = CreateEntityByName("hunter_flechette")
            UTIL_SetOrigin(flechette, vecOrigin)
            flechette.SetAbsAngles(angAngles)
            flechette.damage = damage
            flechette.velocity = velocity
            flechette.dietime = gpGlobals.curtime + 2.0
            flechette.explodetolerance = 32.0
            flechette.Spawn()
            flechette.Activate()
            flechette.SetOwnerEntity(owner)
            flechette.SetOwnerNumber(owner.GetOwnerNumber())
            flechette.SetTargetAndFire(owner.enemy)
            return flechette
            
        '''
        def __init__(self):
            super(HunterFlechette, self).__init__()
            self.UseClientSideAnimation()
            
        def CreateVPhysics(self):
            # Create the object in the physics system
            self.VPhysicsInitNormal(SOLID_BBOX, FSOLID_NOT_STANDABLE, False)
            return True
        '''
        
        def CreateSprites(self, bBright):
            if bBright:
                DispatchParticleEffect("hunter_flechette_trail_striderbuster", PATTACH_ABSORIGIN_FOLLOW, self)
            else:
                DispatchParticleEffect("hunter_flechette_trail", PATTACH_ABSORIGIN_FOLLOW, self)
            return True
        
        def Precache(self):
            super(HunterFlechette, self).Precache()
            
            self.PrecacheModel(self.HUNTER_FLECHETTE_MODEL)
            self.PrecacheModel("sprites/light_glow02_noz.vmt")

            self.PrecacheScriptSound("NPC_Hunter.FlechetteNearmiss")
            self.PrecacheScriptSound("NPC_Hunter.FlechetteHitBody")
            self.PrecacheScriptSound("NPC_Hunter.FlechetteHitWorld")
            self.PrecacheScriptSound("NPC_Hunter.FlechettePreExplode")
            self.PrecacheScriptSound("NPC_Hunter.FlechetteExplode")

            PrecacheParticleSystem("hunter_flechette_trail_striderbuster")
            PrecacheParticleSystem("hunter_flechette_trail")
            PrecacheParticleSystem("hunter_projectile_explosion_1")
            
            
        def Spawn(self):
            super(HunterFlechette, self).Spawn()
            
            self.SetModel(self.HUNTER_FLECHETTE_MODEL)
            #self.SetMoveType(MOVETYPE_FLYGRAVITY, MOVECOLLIDE_FLY_CUSTOM)
            UTIL_SetSize(self, -Vector(1,1,1), Vector(1,1,1))
            self.SetSolid(SOLID_BBOX)
            #self.SetGravity(0.05)
            self.SetCollisionGroup(COLLISION_GROUP_PROJECTILE)
            self.SetCollisionGroup(self.CalculateIgnoreOwnerCollisionGroup())
            
            # Make sure we're updated if we're underwater
            #self.UpdateWaterState()

            self.SetTouch(self.FlechetteTouch)

            # Make us glow until we've hit the wall
            self.skin = 1
            
        def Activate(self):
            super(HunterFlechette, self).Activate()
            self.SetupGlobalModelData()
            
        def SetupGlobalModelData(self):
            global s_nHunterFlechetteImpact, s_nFlechetteFuseAttach
            if s_nHunterFlechetteImpact == -2:
                s_nHunterFlechetteImpact = self.LookupSequence("impact")
                s_nFlechetteFuseAttach = self.LookupAttachment("attach_fuse")
            
        s_nImpactCount = 0
        def StickTo(self, pOther, tr):
            self.EmitSound( "NPC_Hunter.FlechetteHitWorld" )

            self.SetMoveType( MOVETYPE_NONE )
            
            if not pOther.IsWorld():
                self.SetParent(pOther)
                self.SetSolid(SOLID_NONE)
                self.SetSolidFlags(FSOLID_NOT_SOLID)

            # Do an impact effect.
            #Vector vecDir = GetAbsVelocity()
            #float speed = VectorNormalize( vecDir )

            #Vector vForward
            #AngleVectors( GetAbsAngles(), &vForward )
            #VectorNormalize ( vForward )

            #CEffectData	data
            #data.m_vOrigin = tr.endpos
            #data.m_vNormal = vForward
            #data.m_nEntIndex = 0
            #DispatchEffect( "BoltImpact", data )
            
            vecVelocity = self.GetAbsVelocity()
            bAttachedToBuster = False #StriderBuster_OnFlechetteAttach( pOther, vecVelocity )

            self.SetTouch(None)

            # We're no longer flying. Stop checking for water volumes.
            self.SetThink(None, 0, s_szHunterFlechetteBubbles)

            # Stop seeking.
            self.seektarget = None
            self.SetThink(None, 0, s_szHunterFlechetteSeekThink)

            # Get ready to explode.
            if not bAttachedToBuster:
                self.SetThink(self.DangerSoundThink)
                self.SetNextThink(gpGlobals.curtime + (self.explodedelay - HUNTER_FLECHETTE_WARN_TIME))
            else:
                self.DangerSoundThink()

            # Play our impact animation.
            self.ResetSequence(s_nHunterFlechetteImpact)

            self.s_nImpactCount += 1
            if self.s_nImpactCount & 0x01:
                UTIL_ImpactTrace(tr, DMG_BULLET)
                
                # Shoot some sparks
                # TODO
                #if UTIL_PointContents(self.GetAbsOrigin()) != CONTENTS_WATER:
                #    te.Sparks(self.GetAbsOrigin())

        def FlechetteTouch(self, pOther):
            if pOther.IsSolidFlagSet(FSOLID_VOLUME_CONTENTS | FSOLID_TRIGGER):
                # Some NPCs are triggers that can take damage (like antlion grubs). We should hit them.
                if (pOther.takedamage == DAMAGE_NO) or (pOther.takedamage == DAMAGE_EVENTS_ONLY):
                    return

            if FClassnameIs(pOther, "hunter_flechette"):
                return

            tr = super(HunterFlechette, self).GetTouchTrace()

            if pOther.takedamage != DAMAGE_NO:
                vecNormalizedVel = self.GetAbsVelocity()

                ClearMultiDamage()
                VectorNormalize(vecNormalizedVel)

                flDamage = self.damage
                #CBreakable *pBreak = dynamic_cast <CBreakable *>(pOther)
                #if ( pBreak and ( pBreak.GetMaterialType() == matGlass ) )
                #{
                #    flDamage = MAX( pOther.GetHealth(), flDamage )
                #}

                dmgInfo = CTakeDamageInfo(self, self.GetOwnerEntity(), flDamage, DMG_DISSOLVE | DMG_NEVERGIB)
                CalculateMeleeDamageForce(dmgInfo, vecNormalizedVel, tr.endpos, 0.7)
                dmgInfo.SetDamagePosition(tr.endpos)
                pOther.DispatchTraceAttack(dmgInfo, vecNormalizedVel, tr)

                ApplyMultiDamage()

                # Keep going through breakable glass.
                if pOther.GetCollisionGroup() == COLLISION_GROUP_BREAKABLE_GLASS:
                     return
                     
                self.SetAbsVelocity(Vector(0, 0, 0))

                # play body "thwack" sound
                self.EmitSound( "NPC_Hunter.FlechetteHitBody" )

                StopParticleEffects(self)

                vForward = Vector()
                AngleVectors(self.GetAbsAngles(), vForward)
                VectorNormalize(vForward)

                tr2 = trace_t()
                UTIL_TraceLine(self.GetAbsOrigin(), self.GetAbsOrigin() + vForward * 128, MASK_BLOCKLOS, pOther, COLLISION_GROUP_NONE, tr2)

                if tr2.fraction != 1.0:
                    #NDebugOverlay::Box( tr2.endpos, Vector( -16, -16, -16 ), Vector( 16, 16, 16 ), 0, 255, 0, 0, 10 )
                    #NDebugOverlay::Box( GetAbsOrigin(), Vector( -16, -16, -16 ), Vector( 16, 16, 16 ), 0, 0, 255, 0, 10 )

                    if tr2.ent == None or (tr2.ent and tr2.ent.GetMoveType() == MOVETYPE_NONE):
                        data = CEffectData()

                        data.origin = tr2.endpos
                        data.normal = vForward
                        data.entindex = tr2.fraction != 1.0
                    
                        #DispatchEffect( "BoltImpact", data )

                if ( ((pOther.GetMoveType() == MOVETYPE_VPHYSICS) or (pOther.GetMoveType() == MOVETYPE_PUSH)) and 
                    ((pOther.health > 0) or (pOther.takedamage == DAMAGE_EVENTS_ONLY)) ):
                    #pProp = dynamic_cast<CPhysicsProp *>( pOther )
                    #if pProp:
                    #    pProp.SetInteraction( PROPINTER_PHYSGUN_NOTIFY_CHILDREN )
                
                    # We hit a physics object that survived the impact. Stick to it.
                    self.StickTo(pOther, tr)
                else:
                    self.SetTouch(None)
                    self.SetThink(None)
                    self.SetThink(None, 0, s_szHunterFlechetteBubbles)

                    UTIL_Remove(self)
            else:
                # See if we struck the world
                if pOther.GetMoveType() == MOVETYPE_NONE and not( tr.surface.flags & SURF_SKY ):
                    # We hit a physics object that survived the impact. Stick to it.
                    self.StickTo( pOther, tr )
                elif pOther.GetMoveType() == MOVETYPE_PUSH and FClassnameIs(pOther, "func_breakable"):
                    # We hit a func_breakable, stick to it.
                    # The MOVETYPE_PUSH is a micro-optimization to cut down on the classname checks.
                    self.StickTo( pOther, tr )
                else:
                    # Put a mark unless we've hit the sky
                    if (tr.surface.flags & SURF_SKY) == False:
                        UTIL_ImpactTrace(tr, DMG_BULLET)

                    UTIL_Remove(self)

        def BubbleThink(self):
            """ Think every 0.1 seconds to make bubbles if we're flying through water. """
            self.SetNextThink(gpGlobals.curtime + 0.1, s_szHunterFlechetteBubbles)

            if self.GetWaterLevel()  == 0:
                return

            UTIL_BubbleTrail(self.GetAbsOrigin() - self.GetAbsVelocity() * 0.1, self.GetAbsOrigin(), 5)
            
        def Shoot(self, vecVelocity, bBrightFX):
            self.CreateSprites(bBrightFX)

            self.vecshootposition = self.GetAbsOrigin()

            self.SetAbsVelocity(vecVelocity)

            # Doppler think is single player only, needs mp implementation
            #self.SetThink(self.DopplerThink)
            #self.SetNextThink(gpGlobals.curtime)

            self.SetThink(self.BubbleThink, gpGlobals.curtime + 0.1, s_szHunterFlechetteBubbles)

        def DangerSoundThink(self):
            self.EmitSound( "NPC_Hunter.FlechettePreExplode" )

            #CSoundEnt.InsertSound( SOUND_DANGER|SOUND_CONTEXT_EXCLUDE_COMBINE, GetAbsOrigin(), 150.0f, 0.5, self )
            self.SetThink(self.ExplodeThink)
            self.SetNextThink(gpGlobals.curtime + HUNTER_FLECHETTE_WARN_TIME)

        def ExplodeThink(self):
            self.Explode()

        s_nExplosionCount = 0
        def Explode(self):
            self.SetSolid( SOLID_NONE )

            # Don't catch self in own explosion!
            self.takedamage = DAMAGE_NO

            self.EmitSound( "NPC_Hunter.FlechetteExplode" )
            
            # Move the explosion effect to the tip to reduce intersection with the world.
            vecFuse = Vector()
            self.GetAttachment( s_nFlechetteFuseAttach, vecFuse )
            DispatchParticleEffect("hunter_projectile_explosion_1", vecFuse, self.GetAbsAngles(), None)

            nDamageType = DMG_DISSOLVE

            # Perf optimization - only every other explosion makes a physics force. self is
            # hardly noticeable since flechettes usually explode in clumps.
            self.s_nExplosionCount += 1
            if (self.s_nExplosionCount & 0x01) and hunter_cheap_explosions.GetBool():
                nDamageType |= DMG_PREVENT_PHYSICS_FORCE

            RadiusDamage(CTakeDamageInfo(self, self.GetOwnerEntity(), self.explodedamage, nDamageType), self.GetAbsOrigin(), self.exploderadius, CLASS_NONE, None)
                
            self.AddEffects(EF_NODRAW)

            self.SetThink(self.SUB_Remove)
            self.SetNextThink(gpGlobals.curtime + 0.1)
            
        HUNTER_FLECHETTE_MODEL = "models/weapons/hunter_flechette.mdl"
        damage = 4.0
        explodedamage = 12.0
        exploderadius = 128.0
        explodedelay = 2.5
    
@entity('unit_hunter', networked=True)
class UnitHunter(BaseClass):
    if isserver:
        def Precache(self):
            super(UnitHunter, self).Precache()
        
            PropBreakablePrecacheAll("models/hunter.mdl")

            self.PrecacheScriptSound( "NPC_Hunter.Idle" )
            self.PrecacheScriptSound( "NPC_Hunter.Scan" )
            self.PrecacheScriptSound( "NPC_Hunter.Alert" )
            self.PrecacheScriptSound( "NPC_Hunter.Pain" )
            self.PrecacheScriptSound( "NPC_Hunter.PreCharge" )
            self.PrecacheScriptSound( "NPC_Hunter.Angry" )
            self.PrecacheScriptSound( "NPC_Hunter.Death" )
            self.PrecacheScriptSound( "NPC_Hunter.FireMinigun" )
            self.PrecacheScriptSound( "NPC_Hunter.Footstep" )
            self.PrecacheScriptSound( "NPC_Hunter.BackFootstep" )
            self.PrecacheScriptSound( "NPC_Hunter.FlechetteVolleyWarn" )
            self.PrecacheScriptSound( "NPC_Hunter.FlechetteShoot" )
            self.PrecacheScriptSound( "NPC_Hunter.FlechetteShootLoop" )
            self.PrecacheScriptSound( "NPC_Hunter.FlankAnnounce" )
            self.PrecacheScriptSound( "NPC_Hunter.MeleeAnnounce" )
            self.PrecacheScriptSound( "NPC_Hunter.MeleeHit" )
            self.PrecacheScriptSound( "NPC_Hunter.TackleAnnounce" )
            self.PrecacheScriptSound( "NPC_Hunter.TackleHit" )
            self.PrecacheScriptSound( "NPC_Hunter.ChargeHitEnemy" )
            self.PrecacheScriptSound( "NPC_Hunter.ChargeHitWorld" )
            self.PrecacheScriptSound( "NPC_Hunter.FoundEnemy" )
            self.PrecacheScriptSound( "NPC_Hunter.FoundEnemyAck" )
            self.PrecacheScriptSound( "NPC_Hunter.DefendStrider" )
            self.PrecacheScriptSound( "NPC_Hunter.HitByVehicle" )

            PrecacheParticleSystem( "hunter_muzzle_flash" )
            PrecacheParticleSystem( "blood_impact_synth_01" )
            PrecacheParticleSystem( "blood_impact_synth_01_arc_parent" )
            PrecacheParticleSystem( "blood_spurt_synth_01" )
            PrecacheParticleSystem( "blood_drip_synth_01" )

            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_scan.vcd" )
            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_eyeclose.vcd" )
            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_roar.vcd" )
            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_pain.vcd" )
            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_eyedarts_top.vcd" )
            #PrecacheInstancedScene( "scenes/npc/hunter/hunter_eyedarts_bottom.vcd" )
            
            PrecacheMaterial( "effects/water_highlight" )

            UTIL_PrecacheOther( "hunter_flechette" )
            #UTIL_PrecacheOther( "sparktrail" )

    def Spawn(self):
        super(UnitHunter, self).Spawn()
        
        self.SetupGlobalModelData()
        
    def OnRestore(self):
        super(UnitHunter, self).OnRestore()
        self.SetupGlobalModelData()
    
    def SetupGlobalModelData(self):
        if self.gm_nTopGunAttachment != -1:
            return 
                
        self.gm_nAimYawPoseParam = self.LookupPoseParameter( "aim_yaw" )
        self.gm_nAimPitchPoseParam = self.LookupPoseParameter( "aim_pitch" )

        self.gm_nBodyYawPoseParam = self.LookupPoseParameter( "body_yaw" )
        self.gm_nBodyPitchPoseParam = self.LookupPoseParameter( "body_pitch" )

        self.gm_nTopGunAttachment = self.LookupAttachment( "top_eye" )
        self.gm_nBottomGunAttachment = self.LookupAttachment( "bottom_eye" )
        self.gm_nStaggerYawPoseParam = self.LookupAttachment( "stagger_yaw" )
        
        self.gm_nHeadCenterAttachment = self.LookupAttachment( "head_center" )
        self.gm_nHeadBottomAttachment = self.LookupAttachment( "head_radius_measure" )

        # Measure the radius of the head.
        vecHeadCenter = Vector()
        vecHeadBottom = Vector()
        self.GetAttachment( self.gm_nHeadCenterAttachment, vecHeadCenter )
        self.GetAttachment( self.gm_nHeadBottomAttachment, vecHeadBottom )
        self.gm_flHeadRadius = ( vecHeadCenter - vecHeadBottom ).Length()

        #nSequence = self.SelectWeightedSequence( ACT_HUNTER_RANGE_ATTACK2_UNPLANTED )
        #self.gm_nUnplantedNode = GetEntryNode( nSequence )

        #nSequence = self.SelectWeightedSequence( ACT_RANGE_ATTACK2 )
        #self.gm_nPlantedNode = self.GetEntryNode( nSequence )

    def BleedThink(self):
        """ Our health is low. Show damage effects. """
        # Spurt blood from random points on the hunter's head.
        vecOrigin = Vector()
        angDir = QAngle()
        self.GetAttachment(self.gm_nHeadCenterAttachment, vecOrigin, angDir)
        
        vecDir = RandomVector( -1, 1 )
        VectorNormalize( vecDir )
        VectorAngles( vecDir, Vector( 0, 0, 1 ), angDir )

        vecDir *= self.gm_flHeadRadius
        DispatchParticleEffect( "blood_spurt_synth_01", vecOrigin + vecDir, angDir )

        self.SetNextThink( gpGlobals.curtime + random.uniform(0.6, 1.5), HUNTER_BLEED_THINK)

    def StartBleeding(self):
        # Do this even if we're already bleeding (see OnRestore).
        self.isbleeding = True

        # Start gushing blood from our... anus or something.
        DispatchParticleEffect("blood_drip_synth_01", PATTACH_POINT_FOLLOW, self, self.gm_nHeadBottomAttachment )

        # Emit spurts of our blood
        self.SetThink(self.BleedThink, gpGlobals.curtime + 0.1, HUNTER_BLEED_THINK)

    def DoMuzzleFlash(self, nAttachment):
        super(UnitHunter, self).DoMuzzleFlash()
        
        DispatchParticleEffect("hunter_muzzle_flash", PATTACH_POINT_FOLLOW, self, nAttachment)

        # Dispatch the elight
        data = CEffectData()
        data.attachmentindex = nAttachment
        data.entindex = self.entindex()
        DispatchEffect("HunterMuzzleFlash", data)

    def GetShootDir(self, vecSrc, pTargetEntity, bStriderBuster, nShotNum, bSingleShot):
        """ Given a target to shoot at, decide where to aim. """
        #RestartGesture( ACT_HUNTER_GESTURE_SHOOT )

        self.EmitSound("NPC_Hunter.FlechetteShoot")

        vecBodyTarget = Vector()

        #if pTargetEntity.Classify() == CLASS_PLAYER_ALLY_VITAL:
            # Shooting at Alyx, most likely (in EP2). The attack is designed to displace
            # her, not necessarily actually harm her. So shoot at the area around her feet.
        #    vecBodyTarget = pTargetEntity.GetAbsOrigin()
        #else:
        vecBodyTarget = pTargetEntity.BodyTarget(vecSrc)

        vecTarget = Vector(vecBodyTarget)

        vecDelta = pTargetEntity.GetAbsOrigin() - self.GetAbsOrigin()
        flDist = vecDelta.Length()

        if not bStriderBuster:
            # If we're not firing at a strider buster, miss in an entertaining way for the 
            # first three shots of each volley.
            '''
            if (nShotNum < 3) and (flDist > 200):
                vecTargetForward = Vector()
                vecTargetRight = Vector()
                pTargetEntity.GetVectors(vecTargetForward,vecTargetRight, None )

                vecForward = Vector()
                self.GetVectors(vecForward, None, None)

                flDot = DotProduct(vecTargetForward, vecForward)

                if flDot < -0.8:
                    # Our target is facing us, shoot the ground between us.
                    flPerc = 0.7 + ( 0.1 * nShotNum )
                    vecTarget = self.GetAbsOrigin() + ((pTargetEntity.GetAbsOrigin() * flPerc - self.GetAbsOrigin()))
                elif flDot > 0.8:
                    # Our target is facing away from us, shoot to the left or right.
                    vecMissDir = Vector(vecTargetRight)
                    if self.missleft:
                        vecMissDir *= -1.0

                    vecTarget = pTargetEntity.EyePosition() + vecMissDir * (36.0 * (3 - nShotNum))
                else:
                    # Our target is facing vaguely perpendicular to us, shoot across their view.
                    vecTarget = pTargetEntity.EyePosition() + vecTargetForward * (36.0 * (3 - nShotNum))
            '''
            # If we can't see them, shoot where we last saw them.
            #elif not self.HasCondition( COND_SEE_ENEMY ):
            #    Vector vecDelta = vecTarget - pTargetEntity.GetAbsOrigin()
            #    vecTarget = m_vecEnemyLastSeen + vecDelta
        else:
            # If we're firing at a striderbuster, lead it.
            flSpeed = self.flechettespeed

            flSpeed *= 1.5

            flDeltaTime = flDist / flSpeed
            vecTarget = vecTarget + flDeltaTime * pTargetEntity.GetSmoothedVelocity()

        vecDir = vecTarget - vecSrc
        VectorNormalize(vecDir)
        return vecDir

    def ShootFlechette(self, pTargetEntity, bSingleShot):
        if not pTargetEntity:
            return False

        nShotNum = self.volleysize - self.flechettesqueued

        bStriderBuster = False #IsStriderBuster(pTargetEntity)

        # Choose the next muzzle to shoot from.
        vecSrc = Vector()
        angMuzzle = QAngle()

        if self.topmuzzle:
            self.GetAttachment(self.gm_nTopGunAttachment, vecSrc, angMuzzle)
            self.DoMuzzleFlash(self.gm_nTopGunAttachment)
        else:
            self.GetAttachment(self.gm_nBottomGunAttachment, vecSrc, angMuzzle)
            self.DoMuzzleFlash(self.gm_nBottomGunAttachment)

        self.topmuzzle = not self.topmuzzle

        vecDir = self.GetShootDir(vecSrc, pTargetEntity, bStriderBuster, nShotNum, bSingleShot)

        bClamped = False
        #if hunter_clamp_shots.GetBool():
        #    bClamped = self.ClampShootDir( vecDir )

        #manipulator = CShotManipulator(vecDir)
        #vecShoot = Vector()

        #if( IsUsingSiegeTargets() and nShotNum >= 2 && (nShotNum % 2) == 0 )
            # Near perfect accuracy for these three shots, so they are likely to fly right into the windows.
            # NOTE! In siege behavior in the map that this behavior was designed for (ep2_outland_10), the
            # Hunters will only ever shoot at siege targets in siege mode. If you allow Hunters in siege mode
            # to attack players or other NPCs, this accuracy bonus will apply unless we apply a bit more logic to it.
        #    vecShoot = manipulator.ApplySpread( VECTOR_CONE_1DEGREES * 0.5, 1.0 )
        #else:
        #    vecShoot = manipulator.ApplySpread( VECTOR_CONE_4DEGREES, 1.0 )
        vecShoot = vecDir

        angShoot = QAngle()
        VectorAngles(vecShoot, angShoot)

        attackinfo = self.unitinfo.AttackRange
        flechette = HunterFlechette.FlechetteCreate(vecSrc, angShoot, self, damage=attackinfo.damage, velocity=self.flechettespeed)

        flechette.AddEffects(EF_NOSHADOW)

        #vecShoot *= self.flechettespeed

        #flechette.Shoot(vecShoot, bStriderBuster)

        #if self.ShouldSeekTarget(pTargetEntity, bStriderBuster):
        #    flechette.SetSeekTarget( pTargetEntity )

        #if nShotNum == 1 and pTargetEntity.Classify() == CLASS_PLAYER_ALLY_VITAL:
            # Make this person afraid and react to ME, not to the flechettes. 
            # Otherwise they could be scared into running towards the hunter.
            #CSoundEnt.InsertSound( SOUND_DANGER|SOUND_CONTEXT_REACT_TO_SOURCE|SOUND_CONTEXT_EXCLUDE_COMBINE, pTargetEntity.EyePosition(), 180.0f, 2.0f, this )

        return bClamped
        
    if isserver:
        def StartRangeAttack(self):
            attackinfo = self.unitinfo.AttackRange
            self.flechettesqueued = 1
            self.ShootFlechette(self.enemy, False)
            self.currentburst -= 1
            if self.currentburst <= 0:
                self.nextattacktime = gpGlobals.curtime + 1.2
                self.currentburst = 10
            else:
                self.nextattacktime = gpGlobals.curtime + attackinfo.attackspeed
            return True
    else:
        def StartRangeAttack(self): return False
        
    animconfig = UnitAnimConfig(
        maxbodyyawdegrees=60.0,
        leganimtype=LegAnimType_t.LEGANIM_8WAY,
        useaimsequences=False,
    )
    class AnimStateClass(BaseClass.AnimStateClass):
        def OnNewModel(self):
            super(UnitHunter.AnimStateClass, self).OnNewModel()
            
            studiohdr = self.outer.GetModelPtr()
            
            self.bodyyaw = self.outer.LookupPoseParameter("body_yaw")
            self.bodypitch = self.outer.LookupPoseParameter("body_pitch")
            
    if isserver:
        # Anim events
        aetable = {
            'AE_HUNTER_FOOTSTEP_LEFT' : EmitSoundAnimEventHandler('NPC_Hunter.Footstep'),
            'AE_HUNTER_FOOTSTEP_RIGHT' : EmitSoundAnimEventHandler('NPC_Hunter.Footstep'),
            'AE_HUNTER_FOOTSTEP_BACK' : EmitSoundAnimEventHandler('NPC_Hunter.BackFootstep'),
        }
        
    topmuzzle = False
    flechettesqueued = 0
    flechettedelay = 0.1
    currentburst = 10
    missleft = False
    
    gm_nTopGunAttachment = -1
    gm_nBottomGunAttachment = -1
    gm_nHeadBottomAttachment = -1
    
    volleysize = 8
    flechettespeed = 2000

    maxspeed = 349.0

class CombineHunterUnlock(AbilityUpgrade):
    name = 'combine_hunter_unlock'
    displayname = '#CombHunterUnlock_Name'
    description = '#CombHunterUnlock_Description'
    image_name = "vgui/abilities/ability_unknown.vmt"
    buildtime = 200.0
    costs = [[('kills', 5)], [('requisition', 5)]]
    
class CombineHunterInfo(UnitInfo):
    name        = 'unit_hunter'
    cls_name    = 'unit_hunter'
    displayname = '#CombHunter_Name'
    description = '#CombHunter_Description'
    image_name = 'vgui/combine/units/unit_hunter'
    costs = [('requisition', 8), ('power', 2)]
    buildtime = 60.0
    health = 300
    population = 2
    attributes = ['creature', 'bullet']
    modelname = 'models/hunter.mdl'
    hulltype = 'HULL_MEDIUM_TALL'
    abilities = {
        8 : 'attackmove',
        9 : 'holdposition',
    }
    class AttackRange(UnitInfo.AttackRange):
        damage = 4.0
        cone = 0.99
        maxrange = 820.0
        attackspeed = 0.1
    attacks = 'AttackRange'
    
class OverrunCombineHunterInfo(CombineHunterInfo):
    name = 'overrun_unit_hunter'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    costs = [('kills', 8)]
    