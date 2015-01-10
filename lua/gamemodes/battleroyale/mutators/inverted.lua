local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeInverted_Title"
mutator.Description = "#JB_BR_RoundTypeInverted_Desc"

mutator.PlayerConditions = { JB_CONDITION_INVERTED }

mutators:Register( "inverted", mutator )

