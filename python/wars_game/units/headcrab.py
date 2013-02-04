from math import sqrt
from vmath import Vector, QAngle, VectorSubtract, AngleVectors, VectorAngles, VectorNormalize, DotProduct, vec3_origin, vec3_angle, VectorMultiply, AngleNormalize
from srcbase import FL_ONGROUND, DAMAGE_NO, MASK_NPCSOLID, DMG_SLASH, FL_FLY, EF_NOINTERP
from core.units import UnitInfo, UnitBaseCombat as BaseClass, EventHandlerAnimation
from entities import entity, networked, Activity, D_HT, CTakeDamageInfo, CalculateMeleeDamageForce 
from gameinterface import ConVarRef
from utils import trace_t, UTIL_TraceEntity, UTIL_SetOrigin
import random

if isserver:
    from unit_helper import BaseAnimEventHandler
    from core.units.intention import BaseAction
    
sv_gravity = ConVarRef('sv_gravity')

@networked
class UnitBaseHeadcrab(BaseClass):
    if isserver:
        def MoveOrigin(self, vecdelta):
            UTIL_SetOrigin(self, self.GetLocalOrigin() + vecdelta)

        def Leap(self, vecvel):
            self.SetTouch(self.LeapTouch)

            self.SetGroundEntity(None)

            self.ignoreworldcollisiontime = gpGlobals.curtime + self.HEADCRAB_IGNORE_WORLD_COLLISION_TIME

            if self.HasHeadroom():
                # Take him off ground so engine doesn't instantly reset FL_ONGROUND.
                self.MoveOrigin(Vector(0, 0, 3))

            self.AddFlag(FL_FLY)
            self.SetAbsVelocity(vecvel)

            # Think every frame so the player sees the headcrab where he actually is...
            self.midjump = True
            self.SetThink(self.ThrowThink, gpGlobals.curtime, "ThrowThink")
            
        def ThrowThink(self):
            if self.GetFlags() & FL_ONGROUND:
                self.midjump = False
                return

            self.SetNextThink(gpGlobals.curtime, "ThrowThink")
            
        def ThrowAt(self, vecPos):
            self.JumpAttack(False, vecPos, True)
    
        def JumpAttack(self, randomjump, vecpos=vec3_origin, thrown=False):
            """ Does a jump attack at the given position. 
            
                randomjump - Just hop in a random direction.
                vecpos - Position to jump at, ignored if bRandom is set to true.
                thrown - 
            """
            vecJumpVel = Vector()
            if not randomjump:
                gravity = sv_gravity.GetFloat()
                if gravity <= 1:
                    gravity = 1

                # How fast does the headcrab need to travel to reach the position given gravity?
                flActualHeight = vecpos.z - self.GetAbsOrigin().z
                height = flActualHeight
                if height < 16:
                    height = 16
                else:
                    flMaxHeight = 400 if thrown else 120
                    if height > flMaxHeight:
                        height = flMaxHeight

                # overshoot the jump by an additional 8 inches
                # NOTE: This calculation jumps at a position INSIDE the box of the enemy (player)
                # so if you make the additional height too high, the crab can land on top of the
                # enemy's head.  If we want to jump high, we'll need to move vecpos to the surface/outside
                # of the enemy's box.
                
                additionalHeight = 0
                if height < 32:
                    additionalHeight = 8

                height += additionalHeight

                # NOTE: This equation here is from vf^2 = vi^2 + 2*a*d
                speed = sqrt( 2 * gravity * height )
                time = speed / gravity

                # add in the time it takes to fall the additional height
                # So the impact takes place on the downward slope at the original height
                time += sqrt( (2 * additionalHeight) / gravity )

                # Scale the sideways velocity to get there at the right time
                VectorSubtract(vecpos, self.GetAbsOrigin(), vecJumpVel)
                vecJumpVel /= time

                # Speed to offset gravity at the desired height.
                vecJumpVel.z = speed

                # Don't jump too far/fast.
                flJumpSpeed = vecJumpVel.Length()
                flMaxSpeed = 1000.0 if thrown else 650.0
                if flJumpSpeed > flMaxSpeed:
                    vecJumpVel *= flMaxSpeed / flJumpSpeed
            else:
                #
                # Jump hop, don't care where.
                #
                forward = Vector()
                up = Vector()
                AngleVectors(self.GetLocalAngles(), forward, None, up)
                vecJumpVel = Vector(forward.x, forward.y, up.z) * 350

            self.AttackSound()
            self.Leap(vecJumpVel)

        def HasHeadroom(self):
            """ Before jumping, headcrabs usually use SetOrigin() to lift themselves off the 
                ground. If the headcrab doesn't have the clearance to so, they'll be stuck
                in the world. So this function makes sure there's headroom first. 
            """
            tr = trace_t()
            UTIL_TraceEntity(self, self.GetAbsOrigin(), self.GetAbsOrigin() + Vector(0, 0, 1), 
                    MASK_NPCSOLID, self, self.GetCollisionGroup(), tr)

            return (tr.fraction == 1.0)

        def LeapTouch(self, other):
            """ LeapTouch - this is the headcrab's touch function when it is in the air.
            
                other - 
            """
            self.midjump = False
            self.RemoveFlag(FL_FLY)

            if self.IRelationType(other) == D_HT:
                # Don't hit if back on ground
                if not ( self.GetFlags() & FL_ONGROUND ):
                    if other.takedamage != DAMAGE_NO:
                        self.BiteSound()
                        self.TouchDamage(other)

                        # attack succeeded, so don't delay our next attack if we previously thought we failed
                        self.attackfailed = False
                    else:
                        self.ImpactSound()
                else:
                    self.ImpactSound()
            elif not (self.GetFlags() & FL_ONGROUND):
                # Still in the air...
                if not other.IsSolid():
                    # Touching a trigger or something.
                    return

                # just ran into something solid, so the attack probably failed.  make a note of it
                # so that when the attack is done, we'll delay attacking for a while so we don't
                # just repeatedly leap at the enemy from a bad location.
                self.attackfailed = True

                if gpGlobals.curtime < self.ignoreworldcollisiontime:
                    # Headcrabs try to ignore the world, static props, and friends for a 
                    # fraction of a second after they jump. This is because they often brush
                    # doorframes or props as they leap, and touching those objects turns off
                    # this touch function, which can cause them to hit the player and not bite.
                    # A timer probably isn't the best way to fix this, but it's one of our 
                    # safer options at this point (sjb).
                    return
                    
            # Shut off the touch function.
            self.SetTouch(None)
            
        def CalcDamageInfo(self, info):
            attackinfo = self.unitinfo.AttackRange
            info.Set(self, self, attackinfo.damage, attackinfo.damagetype)
            CalculateMeleeDamageForce(info, self.GetAbsVelocity(), self.GetAbsOrigin())
            return info.GetDamage()

        def TouchDamage(self, other):
            """ Deal the damage from the headcrab's touch attack. """
            info = CTakeDamageInfo()
            self.CalcDamageInfo(info)
            other.TakeDamage(info)
            
        def CrawlFromCanister(self):
            """ The headcrab will crawl from the cannister, then jump to a burrow point """
            # This is necessary to prevent ground computations, etc. from happening
            # while the crawling animation is occuring
            assert(not self.behaviorgeneric.actions) # Shouldn't have any actions on the stack yet
            self.AddFlag(FL_FLY)
            self.behaviorgeneric.StartingAction = self.behaviorgeneric.ActionStartCrawlFromCanister
            
        # Eliminates roll + pitch from the headcrab
        HEADCRAB_ROLL_ELIMINATION_TIME = 0.3
        HEADCRAB_PITCH_ELIMINATION_TIME = 0.3

        def EliminateRollAndPitch(self):
            """ Eliminates roll + pitch potentially in the headcrab at canister jump time """
            angles = self.GetAbsAngles()
            angles.x = AngleNormalize( angles.x )
            angles.z = AngleNormalize( angles.z )
            if ( angles.x == 0.0 ) and ( angles.z == 0.0 ):
                return

            flPitchRate = 90.0 / self.HEADCRAB_PITCH_ELIMINATION_TIME
            flPitchDelta = flPitchRate * gpGlobals.interval_per_tick
            if abs( angles.x ) <= flPitchDelta:
                angles.x = 0.0
            else:
                flPitchDelta *= -1.0 if (angles.x > 0.0) else 1.0
                angles.x += flPitchDelta

            flRollRate = 180.0 / self.HEADCRAB_ROLL_ELIMINATION_TIME
            flRollDelta = flRollRate * gpGlobals.interval_per_tick
            if abs( angles.z ) <= flRollDelta:
                angles.z = 0.0
            else:
                flRollDelta *=  -1.0 if (angles.z > 0.0) else 1.0
                angles.z += flRollDelta

            self.SetAbsAngles(angles)

            self.SetThink(self.EliminateRollAndPitch, gpGlobals.curtime + gpGlobals.interval_per_tick, "PitchContext")

        def BeginClimbFromCanister(self):
            """ Begins the climb from the canister """
            assert(self.GetMoveParent())
            # Compute a desired position or hint
            vecForward = Vector()
            vecActualForward = Vector()
            AngleVectors(self.GetMoveParent().GetAbsAngles(), vecActualForward)
            vecForward = vecActualForward
            vecForward.z = 0.0
            VectorNormalize(vecForward)

            vecSearchCenter = self.GetAbsOrigin()

            # Choose a random direction (forward, left, or right)
            self.jumpfromcanisterdir = random.randint(0, 2)

            self.DoAnimation(self.ANIM_HEADCRAB_CRAWL_FROM_CANISTER, self.jumpfromcanisterdir)

        HEADCRAB_ATTACK_PLAYER_FROM_CANISTER_DIST = 250.0
        HEADCRAB_ATTACK_PLAYER_FROM_CANISTER_COSANGLE = 0.866

        def JumpFromCanister(self):
            """ Jumps from the canister """
            assert(self.GetMoveParent())

            vecForward = Vector()
            vecActualForward = Vector()
            vecActualRight = Vector()
            AngleVectors(self.GetMoveParent().GetAbsAngles(), vecActualForward, vecActualRight, None)

            if self.jumpfromcanisterdir == 0:
                VectorMultiply(vecActualRight, -1.0, vecForward)
            elif self.jumpfromcanisterdir == 1:
                vecForward = vecActualForward
            elif self.jumpfromcanisterdir == 2:
                vecForward = vecActualRight

            vecForward.z = 0.0
            VectorNormalize(vecForward)
            headCrabAngles = QAngle()
            VectorAngles(vecForward, headCrabAngles)

            #self.SetActivity( ACT_RANGE_ATTACK1 )
            #self.StudioFrameAdvanceManual( 0.0 )
            self.SetParent(None)
            self.RemoveFlag(FL_FLY)
            self.AddEffects(EF_NOINTERP)
            self.SetOwnerEntity(None)

            #GetMotor().SetIdealYaw( headCrabAngles.y )
            
            # Check to see if the player is within jump range. If so, jump at him!
            bJumpedAtEnemy = False

            # FIXME: Can't use GetEnemy() here because enemy only updates during
            # schedules which are interruptible by COND_NEW_ENEMY or COND_LOST_ENEMY
            if self.enemy:
                vecDirToEnemy = Vector()
                VectorSubtract(self.enemy.GetAbsOrigin(), self.GetAbsOrigin(), vecDirToEnemy)
                vecDirToEnemy.z = 0.0
                flDist = VectorNormalize(vecDirToEnemy)
                if ( ( flDist < self.HEADCRAB_ATTACK_PLAYER_FROM_CANISTER_DIST ) and 
                    ( DotProduct(vecDirToEnemy, vecForward) >= self.HEADCRAB_ATTACK_PLAYER_FROM_CANISTER_COSANGLE ) ):
                    #GrabHintNode( NULL )
                    self.JumpAttack(False, self.enemy.EyePosition(), False)
                    bJumpedAtEnemy = True
 

            if not bJumpedAtEnemy:
                vecForward *= 100.0
                vecForward += self.GetAbsOrigin()
                self.JumpAttack(False, vecForward, False)

            self.EliminateRollAndPitch()

        def BiteSound(self): pass
        def ImpactSound(self): pass
        def ImpactSound(self): pass
        def TelegraphSound(self): pass
    
        class HeadcrabJumpAttack(BaseAnimEventHandler):
            def HandleEvent(self, unit, event):
                # Ignore if we're in mid air
                if unit.midjump:
                    return

                enemy = unit.enemy
                if enemy and unit.controllerplayer is None:
                    if unit.committedtojump:
                        unit.JumpAttack(False, unit.veccommittedjumppos)
                    else:
                        # Jump at my enemy's eyes.
                        unit.JumpAttack(False, enemy.EyePosition())

                    unit.committedtojump = False
                else:
                    # Jump hop, don't care where.
                    unit.JumpAttack(True)
                    
        class HeadcrabJumpTelegraph(BaseAnimEventHandler):
            def HandleEvent(self, unit, event):
                unit.TelegraphSound()
                
                if unit.enemy:
                    self.veccommittedjumppos = unit.enemy.EyePosition()
                    self.committedtojump = True
                    
                    
        # AI
        class BehaviorGenericClass(BaseClass.BehaviorGenericClass):
            class ActionStartCrawlFromCanister(BaseAction):
                def OnStart(self):
                    self.outer.BeginClimbFromCanister()
                    return self.ChangeTo(self.behavior.ActionCrawlFromCanister, 'Waiting for activity', 
                            activity=self.outer.animstate.specificmainactivity, transitionaction=self.behavior.ActionJumpFromCanister)
                    
            class ActionCrawlFromCanister(BaseClass.BehaviorGenericClass.ActionWaitForActivityTransition):
                def OnStart(self):
                    # Disable movement, and make sure the local origin and angles are on zero
                    self.outer.SetLocalOrigin(vec3_origin)
                    self.outer.SetLocalAngles(vec3_angle)
                    self.outer.locomotionenabled = False
                    return super(UnitHeadcrab.BehaviorGenericClass.ActionCrawlFromCanister, self).OnStart()
                def Update(self):
                    self.outer.AutoMovement()
                    return super(UnitHeadcrab.BehaviorGenericClass.ActionCrawlFromCanister, self).Update()
                def OnEnd(self):
                    self.outer.locomotionenabled = True
                    return super(UnitHeadcrab.BehaviorGenericClass.ActionCrawlFromCanister, self).OnEnd()
                    
            class ActionJumpFromCanister(BaseAction):
                def OnStart(self):
                    self.outer.JumpFromCanister()
                    return self.ChangeTo(self.behavior.ActionIdle, 'Canister actions done')
                    
    def EventHandlerCrawFromCanister(self, data):
        animstate = self.animstate
        if data == 0:
            animstate.specificmainactivity = self.ACT_HEADCRAB_CRAWL_FROM_CANISTER_LEFT
        elif data == 1:
            animstate.specificmainactivity = self.ACT_HEADCRAB_CRAWL_FROM_CANISTER_CENTER
        elif data == 2:
            animstate.specificmainactivity = self.ACT_HEADCRAB_CRAWL_FROM_CANISTER_RIGHT
        animstate.RestartMainSequence()

    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_HEADCRAB_CRAWL_FROM_CANISTER' : EventHandlerCrawFromCanister,
    } )
    
    maxspeed = 50.0
    yawspeed = 15.0
    
    midjump = False
    committedtojump = False
    ignoreworldcollisiontime = 0.0
    
    HEADCRAB_IGNORE_WORLD_COLLISION_TIME = 0.5
    
    # Activity list
    activitylist = list(BaseClass.activitylist)
    activitylist.extend( [
        'ACT_HEADCRAB_THREAT_DISPLAY',
        'ACT_HEADCRAB_HOP_LEFT',
        'ACT_HEADCRAB_HOP_RIGHT',
        'ACT_HEADCRAB_DROWN',
        'ACT_HEADCRAB_BURROW_IN',
        'ACT_HEADCRAB_BURROW_OUT',
        'ACT_HEADCRAB_BURROW_IDLE',
        'ACT_HEADCRAB_CRAWL_FROM_CANISTER_LEFT',
        'ACT_HEADCRAB_CRAWL_FROM_CANISTER_CENTER',
        'ACT_HEADCRAB_CRAWL_FROM_CANISTER_RIGHT',
        'ACT_HEADCRAB_CEILING_FALL',
        'ACT_HEADCRAB_CEILING_IDLE',
        'ACT_HEADCRAB_CEILING_DETACH',
        'ACT_HEADCRAB_CEILING_LAND',
    ] )
    
    # Activity translation table
    acttables = { 
        Activity.ACT_WALK : Activity.ACT_RUN,
    }
    
    if isserver:
        # Animation Events
        aetable = {
            'AE_HEADCRAB_JUMPATTACK' : HeadcrabJumpAttack(),
            'AE_HEADCRAB_JUMP_TELEGRAPH' : HeadcrabJumpTelegraph(),
            'AE_HEADCRAB_BURROW_IN' : None,
            'AE_HEADCRAB_BURROW_IN_FINISH' : None,
            'AE_HEADCRAB_BURROW_OUT' : None,
            'AE_HEADCRAB_CEILING_DETACH' : None,
        }
        
