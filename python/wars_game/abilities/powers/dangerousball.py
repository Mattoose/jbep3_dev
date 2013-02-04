from srcbase import *
from vmath import *
import random
from core.abilities import AbilityMouseOverride
from entities import entity

if isserver:
    from entities import CreateEntityByName, DispatchSpawn, CBaseAnimating as BaseClass
    from entities import FOWFLAG_UNITS_MASK, CTakeDamageInfo
    import utils
    from particles import PrecacheParticleSystem, DispatchParticleEffect, ParticleAttachment_t
else:
    from entities import C_BaseAnimating as BaseClass

@entity('dangerousball', networked=True)
class DangerousBall(BaseClass):
    def ShouldDraw(self):
        return False    # Don't draw our model (we only use it for the physics)
        
    # The following methods are only implemented on the server
    if isserver:
        def __init__(self):
            super(DangerousBall, self).__init__()
        
            # This entity updates the fog of war 
            self.viewdistance = 1024.0
            self.AddFOWFlags(FOWFLAG_UNITS_MASK)
                
        def Precache(self):
            super(DangerousBall, self).Precache()
        
            # Preache our model (containing the physic model) and the particle system
            self.PrecacheModel( self.DANGEROUSBALL_MODEL )  
            PrecacheParticleSystem(self.PARTICLES_NAME)

        def Spawn(self):
            self.Precache()
            
            # point sized, solid, bouncing
            self.SetCollisionGroup( Collision_Group_t.COLLISION_GROUP_PROJECTILE )
            self.SetModel( self.DANGEROUSBALL_MODEL )
            self.SetMoveType( MoveType_t.MOVETYPE_VPHYSICS )
            self.SetSolidFlags( FSOLID_TRIGGER )
            self.SetTouch( self.DissolveTouch )   
            self.AddEFlags( EF_NOSHADOW )
           
            # Init physics
            physicsObject = self.VPhysicsInitNormal( SolidType_t.SOLID_VPHYSICS, self.GetSolidFlags(), False )
            vecAbsVelocity = self.GetAbsVelocity()
            physicsObject.AddVelocity( vecAbsVelocity, None )
            
            # Make some particles follow us
            DispatchParticleEffect(self.PARTICLES_NAME, ParticleAttachment_t.PATTACH_ABSORIGIN_FOLLOW, self)
            
        def DissolveTouch(self, touchent):
            """ Kill everything we touch """
            info = CTakeDamageInfo(None, None, 99999, DMG_DISSOLVE)
            touchent.TakeDamage(info)
            
        def VPhysicsCollision(self, index, event):
            """ If we hit something, bump up """
            super(DangerousBall, self).VPhysicsCollision( index, event )
            
            self.VPhysicsGetObject().AddVelocity( Vector(0,0,1) * 200.0, None ) 
            
    DANGEROUSBALL_MODEL = "models/combine_helicopter/helicopter_bomb01.mdl"
    PARTICLES_NAME = "dangerousball"

# Spawns a dangerous ball
class AbilityDangerousBall(AbilityMouseOverride):
    # Info
    name = "dangerousball"
    description = "A dangerous ball"
    
    # Ability
    if isserver:
        @classmethod           
        def Precache(info):
            super(AbilityDangerousBall, info).Precache()
            
            PrecacheParticleSystem(DangerousBall.PARTICLES_NAME)
        
        def Init(self):
            super(AbilityDangerousBall, self).Init()

            # Spawn the ball from the player origin in the direction the mouse is pointing
            data = self.player.GetMouseData()
            vecShootDir = data.endpos - self.player.GetAbsOrigin()
            VectorNormalize( vecShootDir )
            ball = CreateEntityByName( "dangerousball" )
            if not ball:
                self.Completed()
                return
            ball.SetAbsOrigin( self.player.GetAbsOrigin() )
            ball.SetAbsVelocity( vecShootDir * 10000.0 )
            ball.SetOwnerNumber(self.player.GetOwnerNumber())
            DispatchSpawn( ball )      
            self.ball = ball.GetHandle()  
        
        def Cleanup(self):
            super(AbilityDangerousBall, self).Cleanup()
            
            # Remove the ball
            if self.ball:
                self.ball.Remove()
                
        lastmousesample = None
        ticksignal = 0.1
        def Tick(self):
            # Clear this ability in case the ball entity got killed for some reason
            if not self.ball:
                self.Completed()
                return
                
            if self.player.IsLeftPressed():
                if self.lastmousesample:
                    # Add velocity in the direction the mouse is being dragged
                    # Moving faster will add more velocity
                    data = self.player.GetMouseData()
                    dir = data.endpos - self.lastmousesample.endpos
                    dist = VectorNormalize( dir )
                    dir.z = 0.0
                    self.ball.VPhysicsGetObject().AddVelocity(dir * dist * 1.5, None) 
                    
                    # If additionally right is pressed an upward velocity is added to the ball
                    if self.player.IsRightPressed():
                        self.ball.VPhysicsGetObject().AddVelocity(Vector(0,0,1) * 100.0, None) 
                    
                # Store mouse sample for the next update
                self.lastmousesample = self.player.GetMouseData() 
            
        def OnLeftMouseButtonReleased(self):
            """ Clear current mouse sample """
            self.lastmousesample = None
            return True
            
        def OnRightMouseButtonPressed(self): 
            """ Clear this ability when right is pressed """
            if self.player.IsLeftPressed():
                return True
            self.Completed()
            return True
            
    allowmulitpleability = True
