local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeSniper_Title"
mutator.Description = "#JB_BR_RoundTypeSniper_Desc"

mutator.ItemPool = {
	"weapon_knife",
	"weapon_mosin",
	"weapon_vintorez",
}

mutators:Register( "snipers", mutator )

