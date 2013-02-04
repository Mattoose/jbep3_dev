from core.abilities import AbilityTarget

if isserver:
    from entities import CreateEntityByName, g_EventQueue, variant_t, DispatchSpawn

class AbilityExplode(AbilityTarget):
    name = "explode"

    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()
        
            bomb = CreateEntityByName( "env_explosion" ) 
            bomb.SetAbsOrigin( data.endpos )
            bomb.KeyValue( "iMagnitude", "100" )
            bomb.KeyValue( "DamageForce", "500" )
            bomb.KeyValue( "fireballsprite", "sprites/zerogxplode.spr" )
            bomb.KeyValue( "rendermode", "5" )
            DispatchSpawn( bomb )       
            bomb.Activate()    
            
            value = variant_t()
            g_EventQueue.AddEvent( bomb, "Explode", value, 0.5, None, None )
            g_EventQueue.AddEvent( bomb, "kill", value, 1.0, None, None )
            
            self.Completed()
        
    infoprojtextures = [{'texture' : 'decals/testeffect'}]