
if isserver:
    from vmath import Vector
    from srcbase import (DAMAGE_EVENTS_ONLY, DAMAGE_YES, COLLISION_GROUP_WEAPON, FSOLID_NOT_STANDABLE, SOLID_BBOX,
                         kRenderGlow, kRenderFxNoDissipation, kRenderTransAdd, kRenderFxNone, DMG_BLAST, DMG_BURN)
    from entities import entity, CBaseGrenade as BaseClass, CSoundEnt, SOUND_DANGER, CSprite, CSpriteTrail
    
    @entity('grenade_frag')
    class GrenadeFrag(BaseClass):
        def Spawn(self):
            self.Precache( )

            self.SetModel( self.GRENADE_MODEL )

            self.damage = self.DAMAGE
            self.damageradius = self.DMGRADIUS

            self.takedamage	= DAMAGE_YES
            self.health = 1

            self.SetSize( -Vector(4,4,4), Vector(4,4,4) )
            #self.SetCollisionGroup( COLLISION_GROUP_WEAPON )
            self.SetCollisionGroup( self.CalculateIgnoreOwnerCollisionGroup() )
            self.CreateVPhysics()

            self.BlipSound()
            self.nextbliptime = gpGlobals.curtime + self.FRAG_GRENADE_BLIP_FREQUENCY

            self.AddSolidFlags( FSOLID_NOT_STANDABLE )

            self.punted = False

            super(GrenadeFrag, self).Spawn()
        
        def CreateEffects(self):
            # Start up the eye glow
            self.mainglow = CSprite.SpriteCreate( "sprites/redglow1.vmt", self.GetLocalOrigin(), False )

            nAttachment = self.LookupAttachment( "fuse" )

            if self.mainglow != None:
                self.mainglow.FollowEntity( self )
                self.mainglow.SetAttachment( self, nAttachment )
                self.mainglow.SetTransparency( kRenderGlow, 255, 255, 255, 200, kRenderFxNoDissipation )
                self.mainglow.SetScale( 0.2 )
                self.mainglow.SetGlowProxySize( 4.0 )
                
            # Start up the eye trail
            self.glowtrail = CSpriteTrail.SpriteTrailCreate( "sprites/bluelaser1.vmt", self.GetLocalOrigin(), False )

            if self.glowtrail != None:
                self.glowtrail.FollowEntity( self )
                self.glowtrail.SetAttachment( self, nAttachment )
                self.glowtrail.SetTransparency( kRenderTransAdd, 255, 0, 0, 255, kRenderFxNone )
                self.glowtrail.SetStartWidth( 8.0 )
                self.glowtrail.SetEndWidth( 1.0 )
                self.glowtrail.SetLifeTime( 0.5 )

        def CreateVPhysics(self):
            # Create the object in the physics system
            self.VPhysicsInitNormal( SOLID_BBOX, 0, False )
            return True
            
        def Precache(self):
            self.PrecacheModel( self.GRENADE_MODEL )

            self.PrecacheScriptSound( "Grenade.Blip" )

            self.PrecacheModel( "sprites/redglow1.vmt" )
            self.PrecacheModel( "sprites/bluelaser1.vmt" )

            super(GrenadeFrag, self).Precache()
            
        def SetTimer(self, detonateDelay, warnDelay):
            self.detonatetime = gpGlobals.curtime + detonateDelay
            self.warnaitime = gpGlobals.curtime + warnDelay
            self.SetThink( self.DelayThink )
            self.SetNextThink( gpGlobals.curtime )

            self.CreateEffects()
            
        def DelayThink(self): 
            if gpGlobals.curtime > self.detonatetime:
                self.Detonate()
                return

            if not self.haswarnedai and gpGlobals.curtime >= self.warnaitime:
                #CSoundEnt.InsertSound(SOUND_DANGER, self.GetAbsOrigin(), 400, 1.5, self)
                
                self.haswarnedai = True
            
            if gpGlobals.curtime > self.nextbliptime:
                self.BlipSound()
                
                if self.haswarnedai:
                    self.nextbliptime = gpGlobals.curtime + self.FRAG_GRENADE_BLIP_FAST_FREQUENCY
                else:
                    self.nextbliptime = gpGlobals.curtime + self.FRAG_GRENADE_BLIP_FREQUENCY

            self.SetNextThink( gpGlobals.curtime + 0.1 )

        def SetVelocity(self, velocity, angVelocity):
            physobj = self.VPhysicsGetObject()
            if physobj != None:
                physobj.AddVelocity(velocity, angVelocity)

        def OnTakeDamage(self, inputInfo):
            # Manually apply vphysics because BaseCombatCharacter takedamage doesn't call back to CBaseEntity OnTakeDamage
            self.VPhysicsTakeDamage(inputInfo)

            # Grenades only suffer blast damage and burn damage.
            if not (inputInfo.GetDamageType() & (DMG_BLAST|DMG_BURN) ):
                return 0

            return super(GrenadeFrag, self).OnTakeDamage( inputInfo )
            
        def VPhysicsCollision(self, index, event):
            super(GrenadeFrag, self).VPhysicsCollision(index, event)
            
            physobj = self.VPhysicsGetObject()
            vel = Vector()
            ang = Vector()
            physobj.GetVelocity(vel, ang)
            vel.x = vel.y = 0.0
            physobj.SetVelocity(vel, ang)
            
        def BlipSound(self): self.EmitSound( "Grenade.Blip" )
        
        def InputSetTimer(self, inputdata):
            self.SetTimer(inputdata.value.Float(), inputdata.value.Float() - self.FRAG_GRENADE_WARN_TIME)

        @classmethod
        def Fraggrenade_Create(cls, position, angles, velocity, angVelocity, pOwner, timer):
            # Don't set the owner here, or the player can't interact with grenades he's thrown
            grenade = cls.Create( "grenade_frag", position, angles, pOwner)
            
            grenade.SetTimer( timer, timer - cls.FRAG_GRENADE_WARN_TIME )
            grenade.SetVelocity( velocity, angVelocity )
            grenade.SetThrower( pOwner )
            grenade.takedamage = DAMAGE_EVENTS_ONLY

            return grenade
            
        haswarnedai = False
        nextbliptime = 0.0
        
        GRENADE_MODEL = "models/Weapons/w_grenade.mdl"
        
        DAMAGE = 125.0
        DMGRADIUS = 250.0
    
        FRAG_GRENADE_BLIP_FREQUENCY = 1.0
        FRAG_GRENADE_BLIP_FAST_FREQUENCY = 0.3

        FRAG_GRENADE_GRACE_TIME_AFTER_PICKUP = 1.5
        FRAG_GRENADE_WARN_TIME = 1.5

        GRENADE_COEFFICIENT_OF_RESTITUTION = 0.2
    