from srcbase import SOLID_VPHYSICS, DMG_BLAST, SOLID_BBOX, FSOLID_NOT_STANDABLE, COLLISION_GROUP_INTERACTIVE
from vmath import Vector, vec3_origin, RandomAngularImpulse
from math import floor
from entities import entity
if isserver:
    from entities import CTakeDamageInfo, CLASS_NONE, RadiusDamage, CreateEntityByName, DispatchSpawn, breakablepropparams_t, PropBreakableCreateAll
    from particles import PrecacheParticleSystem, DispatchParticleEffect
    from utils import UTIL_Remove
    from gameinterface import CPASAttenuationFilter, CPVSFilter
from gameinterface import ConVarRef

from core.buildings import WarsTurretInfo, UnitBaseAutoTurret
from core.abilities import AbilityUpgrade
    
sv_gravity = ConVarRef('sv_gravity')

def clamp(val, min, max):
    return max if val > max else min if val < min else val

@entity('floor_turret', networked=True)
class FloorTurret(UnitBaseAutoTurret):
    def GetTracerType(self): return "AR2Tracer"
    
    if isserver:
        def Precache(self):
            super(FloorTurret, self).Precache()
            
            self.PrecacheScriptSound( "NPC_FloorTurret.AlarmPing")
            
            self.PrecacheScriptSound( "NPC_FloorTurret.Retire" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Deploy" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Move" )
            self.PrecacheScriptSound( "NPC_Combine.WeaponBash" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Activate" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Alert" )
            #self.shotsounds = self.PrecacheScriptSound( "NPC_FloorTurret.ShotSounds" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Die" )
            self.PrecacheScriptSound( "NPC_FloorTurret.Retract")
            self.PrecacheScriptSound( "NPC_FloorTurret.Alarm")
            self.PrecacheScriptSound( "NPC_FloorTurret.Ping")
            self.PrecacheScriptSound( "NPC_FloorTurret.DryFire")
            self.PrecacheScriptSound( "NPC_FloorTurret.Destruct" )
    
            PrecacheParticleSystem( "explosion_turret_break" )
            
        def Spawn(self):
            super(FloorTurret, self).Spawn()
            
            self.SetSolid(SOLID_BBOX)
            self.AddSolidFlags(FSOLID_NOT_STANDABLE)
            
        def DestructThink(self):
            """ The countdown to destruction! """
            # Continue to animate
            #PreThink( TURRET_SELF_DESTRUCTING )

            # If we're done, explode
            if ( gpGlobals.curtime - self.destructstarttime ) >= self.SELF_DESTRUCT_DURATION:
                self.SetThink( self.BreakThink )
                self.SetNextThink( gpGlobals.curtime + 0.1 )
                UTIL_Remove( self.fizzleeffect )
                self.fizzleeffect = None
                return
            

            # Find out where we are in the cycle of our destruction
            flDestructPerc = clamp( ( gpGlobals.curtime - self.destructstarttime ) / self.SELF_DESTRUCT_DURATION, 0.0, 1.0 )

            # Figure out when our next beep should occur
            flBeepTime = self.SELF_DESTRUCT_BEEP_MAX_DELAY + ( ( self.SELF_DESTRUCT_BEEP_MIN_DELAY - self.SELF_DESTRUCT_BEEP_MAX_DELAY ) * flDestructPerc )

            # If it's time to beep again, do so
            if gpGlobals.curtime > ( self.pingtime + flBeepTime ):
                # Figure out what our beep pitch will be
                flBeepPitch = self.SELF_DESTRUCT_BEEP_MIN_PITCH + ( ( self.SELF_DESTRUCT_BEEP_MAX_PITCH - self.SELF_DESTRUCT_BEEP_MIN_PITCH ) * flDestructPerc )
                
                self.StopSound( "NPC_FloorTurret.AlarmPing" )

                # Play the beep
                filter = CPASAttenuationFilter( self, "NPC_FloorTurret.AlarmPing" )
                #params = EmitSound()
                #params.m_pSoundName = "NPC_FloorTurret.AlarmPing"
                #params.m_nPitch = floor( flBeepPitch )
                #params.m_nFlags = SND_CHANGE_PITCH
                #self.EmitSound( filter, self.entindex(), params )
                self.EmitSound( "NPC_FloorTurret.AlarmPing" )
                
                # Flash our eye
                #SetEyeState( TURRET_EYE_ALARM )
                
                # Save this as the last time we pinged
                self.pingtime = gpGlobals.curtime
                
                # Randomly twitch
                #m_vecGoalAngles.x = GetAbsAngles().x + random.RandomFloat( -60*flDestructPerc, 60*flDestructPerc )
                #m_vecGoalAngles.y = GetAbsAngles().y + random.RandomFloat( -60*flDestructPerc, 60*flDestructPerc )
            
            
            #UpdateFacing()

            # Think again!
            self.SetNextThink( gpGlobals.curtime + 0.05 )

        def BreakThink(self):
            vecUp = Vector()
            self.GetVectors( None, None, vecUp )
            vecOrigin = self.WorldSpaceCenter() + ( vecUp * 12.0 )

            # Our effect
            DispatchParticleEffect( "explosion_turret_break", vecOrigin, self.GetAbsAngles() )

            # K-boom
            RadiusDamage( CTakeDamageInfo( self, self, 15.0, DMG_BLAST ), vecOrigin, (10*12), CLASS_NONE, self )

            self.EmitSound( "NPC_FloorTurret.Destruct" )

            params = breakablepropparams_t( self.GetAbsOrigin(), self.GetAbsAngles(), vec3_origin, RandomAngularImpulse( -800.0, 800.0 ) )
            params.impactEnergyScale = 1.0
            params.defCollisionGroup = COLLISION_GROUP_INTERACTIVE

            # no damage/damage force? set a burst of 100 for some movement
            params.defBurstScale = 100
            #PropBreakableCreateAll( self.GetModelIndex(), self.VPhysicsGetObject(), params, self, -1, True, True )
            PropBreakableCreateAll( self.GetModelIndex(), None, params, self, -1, True, True )

            # Throw out some small chunks too obscure the explosion even more
            #filter = CPVSFilter( vecOrigin )
            #for i in range(0, 4):
            #    gibVelocity = RandomVector(-100,100)
            #    iModelIndex = modelinfo.GetModelIndex( g_PropDataSystem.GetRandomChunkModel( "MetalChunks" ) )	
            #    te.BreakModel( filter, 0.0, vecOrigin, self.GetAbsAngles(), Vector(40,40,40), gibVelocity, iModelIndex, 150, 4, 2.5, BREAK_METAL )

            # We're done!
            UTIL_Remove( self )
            
        def Event_Killed(self, info):
            super(FloorTurret, self).Event_Killed(info)
            
            self.destructstarttime = gpGlobals.curtime
            self.pingtime = gpGlobals.curtime
            
            # Create the dust effect in place
            self.fizzleeffect = CreateEntityByName( "info_particle_system" )
            if self.fizzleeffect is not None:
                vecUp = Vector()
                self.GetVectors( None, None, vecUp )

                # Setup our basic parameters
                self.fizzleeffect.KeyValue( "start_active", "1" )
                self.fizzleeffect.KeyValue( "effect_name", "explosion_turret_fizzle" )
                self.fizzleeffect.SetParent( self )
                self.fizzleeffect.SetAbsOrigin( self.WorldSpaceCenter() + ( vecUp * 12.0 ) )
                DispatchSpawn( self.fizzleeffect )
                self.fizzleeffect.Activate()
            
    #def CreateVPhysics(self):
    #    #Spawn our physics hull
    #    if self.VPhysicsInitNormal( SOLID_VPHYSICS, 0, False ) == None:
    #        DevMsg( "npc_turret_floor unable to spawn physics object!\n" )
    #    return True

    autoconstruct = True
    aimtype = UnitBaseAutoTurret.AIMTYPE_POSE
    barrelattachmentname = 'eyes'
    ammotype = 'Pistol'
    firesound = "NPC_FloorTurret.ShotSounds"
    muzzleoptions = 'COMBINE eyes'
    
    # BUG: Client is missing these animations, so we cannot use them
    # If we do the turret becomes invisible on dedicated servers. Local it seems fine.
    #idleact = 'ACT_FLOOR_TURRET_OPEN_IDLE'
    #fireact = 'ACT_FLOOR_TURRET_FIRE'

    fizzleeffect = None
    
    SELF_DESTRUCT_DURATION = 4.0
    SELF_DESTRUCT_BEEP_MIN_DELAY = 0.1
    SELF_DESTRUCT_BEEP_MAX_DELAY = 0.75
    SELF_DESTRUCT_BEEP_MIN_PITCH = 100.0
    SELF_DESTRUCT_BEEP_MAX_PITCH = 225.0

