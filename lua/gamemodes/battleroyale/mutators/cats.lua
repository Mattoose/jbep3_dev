local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeCat_Title"
mutator.Description = "#JB_BR_RoundTypeCat_Desc"

mutator.PlayerModels = { "models/player/dog.mdl" }

mutator.ItemPool = {
	"weapon_catmine",
}

mutators:Register( "cats", mutator )

