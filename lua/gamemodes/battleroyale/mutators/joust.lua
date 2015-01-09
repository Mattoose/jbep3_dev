local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeJousting_Title"
mutator.Description = "#JB_BR_RoundTypeJousting_Desc"

mutator.ItemPool = { }

function mutator:ScaleHitboxDamage( pl, hitbox, info )

	if( info:GetDamageCustom( JB_DMG_CUSTOM_DIVING ) ) then
		info:ScaleDamage( 50 )
		info:ScaleDamageForce( 150 )
		return true
	end

	return false
	
end

mutators:Register( "joust", mutator )

