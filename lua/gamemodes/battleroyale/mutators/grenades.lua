local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeGrenades_Title"
mutator.Description = "#JB_BR_RoundTypeGrenades_Desc"

mutator.ItemPool = { "weapon_grenade" }
mutator.PlayerConditions = { JB_CONDITION_INFINITE_AMMO }

mutators:Register( "grenades", mutator )

