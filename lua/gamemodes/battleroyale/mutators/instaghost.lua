local mutator = {}

mutator.Base = "default"
mutator.Name = "InstaGhosts"
mutator.Description = "Invisible players, fartsteps and instagib weapons"

mutator.PlayerConditions = { JB_CONDITION_INVISIBLE, JB_CONDITION_AUTOSTAND }

mutator.ItemPool = {
	"weapon_handgun_insta",
	"weapon_goldengun",
	"weapon_railgun_insta",
	"weapon_neszapper",
}

function mutator:RoundStart()
	FindConVar( "jb_sv_fartsteps" ):SetValue( true )
end

function mutator:RoundEnd()
	FindConVar( "jb_sv_fartsteps" ):Revert()
end

mutators:Register( "instaghosts", mutator )
