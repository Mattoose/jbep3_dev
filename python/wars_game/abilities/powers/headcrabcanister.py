from vmath import Vector, QAngle, VectorNormalize
from core.abilities import AbilityTarget

if isserver:
    from entities import CreateEntityByName, DispatchSpawn, variant_t, g_EventQueue
    from core.units import CreateUnitNoSpawn
    
# Launches a headcrab canister
class AbilityCanister(AbilityTarget):
    name = "launch_headcrabcanister"

    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()

            # Create a launch spot
            spot = CreateEntityByName( "info_target" )
            spot.KeyValue("targetname", "spot" )
            spot.SetAbsOrigin(self.player.GetAbsOrigin() + Vector(512.0, 90.0, 712.0))
            spot.SetAbsAngles(QAngle( 60, 0, 0 ))
            DispatchSpawn(spot)
    
            # Create and setup the canister
            can = CreateUnitNoSpawn( "unit_headcrabcanister" )
            can.SetOwnerNumber(self.player.GetOwnerNumber())
            can.KeyValue("name", "head" )
            can.KeyValue( "HeadcrabType", "0")
            can.KeyValue( "HeadcrabCount", "6")
            can.KeyValue( "FlightSpeed", "512")
            can.KeyValue( "FlightTime", "1")
            can.KeyValue( "Damage" , "75" )
            can.KeyValue( "DamageRadius", "250" )
            can.KeyValue( "LaunchPositionName", "spot")
            can.SetAbsOrigin( data.endpos )
            can.SetAbsAngles(QAngle( -90, 0, 0 ))
            DispatchSpawn( can )      
            
            g_EventQueue.AddEvent( can, "FireCanister", variant_t(), 1.0, None, None, 0 )
            g_EventQueue.AddEvent( spot, "kill", variant_t(), 25.0, None, None, 0 )
    
            self.Completed()
        
    infoprojtextures = [{'texture' : 'decals/testeffect'}]
        