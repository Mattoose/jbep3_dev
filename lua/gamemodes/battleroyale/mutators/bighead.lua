local mutator = {}

mutator.Base = "default_bullets"
mutator.Name = "#JB_BR_RoundTypeBigHead_Title"
mutator.Description = "#JB_BR_RoundTypeBigHead_Desc"

function mutator:OnWeaponAssigned( pl, weap )
	pl:SetHeadScale( 4.5 )
end

mutators:Register( "bighead", mutator )

