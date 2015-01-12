local mutator = {}

mutator.Base = "default"
mutator.Name = "Slippy"
mutator.Description = "Zero friction"

function mutator:RoundStart()
	FindConVar( "sv_friction" ):SetValue( 0 )
end

function mutator:RoundEnd()
	FindConVar( "sv_friction" ):Revert()
end

mutators:Register( "slippy", mutator )

