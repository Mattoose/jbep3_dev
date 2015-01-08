local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeFart_Title"
mutator.Description = "#JB_BR_RoundTypeFart_Desc"

mutator.ItemPool = { "weapon_pistol" }
mutator.PlayerConditions = { JB_CONDITION_FARTONLY }

mutators:Register( "farts", mutator )