@entity('unit_headcrab')
class UnitHeadcrab(UnitBaseHeadcrab):
    def Precache(self):
        super(UnitHeadcrab, self).Precache()
        
        self.PrecacheScriptSound("NPC_HeadCrab.Gib")
        self.PrecacheScriptSound("NPC_HeadCrab.Idle")
        self.PrecacheScriptSound("NPC_HeadCrab.Alert")
        self.PrecacheScriptSound("NPC_HeadCrab.Pain")
        self.PrecacheScriptSound("NPC_HeadCrab.Die")
        self.PrecacheScriptSound("NPC_HeadCrab.Attack")
        self.PrecacheScriptSound("NPC_HeadCrab.Bite")
        self.PrecacheScriptSound("NPC_Headcrab.BurrowIn")
        self.PrecacheScriptSound("NPC_Headcrab.BurrowOut")

    def TelegraphSound(self):
        #FIXME: Need a real one
        self.EmitSound("NPC_HeadCrab.Alert")

    def AttackSound(self):
        self.EmitSound("NPC_Headcrab.Attack")

    def BiteSound(self):
        self.EmitSound("NPC_HeadCrab.Bite")
        
    maxspeed = 75.0 # Small speed buf compared to the original hl2 headcrab
        
@entity('unit_headcrab_fast')
class UnitFastHeadcrab(UnitBaseHeadcrab):
    def Precache(self):
        super(UnitFastHeadcrab, self).Precache()
        
        self.PrecacheScriptSound("NPC_FastHeadcrab.Idle")
        self.PrecacheScriptSound("NPC_FastHeadcrab.Alert")
        self.PrecacheScriptSound("NPC_FastHeadcrab.Pain")
        self.PrecacheScriptSound("NPC_FastHeadcrab.Die")
        self.PrecacheScriptSound("NPC_FastHeadcrab.Bite")
        self.PrecacheScriptSound("NPC_FastHeadcrab.Attack")
        
    def TelegraphSound(self):
        #FIXME: Need a real one
        self.EmitSound("NPC_FastHeadcrab.Alert")

    def AttackSound(self):
        self.EmitSound("NPC_FastHeadcrab.Attack")

    def BiteSound(self):
        self.EmitSound("NPC_FastHeadcrab.Bite")
        
    maxspeed = 230.0
    
