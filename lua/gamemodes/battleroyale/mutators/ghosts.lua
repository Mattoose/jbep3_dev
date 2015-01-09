local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeGhosts_Title"
mutator.Description = "#JB_BR_RoundTypeGhosts_Desc"

mutator.PlayerConditions = { JB_CONDITION_INVISIBLE }

mutators:Register( "ghosts", mutator )

function mutator:RoundStart()
	temp.ServerCommand( "jb_sv_fartsteps 1;" ) -- Temp until we fix convar setvalue
end

function mutator:RoundEnd()
	temp.ServerCommand( "jb_sv_fartsteps 0;" ) -- Temp until we fix convar setvalue
end