from srcbase import *
from vmath import *
from basedota import UnitDotaInfo, UnitDota as BaseClass
from unit_helper import UnitAnimConfig, LegAnimType_t
from entities import entity, Activity, ACT_INVALID
import random
from particles import DispatchParticleEffect, PATTACH_POINT_FOLLOW
from particles import *

if isserver:
    from core.units import BaseAction
    from entities import SpawnBlood
    #from unit_helper import BaseAnimEventHandler, EmitSoundAnimEventHandler
    
    from entities import (CSprite, gEntList, ImpulseScale, CalculateExplosiveDamageForce,
                          CTakeDamageInfo, D_HT, CalculateMeleeDamageForce)
    from utils import (UTIL_Remove, CTraceFilterMelee, CTraceFilterEntitiesOnly, CTraceFilter, trace_t, Ray_t, UTIL_TraceRay, UTIL_TraceHull, StandardFilterRules, PassServerEntityFilter,
                       UTIL_ScreenShake, SHAKE_START)
    from particles import PrecacheParticleSystem
else:
    from entities import DataUpdateType_t
    
@entity('hero_doom', networked=True)
class UnitDoom(BaseClass):
    """ Infected """
    def __init__(self):
        super(UnitDoom, self).__init__()

    def Precache(self):
        super(UnitDoom, self).Precache()
        
        if isserver:
            PrecacheParticleSystem("doom_bringer_ambient")
            PrecacheParticleSystem("doom_scorched_earth_primary")
            PrecacheParticleSystem("doom_bringer_devour")
            PrecacheParticleSystem("doom_bringer_doom")

    def Spawn(self):
        self.Precache()

        super(UnitDoom, self).Spawn()
        
        #if isserver:
            #att = self.LookupAttachment('attach_attack1')
            #att = self.LookupAttachment('attach_weapon_blur')
            #print att
            #DispatchParticleEffect('doom_bringer_ambient', PATTACH_POINT_FOLLOW, self, att)
            
    if isclient:
        def OnDataChanged(self, type):
            super(UnitDoom, self).OnDataChanged(type)
            
            if type == DataUpdateType_t.DATA_UPDATE_CREATED:
                self.CreateFlame()
                
        def CreateFlame(self):
            prop = self.ParticleProp()
            
            att = self.LookupAttachment('attach_attack1')
            #att = self.LookupAttachment('attach_weapon_blur')
           # print att
            self.flamefx = prop.Create('doom_bringer_ambient', PATTACH_POINT_FOLLOW, att)
            #print self.flamefx
            if self.flamefx:
                for i in range(0, 6):
                    prop.AddControlPoint(self.flamefx, i, self, PATTACH_POINT_FOLLOW, 'attach_attack1')
                    
        def DestroyFlame(self):
            pass
            
        def UpdateOnRemove(self):
            self.DestroyFlame()

            super(UnitDoom, self).UpdateOnRemove()
        
    if isserver:
        def StartMeleeAttack(self):  
            # Do melee damage
            self.MeleeAttack() 
                
            return super(UnitDoom, self).StartMeleeAttack()
        
    def MeleeAttack(self):
        #target = self.enemy
        #if not target:
        #    return
        
        attackinfo = self.unitinfo.AttackMelee
        damage = attackinfo.damage
        
        # If the target's still inside the shove cone, ensure we hit him
        # vecForward = Vector()
        # vecEnd = Vector()
        # AngleVectors( self.GetAbsAngles(), vecForward )
        # flDistSqr = ( target.WorldSpaceCenter() - self.WorldSpaceCenter() ).LengthSqr()
        # v2LOS = ( target.WorldSpaceCenter() - self.WorldSpaceCenter() ).AsVector2D()
        # Vector2DNormalize(v2LOS)
        # flDot	= DotProduct2D (v2LOS, vecForward.AsVector2D() )
        # if flDistSqr < (self.attackinfo.maxrange*self.attackinfo.maxrange) and flDot >= self.ANTLIONGUARD_MELEE1_CONE:
            # vecEnd = target.WorldSpaceCenter()
        # else:
        vecEnd = self.WorldSpaceCenter() + (self.BodyDirection3D() * attackinfo.maxrange)

        # Use the melee trace to ensure we hit everything there
        tr = trace_t()
        dmgInfo = CTakeDamageInfo(self, self, damage, attackinfo.damagetype)
        traceFilter = CTraceFilterMelee( self, Collision_Group_t.COLLISION_GROUP_NONE, dmgInfo, 1.0, True )
        ray = Ray_t()
        ray.Init( self.WorldSpaceCenter(), vecEnd, Vector(-40,-40,   0), Vector(40, 40, 100)) #Vector(-16,-16,-16), Vector(16,16,16) ) # <- Use a rather big ray to ensure we hit something. It's really annoying to see it hit the air.
        UTIL_TraceRay( ray, MASK_SHOT_HULL, traceFilter, tr ) 
        pHurt = tr.ent



        if pHurt:
            traceDir = ( tr.endpos - tr.startpos )
            VectorNormalize( traceDir )

            # Generate enough force to make a 75kg guy move away at 600 in/sec
            vecForce = traceDir * ImpulseScale(75, 600)
            info = CTakeDamageInfo(self, self, vecForce, tr.endpos, damage, DMG_CLUB)
            pHurt.TakeDamage( info )

            #self.EmitSound("NPC_AntlionGuard.Shove")
            
        # Knock things around
        self.ImpactShock(tr.endpos, 512.0, 2500.0)
        
    def ImpactShock(self, origin, radius, magnitude, ignored = None):
        # Also do a local physics explosion to push objects away
        vecSpot = Vector()
        falloff = 1.0 / 2.5

        entity = None

        # Find anything within our radius
        
        while True:
            entity = gEntList.FindEntityInSphere( entity, origin, radius )
            if entity == None:
                break
            # Don't affect the ignored target
            if entity == ignored:
                continue
            if entity == self:
                continue

            # UNDONE: Ask the object if it should get force if it's not MOVETYPE_VPHYSICS?
