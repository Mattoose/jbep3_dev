local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeSpeed2_Title"
mutator.Description = "#JB_BR_RoundTypeSpeed2_Desc"

mutators:Register( "slow", mutator )

local nextSpeedUpdate = 0

function mutator:RoundStart()
	nextSpeedUpdate = CurTime() + 1
end

function mutator:Think()

	if( CurTime() >= nextSpeedUpdate ) then
	
		for _, v in ipairs( player.GetAll() ) do
		
			-- damage players who aren't moving
			if( v:GetHealth() > 1 ) then
				local damage = math.min( math.RemapValClamped( v:GetAbsVelocity():Length(), 120, 300, 0, 4 ), v:GetHealth() - 1 )
				
				if( damage > 0 ) then
					v:TakeDamage( CTakeDamageInfo( GetWorldEntity(), GetWorldEntity(), damage, DMG_CRUSH, JB_DMG_CUSTOM_BOMBCOLLAR ) )
				end
			end
			
		end
	
		nextSpeedUpdate = CurTime() + 1.0
	
	end

end