# Unit registration
class FloorTurretInfo(WarsTurretInfo):
    # Info
    name = "floor_turret"
    cls_name = "floor_turret"
    hulltype = 'HULL_HUMAN'
    image_name = "vgui/abilities/ability_tripod.vmt"
    image_dis_name = "vgui/abilities/ability_tripod_dis"
    portrait = 'resource/portraits/combineTurret.bik'
    health = 300
    costs = [[('requisition', 5), ('power', 2)], [('kills', 5)]]
    buildtime = 15.0
    population = 2
    rechargetime = 25.0
    techrequirements = ['comb_tier2_research']
    modelname   = 'models/combine_turrets/floor_turret.mdl'
    displayname = "#FloorTurret_Name"
    description = "#FloorTurret_Description"
    #placemaxrange = 96
    targetatgroundonly = True
    techrequirements = ['floor_turret_unlock']
    activatesoundscript = '#deployturret'
    
    abilities = {
        #8 : 'attackmove',
    }
    
    # Ability
    infoprojtextures = [
        {'texture' : 'decals/turret_cone_120',
         'mins' : Vector(16, -1039, 0),
         'maxs' : Vector(1216, 1039, 128)}]
         
    class AttackTurret(WarsTurretInfo.AttackTurret):
        damage = 6
        attackspeed = 0.1
    attacks = 'AttackTurret'
         
class AbilityFloorTurretUnlock(AbilityUpgrade):
    name = 'floor_turret_unlock'
    displayname = '#AbilityFloorTurretUnlock_DisplayName'
    description = '#AbilityFloorTurretUnlock_Description'
    image_name = "vgui/abilities/ability_tripod.vmt"
    buildtime = 120.0
    costs = [[('kills', 5)], [('requisition', 5)]]
    
class OverrunFloorTurretInfo(FloorTurretInfo):
    name = "overrun_floor_turret"
    hidden = True
    techrequirements = ['or_tier2_research']
         