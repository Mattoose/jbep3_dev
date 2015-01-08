include( "shared.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

-- Assigned team when clicking join game
function GM:SelectDefaultTeam()
	if math.random(1,2) == 1 then
		return TEAM_RED
	else
		return TEAM_GREEN
	end
end

-- Text displayed in server browser tab
function GM:GetGameDescription()
	return GAMEMODE.Name
end

function GM:Think()
end
	
function GM:PlayerSpawn( pl )
end

function GM:PlayerCanRespawn( pl )
end

function GM:PlayerDefaultItems( pl )
	pl:GiveAllWeapons()
end

function GM:OverridePickupLifetime()
	return -1
end

-- Misc 

function GM:RespawnPlayers( bForceRespawn, iTeamFilter )
	-- Iterate all players, respawning
	for k, v in pairs( player.GetAll() ) do
		-- Only respawn players on the given team (if we gave a team)
		if iTeamFilter == nil or iTeamFilter == v:GetTeamNumber() then
			-- Only respawn if they are not alive (or if we force)
			if bForceRespawn or not v:IsAlive() then
				v:ForceRespawn()
			end
		end
	end
end

-- Returns table containing all the currently living players
function GM:AlivePlayers()
	local alive = {}

	for k, v in pairs( player.GetAll() ) do
		if v:IsAlive() and v:GetTeamNumber() == TEAM_PLAYERS then
			table.insert( alive, v )
		end
	end

	return alive
end

-- Returns total number of players on a non-spectator team
function GM:CountActivePlayers()
	local total = 0

	for k, v in pairs( player.GetAll() ) do
		if v:GetTeamNumber() > TEAM_SPECTATORS then
			total = total + 1
		end
	end

	return total
end