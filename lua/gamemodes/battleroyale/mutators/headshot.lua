local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeHeadshot_Title"
mutator.Description = "#JB_BR_RoundTypeHeadshot_Desc"

mutator.PlayerConditions = { JB_CONDITION_INFINITE_MAGAZINE, JB_CONDITION_AUTOSTAND }
mutator.ItemPool = { "weapon_saa" }

mutators:Register( "headshot", mutator )

local nextHeadUpdate = 0

function mutator:RoundStart()
	nextHeadUpdate = 0
end

function mutator:ScaleHitboxDamage( pl, hitbox, info )

	if( hitbox == HITGROUP_HEAD ) then
		info:ScaleDamage( 69 )
		return true
	end

	info:SetDamage( 0 )
	return true
	
end

function mutator:Think()

	if( CurTime() >= nextHeadUpdate ) then
	
		local headScale = math.RemapValClamped( game.GetRoundTimeLength(), GAMEMODE.TotalRoundLength, 0, 0.01, 4 )
		
		for _, v in ipairs( player.GetAll() ) do
		
			-- damage players who have trapped themselves in prone
			if( v:IsDiving() and v:GetGroundEntity() and CurTime() >= v:GetNextDiveTime() + 2 ) then
				v:TakeDamage( CTakeDamageInfo( GetWorldEntity(), GetWorldEntity(), 2, DMG_CRUSH, JB_DMG_CUSTOM_BOMBCOLLAR ) )
			end
		
			v:SetHeadScale( headScale )
			
		end
	
		nextHeadUpdate = CurTime() + 0.5
	
	end

end
