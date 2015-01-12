local mutator = {}

mutator.Base = "default"
mutator.Name = "Brittle Bones"
mutator.Description = "Extreme wall/ceiling impact damage."
--mutator.PlayerModels = { "models/player/skeleton/skeleton.mdl" } -- Re-enable when we can use skeleton model

function mutator:RoundStart()
	FindConVar( "jb_sv_impact_wallspeed" ):SetValue( 64 )
	FindConVar( "jb_sv_impact_ceilspeed" ):SetValue( 30 )
	FindConVar( "jb_sv_impact_damage" ):SetValue( 500 )
end

function mutator:RoundEnd()
	FindConVar( "jb_sv_impact_wallspeed" ):Revert()
	FindConVar( "jb_sv_impact_ceilspeed" ):Revert()
	FindConVar( "jb_sv_impact_damage" ):Revert()
end

mutators:Register( "brittlebones", mutator )