#if entity.GetMoveType() == MOVETYPE_VPHYSICS or ( entity.VPhysicsGetObject() and entity.IsPlayer() == False ):
            vecSpot = entity.BodyTarget( self.GetAbsOrigin(), True )
            
            # decrease damage for an ent that's farther from the bomb.
            flDist = ( self.GetAbsOrigin() - vecSpot ).Length()

            if radius == 0 or flDist <= radius:
                adjustedDamage = flDist * falloff
                adjustedDamage = magnitude - adjustedDamage
        
                if adjustedDamage < 1:
                    adjustedDamage = 1

                info = CTakeDamageInfo( self, self, adjustedDamage, DMG_BLAST )
                CalculateExplosiveDamageForce( info, (vecSpot - self.GetAbsOrigin()), self.GetAbsOrigin() )

                entity.VPhysicsTakeDamage( info )
                    
    # Vars
    maxspeed = 290.0
    yawspeed = 40.0
    jumpheight = 40.0

# Register unit
class UnitDoomInfo(UnitDotaInfo):
    name = "hero_doom"
    cls_name = "hero_doom"
    displayname = "#DOTA_Doom_Name"
    description = "#DOTA_Doom_Description"
    image_name = "vgui/units/unit_shotgun.vmt"
    modelname = 'models/heroes/doom/doom.mdl'
    hulltype = 'HULL_HUMAN'
    health = 250

    #sound_select = ''
    #sound_move = ''
    #sound_death = ''
    
    abilities = {
        8 : "attackmove",
        9 : "holdposition",
    }
    
    class AttackMelee(UnitDotaInfo.AttackMelee):
        maxrange = 150.0
        damage = 50
        damagetype = DMG_SLASH
        attackspeed = 1.6
    attacks = 'AttackMelee'
    