local mutator = {}

mutator.Base = "default_bullets"
mutator.Name = "#JB_BR_RoundTypeHP_Title"
mutator.Description = "#JB_BR_RoundTypeHP_Desc"

mutator.PlayerConditions = { JB_CONDITION_INFINITE_AMMO }

function mutator:OnWeaponAssigned( pl, weap )
	pl:SetHealth( 500 )
end

mutators:Register( "highhp", mutator )

