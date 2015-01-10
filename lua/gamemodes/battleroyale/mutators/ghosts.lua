local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeGhosts_Title"
mutator.Description = "#JB_BR_RoundTypeGhosts_Desc"

mutator.PlayerConditions = { JB_CONDITION_INVISIBLE }

mutators:Register( "ghosts", mutator )

function mutator:RoundStart()
	FindConVar( "jb_sv_fartsteps" ):SetValue( true )
end

function mutator:RoundEnd()
	FindConVar( "jb_sv_fartsteps" ):Revert()
end