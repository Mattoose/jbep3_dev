from srcbase import *
from vmath import *
from entities import CBaseAnimating as BaseClass, entity
from particles import *
from fields import StringField, GenericField, FloatField
import ndebugoverlay
if isserver:
    from entities import CreateEntityByName, DispatchSpawn, FL_EDICT_ALWAYS, CTakeDamageInfo, D_HT
    from utils import UTIL_EntitiesInBox
    
@entity('projectile_homing', networked=True)
class HomingProjectile(BaseClass):
    """ Projectile that always hits the target. """
    #def ShouldDraw(self):
    #    return False
        
    def UpdateTransmitState(self):
        return self.SetTransmitState(FL_EDICT_ALWAYS)
        
    projfx = None
    def OnDataChanged(self, type):
        super(HomingProjectile, self).OnDataChanged(type)

        if self.projfx:
            self.UpdateLastKnowOrigin()
            self.projfx.SetControlPoint(1, self.lastorigin)
            self.projfx.SetControlPoint(2, Vector(self.velocity, 0, 0))
            
            if (self.GetAbsOrigin() - self.lastorigin).Length() < 32.0:
                self.projfx.StopEmission()
                self.projfx.SetControlPoint(2, Vector(0, 0, 0))
                return
                
    def OnParticleEffectChanged(self):
        if self.particleeffect and self.projtarget:
            prop = self.ParticleProp()
            
            self.UpdateLastKnowOrigin()
                
            # Assume the particle is using "pull toward control point".
            # Control point 1 is the target location.
            # Control point 2 is the force being used (of which only x is set)
            self.projfx = prop.Create(self.particleeffect, PATTACH_ABSORIGIN)
            self.projfx.SetControlPoint(1, self.lastorigin)
            self.projfx.SetControlPoint(2, Vector(self.velocity, 0, 0))
        else:
            self.projfx = None

    def UpdateLastKnowOrigin(self):
        if not self.projtarget:
            return
        self.lastorigin = self.projtarget.BodyTarget(self.GetAbsOrigin(), False)
            
    if isserver:
        def Precache(self):
            if self.particleeffect:
                PrecacheParticleSystem(self.particleeffect)
            if self.pexplosioneffect:
                PrecacheParticleSystem(self.pexplosioneffect)
            if self.modelname:
                self.PrecacheModel(self.modelname)
            
        def Spawn(self):
            self.health = 1
            self.Precache()
            self.SetSolid(SOLID_NONE)
            self.SetMoveType(MOVETYPE_STEP)
            self.SetSolidFlags(FSOLID_NOT_STANDABLE|FSOLID_NOT_SOLID)

            if self.modelname:
                self.SetModel(self.modelname)
                
        def SetTargetAndFire(self, projtarget):
            if not projtarget:
                PrintWarning("Firing projectile with invalid target!\n")
                self.Remove()
                return
            self.projtarget = projtarget
            self.lastorigin = projtarget.GetAbsOrigin()
            self.SetThink(self.ProjectileThink, gpGlobals.curtime)
            
        @classmethod
        def SpawnProjectile(cls, owner, origin, target, damage, velocity, particleeffect=None, modelname=None, pexplosioneffect=None):
            projectile = CreateEntityByName('projectile_homing')
            projectile.SetOwnerEntity(owner)
            projectile.SetOwnerNumber(owner.GetOwnerNumber())
            projectile.SetAbsOrigin(origin)
            projectile.modelname = modelname
            projectile.particleeffect = particleeffect
            projectile.pexplosioneffect = pexplosioneffect
            projectile.velocity = velocity
            projectile.damage = damage
            DispatchSpawn(projectile)
            projectile.SetTargetAndFire(target)
            
        def ProjectileThink(self):
            self.UpdateLastKnowOrigin()
            origin = self.GetAbsOrigin()
            dir = self.lastorigin  - origin
            dist = VectorNormalize(dir)
            traveldist = self.velocity * self.thinkfreq
            if dist < traveldist: traveldist = dist
            self.SetAbsOrigin(origin + (dir * traveldist))
            
            angles = QAngle()
            VectorAngles(dir, Vector(0, 0, 1), angles)
            self.SetAbsAngles(angles)
            
            if (self.GetAbsOrigin() - self.lastorigin).Length() < self.explodetolerance:
                self.Explode()
                return
                
            if self.dietime and self.dietime < gpGlobals.curtime:
                self.Explode()
                return
            
            self.SetNextThink(gpGlobals.curtime + self.thinkfreq)
            
        def Explode(self):
            if self.pexplosioneffect:
                DispatchParticleEffect(self.pexplosioneffect, PATTACH_ABSORIGIN, self)
            #StopParticleEffects(self)
            
            self.particleeffect = None
            
            flRadius = 128.0
            origin = self.GetAbsOrigin()
            if self.GetOwnerEntity():
                ownerorigin = self.GetOwnerEntity().GetAbsOrigin()
            else:
                ownerorigin = origin
                
            enemies = UTIL_EntitiesInBox(32, origin-Vector(flRadius,flRadius,flRadius), origin+Vector(flRadius,flRadius,flRadius), FL_NPC)
            for e in enemies:
                if not e or e == self or self.GetOwnerNumber() == e.GetOwnerNumber(): # TODO: Check relationtype
                    continue
                
                vecDir = (e.GetAbsOrigin() - origin)
                vecDir[2] = 0.0
                vecDir *= (flRadius * 2.0)
                vecDir[2] = 2500.0
                e.ApplyAbsVelocityImpulse(vecDir)
                
                # splat!
                vecDir[2] += 400.0
                dmgInfo = CTakeDamageInfo(self, self, vecDir, e.GetAbsOrigin() , self.damage, DMG_BLAST)
                e.TakeDamage(dmgInfo)
                
            self.SetThink(self.SUB_Remove, gpGlobals.curtime + 2.0)
            
    velocity = FloatField(value=320.0, networked=True)
    modelname = None
    particleeffect = StringField(value='', networked=True, clientchangecallback='OnParticleEffectChanged')
    pexplosioneffect = None
    projtarget = GenericField(value=None, networked=True, clientchangecallback='OnParticleEffectChanged')
    damage = 0
    thinkfreq = 0.1
    dietime = None
    explodetolerance = 32.0
    