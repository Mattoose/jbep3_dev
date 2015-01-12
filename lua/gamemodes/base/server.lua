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

-- Called each server tick
function GM:Think()
end

-- Called when we want to precache any additional assets for this mode
function GM:Precache()

end

-- Called when querying if this spawn point is valid
function GM:IsSpawnPointValid( point, pl )
	return true
end

-- Called when a player spawns for the first time
function GM:PlayerInitialSpawn( pl )

end
	
-- A player has spawned
function GM:PlayerSpawn( pl )
end

-- Called when a player leaves
function GM:ClientDisconnected( pl )

end

-- Can a player respawn? Return true to allow, false to stay dead and go to spectator
function GM:PlayerCanRespawn( pl )
end

-- Called when a player on a valid team spawns
function GM:PlayerDefaultItems( pl )
	pl:GiveAllWeapons()
end

-- A player has been given a weapon
function GM:PlayerWeaponEquipped( pl, weap )

end

-- Return a model path here in order to force a model for a player
function GM:ForcePlayerModel( pl )
	return nil
end

-- Return the number of seconds weapon pickups should stay around for
function GM:OverridePickupLifetime()
	return -1
end

-- Return true here to stop the default hitbox scaling, use info:Scale/SetDamage to change damage dealt
function GM:ScaleHitboxDamage( pl, hitbox, info )
	return false
end

-- A player has taken damage
function GM:PlayerDamageTaken( pl, info, health )

end

-- A player has taken damage, this is called for damage that doesn't deal hitbox damage
function GM:GetDamageAdjustments( pl, info )

end

-- Player has died
function GM:PlayerKilled( pl, info )
	
end

-- Can we drop our weapons?
function GM:CanPlayerDropWeapons( pl, death )
	return true
end

-- Return false to disallow damage
function GM:AllowDamage( pl, info )
	return true
end

-- Conditions for a player have been modified
function GM:OnPlayerCondition( pl, added, removed )
end

-- Utility function to respawn players
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

-- Utility function to freeze players
function GM:FreezePlayers( bFreeze )
    for _, v in ipairs( player.GetAlive() ) do
    	if bFreeze then
    		v:AddCondition( JB_CONDITION_FROZEN )
		else
    		v:RemoveCondition( JB_CONDITION_FROZEN )
		end
    end
end