local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeInstaGhosts_Title"
mutator.Description = "#JB_BR_RoundTypeInstaGhosts_Desc"

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