@entity('unit_headcrab_poison')
class UnitBlackHeadcrab(UnitBaseHeadcrab):
    def Precache(self):
        super(UnitBlackHeadcrab, self).Precache()
        
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Telegraph" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Attack" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Bite" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Threat" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Alert" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Idle" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Talk" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.AlertVoice" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Pain" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Die" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Impact" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.ImpactAngry" )

        self.PrecacheScriptSound( "NPC_BlackHeadcrab.FootstepWalk" )
        self.PrecacheScriptSound( "NPC_BlackHeadcrab.Footstep" )
        
    def TelegraphSound(self):
        #FIXME: Need a real one
        self.EmitSound("NPC_BlackHeadcrab.Alert")

    def AttackSound(self):
        self.EmitSound("NPC_BlackHeadcrab.Attack")

    def BiteSound(self):
        self.EmitSound("NPC_BlackHeadcrab.Bite")
        
            
    #-----------------------------------------------------------------------------
    # Purpose: Bails out of our host zombie, either because he died or was blown
    #			into two pieces by an explosion.
    # Input  : vecAngles - The yaw direction we should face.
    #			flVelocityScale - A multiplier for our ejection velocity.
    #			pEnemy - Who we should acquire as our enemy. Usually our zombie host's enemy.
    #-----------------------------------------------------------------------------
    def Eject(self, vecAngles, flVelocityScale, pEnemy):
        self.SetGroundEntity(None)
        #self.AddSpawnFlags(SF_NPC_FALL_TO_GROUND)

        if pEnemy:
            self.enemy = pEnemy

        self.DoAnimation(self.ANIM_RANGE_ATTACK1)

        self.SetNextThink(gpGlobals.curtime)
        self.PhysicsSimulate()

        #GetMotor().SetIdealYaw( vecAngles.y )

        self.SetAbsVelocity( Vector( random.uniform( -1.0, 1.0 ), random.uniform( -1.0, 1.0 ), random.uniform( 0.5, 1.0 ) ) *
                                flVelocityScale * random.randint( 20, 50 ) )

        self.midjump = False
        self.SetTouch(self.EjectTouch)

    #-----------------------------------------------------------------------------
    # Purpose: Touch function for when we are ejected from the poison zombie.
    #			Panic when we hit the ground.
    #-----------------------------------------------------------------------------
    def EjectTouch(self, pOther):
        self.LeapTouch(pOther)
        #if self.GetFlags() & FL_ONGROUND:
            # Keep trying to take cover for at least a few seconds.
        #    self.Panic(random.uniform( 2, 8 ))
        
    maxspeed = 35.0

