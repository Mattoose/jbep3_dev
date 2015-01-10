local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeFoodFight_Title"
mutator.Description = "#JB_BR_RoundTypeFoodFight_Desc"

mutator.ItemPool = { "weapon_meloncrossbow_foodfight" }

mutators:Register( "foodfight", mutator )

function mutator:OnWeaponAssigned( pl, weap )
	if( weap ) then
		weap:AddCondition( JB_WEAPON_CONDITION_INFINITE_MAGAZINE )
	end
end

function mutator:ScaleHitboxDamage( pl, hitbox, info )

	if info:HasDamageType( DMG_MELON ) then
		info:SetDamage( 15 )
		return true
	end
	
	return false
	
end