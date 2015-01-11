local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeFingerBang_Title"
mutator.Description = "#JB_BR_RoundTypeFingerBang_Desc"

mutator.PlayerConditions = { JB_CONDITION_INFINITE_AMMO }
mutator.ItemPool = { "weapon_handgun" }

function mutator:ScaleHitboxDamage( pl, hitbox, info )

	-- Fists should do very low damage
	if( info:HasDamageType( DMG_CLUB ) ) then
		info:SetDamage( 1 )
		return true
	end

	return false
	
end


function mutator:OnPlayerCondition( pl, added, removed )
	
	-- Send people flying when they get handgunned
	if ( bit32.band( added, JB_CONDITION_HELDUP ) ~= 0 ) then
		pl:SetGroundEntity( nil ) 1
		pl:SetGravity( -1000 ) -- Todo, make this delayed with sounds indicating liftoff
		pl:SetAbsVelocity( Vector( 0, 0, 10000 ) )
	end

end

mutators:Register( "fingerbang", mutator )

