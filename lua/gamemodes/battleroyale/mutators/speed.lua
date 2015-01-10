local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeSpeed_Title"
mutator.Description = "#JB_BR_RoundTypeSpeed_Desc"

mutator.PlayerModels = { "models/player/hevsonic.mdl" }

mutator.Cvars = {}
mutator.Cvars.MinSpeed = CreateConVar( "sv_br_speed_minspeed", "1", FCVAR_NOTIFY )
mutator.Cvars.MaxSpeed = CreateConVar( "sv_br_speed_maxspeed", "3", FCVAR_NOTIFY )

mutators:Register( "speed", mutator )

local nextSpeedUpdate = 0

function mutator:RoundStart()
	nextSpeedUpdate = CurTime() + 1
end

function mutator:Think()

	if( CurTime() >= nextSpeedUpdate ) then
	
		local speedScale = math.RemapValClamped( game.GetRoundTimeLength(), GAMEMODE.TotalRoundLength, 0, self.Cvars.MinSpeed:GetFloat(), self.Cvars.MaxSpeed:GetFloat() )
		
		for _, v in ipairs( player.GetAll() ) do
		
			-- damage players who aren't moving
			if( v:GetHealth() > 1 ) then
				local damage = math.min( math.RemapValClamped( v:GetAbsVelocity():Length(), 0, 290, 10, 0 ), v:GetHealth() - 1 )
				
				if( damage > 0 ) then
					v:TakeDamage( CTakeDamageInfo( GetWorldEntity(), GetWorldEntity(), damage, DMG_CRUSH, JB_DMG_CUSTOM_BOMBCOLLAR ) )
				end
			end
		
			v:SetSpeedMod( speedScale )
			
		end
	
		nextSpeedUpdate = CurTime() + 1.0
	
	end

end
