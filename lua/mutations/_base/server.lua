--[[
You probably won't need to touch this...
]]--

include("shared.lua")

--
-- Initialize
-- Called on gamemode load.
--
function BASE:Initialize()
	con.Msg("------------------------------")
	con.Msg("Loaded mutation: "..MUTATION.Title)
	con.Msg("------------------------------")
end

--
-- LevelInitPostEntity
-- Called after entities are loaded
--
function BASE:LevelInitPostEntity() end

--
-- Think
-- Called each frame, don't do much in here, thanks.
--
function BASE:Think() end

--
-- CheckGameOver
-- Puts us into intermission before map change if we're over the timelimit.
-- This should be called when it's a good time to change the map. 
--
function BASE:CheckGameOver()
	local iTimeToChange = (GetConVar("mp_timelimit"):GetFloat()) * 60
	
	if ( iTimeToChange <= 0 ) then return false end -- 0 = no timelimit
		
	if ( not game.IsGameOver() and game.CurTime() > iTimeToChange ) then
		game.EndMultiplayerGame() -- Throw us to intermission.
		return true
	end
	
	return false
end

--
-- FinishClientPutInServer
--
function BASE:FinishClientPutInServer( pPlayer ) end

-- 
-- PlayerSpawn
--
function BASE:PlayerSpawn( pPlayer ) end

-- 
-- GiveDefaultItems
-- Called on each spawn, handles what weapons the players should get.
--
function BASE:GiveDefaultItems( pPlayer ) 
	pPlayer:GiveAllWeapons() 
end

--
-- PlayerDeath
-- Called on the death of a player.
--
function BASE:PlayerDeath( pVictim, pKiller, pInflictor ) end	

--
-- CanHavePlayerItem
-- Return a boolean, allows/denies the pickup of an item.
--
function BASE:CanHavePlayerItem( pPlayer, entItem ) end

-- 
-- SelectDefaultTeam
-- When the players join the game, place them on this returned team.
-- 
function BASE:SelectDefaultTeam() return TEAM_PLAYERS end -- They've hit join game, what team do we put them in?

--
-- GetGameDescription
-- What should we report to the server browser as our game name.
--
function BASE:GetGameDescription(  ) return "JBEP3: "..MUTATION.Title end

--
-- RoundCleanupShouldIgnore
-- Called for each entity being cleaned up
-- If true is returned, the entity will persist.
--
function BASE:RoundCleanupShouldIgnore( pEnt ) end

-- 
-- IPointsForKill
-- How many points to award to the attacker for killing the victim
--
function BASE:IPointsForKill( pAttacker, pVictim ) 
	if ( not pAttacker:IsPlayer() or not pVictim:IsPlayer() ) then return 0 end -- Nothing
	if ( MUTATION.FriendlyFire and pVictim:GetTeam() == pAttacker:GetTeam() ) then return -1 end -- -1 if it's a teammate when we are obeying ff rules
	return 1
end -- How many points are awarded to pAttacker for killing pVictim

--
-- SelectSpawnPoint
-- Spawn the player on the specified entity
--
local spawnHistory = {}
local possibleSpawns = {}
local checkedSpawns = false
function BASE:SelectSpawnPoint( pPlayer )

	-- Validate our spawns (only once)
	if ( not checkedSpawns ) then
	
		for iTeamIndex,tSpawnList in pairs( MUTATION.SpawnPoints ) do
		
			possibleSpawns[ iTeamIndex ] = {};
		
			for iSpawnKey,sSpawnName in pairs( tSpawnList ) do
				local tResults = ent.FindByClassname( sSpawnName )
				if ( #tResults > 0 ) then					
					con.Warning(" DEBUG: Spawn Setup - Found "..#tResults.." "..sSpawnName.." spawns.");
					for _,spawnEnt in pairs( tResults ) do
						table.insert( possibleSpawns[ iTeamIndex ], spawnEnt );
					end					
				end
			end	
		end		
		
	
		checkedSpawns = true
		
	end

	if ( not pPlayer or not pPlayer:IsPlayer() ) then return nil end
	
	local iTeam = pPlayer:GetTeam();
	
	local tTeamSpawns = possibleSpawns[ iTeam ]
	
	if ( #tTeamSpawns == 0 ) then
		con.Warning("Unable to find a valid spawn...");
		tTeamSpawns = ent.FindByClassname( "info_player_start" )
	
		if ( #tTeamSpawns == 0 ) then 		
			return nil 
		end 
	end
	
	local lastSpawnIndex = spawnHistory[ iTeam ] or 1
	
	local selectedSpawnEntity = tTeamSpawns[ lastSpawnIndex ]
	
	--con.Warning("Selecting spawn ".. lastSpawnIndex .." from ".. #tTeamSpawns .." possible spawns.");
	
	lastSpawnIndex = lastSpawnIndex + 1
	
	if ( lastSpawnIndex > #tTeamSpawns ) then lastSpawnIndex = 1 end -- Reached the end, loop back.
	
	spawnHistory[ iTeam ] = lastSpawnIndex
	
	return selectedSpawnEntity
	
end

function BASE:PlayerCanRespawn( pPlayer )
	return true
end