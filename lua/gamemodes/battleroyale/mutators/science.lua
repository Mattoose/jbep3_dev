local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeScience_Title"
mutator.Description = "#JB_BR_RoundTypeScience_Desc"

mutator.ItemPool = { "weapon_shotgun_scientist" }
mutator.PlayerModels = { "models/player/bms_scientist.mdl" }

mutators:Register( "science", mutator )