# Register units
class HeadcrabInfo(UnitInfo):
    name = 'unit_headcrab'
    displayname = '#ZomHeadcrab_Name'
    description = '#ZomHeadcrab_Description'
    cls_name = 'unit_headcrab'
    image_name = 'vgui/units/unit_shotgun.vmt'
    health = 150
    attributes = ['light', 'slash']
    modelname = 'models/headcrabclassic.mdl'
    hulltype = 'HULL_TINY'
    sound_death = 'NPC_HeadCrab.Die'
    abilities = {
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
    class AttackRange(UnitInfo.AttackRange):
        maxrange = 512.0
        damage = 20
        damagetype = DMG_SLASH
        attackspeed = 1.2
    attacks = 'AttackRange'
    
class FastHeadcrabInfo(UnitInfo):
    name = 'unit_headcrab_fast'
    displayname = '#ZomHeadcrabFast_Name'
    description = '#ZomHeadcrabFast_Description'
    cls_name = 'unit_headcrab_fast'
    image_name = 'vgui/units/unit_shotgun.vmt'
    health = 180
    attributes = ['light', 'slash']
    modelname = 'models/headcrab.mdl'
    hulltype = 'HULL_TINY'
    sound_death = 'NPC_FastHeadcrab.Die'
    abilities = {
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
    class AttackRange(UnitInfo.AttackRange):
        maxrange = 512.0
        damage = 12
        damagetype = DMG_SLASH
        attackspeed = 1.2
    attacks = 'AttackRange'
    
class BlackHeadcrabInfo(UnitInfo):
    name = 'unit_headcrab_poison'
    displayname = '#ZomHeadcrabPoison_Name'
    description = '#ZomHeadcrabPoison_Description'
    cls_name = 'unit_headcrab_poison'
    image_name = 'vgui/units/unit_shotgun.vmt'
    health = 250
    attributes = ['heavy', 'slash']
    modelname = 'models/headcrabblack.mdl'
    hulltype = 'HULL_TINY'
    sound_death = 'NPC_BlackHeadcrab.Die'
    abilities = {
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
    class AttackRange(UnitInfo.AttackRange):
        maxrange = 512.0
        damage = 40
        damagetype = DMG_SLASH
        attackspeed = 1.2
    attacks = 'AttackRange'
    