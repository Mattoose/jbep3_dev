local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeMelee_Title"
mutator.Description = "#JB_BR_RoundTypeMelee_Desc"

mutator.ItemPool = {
	"weapon_crowbar",
	"weapon_drilldo",
	"weapon_handgun"
}

mutators:Register( "melee", mutator )

