local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeDuckHunt_Title"
mutator.Description = "#JB_BR_RoundTypeDuckHunt_Desc"

mutator.ItemPool = { "weapon_doublebarrel" }
mutator.PlayerConditions = { JB_CONDITION_INFINITE_AMMO }

function mutator:ScaleHitboxDamage( pl, hitbox, info )

	if( info:HasDamageType( DMG_CLUB ) or pl:GetGroundEntity() ~= nil ) then
		info:SetDamage( 0.0 )
		return true
	end

	return false
	
end

mutators:Register( "duckhunt", mutator )

