-- This mutator is only intended as a base and contains only weapons that fire bullets (useful for big head, high HP)

local mutator = {}

mutator.Base = "default"
mutator.IsBase = true

mutator.ItemPool = {
	"weapon_ax47",
	"weapon_beretta",
	"weapon_doublebarrel",
	"weapon_goldpistols",
	"weapon_mosin",
	"weapon_mp5k",
	"weapon_p90",
	"weapon_pistol",
	"weapon_railgun",
	"weapon_ruger",
	"weapon_saa",
	"weapon_shotgun",
	"weapon_tmp",
	"weapon_vintorez",
}

mutators:Register( "default_bullets", mutator )

