local mutator = {}

local playersAtStart = 0
local playerKills = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeShrink_Title"
mutator.Description = "#JB_BR_RoundTypeShrink_Desc"

mutators:Register( "shrink", mutator )

function mutator:RoundStart()
	
	-- Store number of alive players
	playersAtStart = 0
	playerKills = {}

	for k, v in pairs( player.GetAll() ) do
		if v:IsAlive() and v:GetTeamNumber() == TEAM_PLAYERS and not v:ValidPossess() then
			playersAtStart = playersAtStart + 1
		end
	end

end

function mutator:PlayerKilled( pl, info )

	local attacker = info:GetAttacker()
	if attacker:IsPlayer() then

		local plIndex = attacker:EntIndex()
		if playerKills[ plIndex ] == nil then
			playerKills[ plIndex ] = 1
		else
			playerKills[ plIndex ] = playerKills[ plIndex ] + 1
		end

		attacker:SetScale( math.RemapValClamped( playerKills[ plIndex ], 0, ( playersAtStart - 1 ) * 0.4, 1, 0.25 ) )
	end
	
end