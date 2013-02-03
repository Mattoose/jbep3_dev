MUTATION.Title = "Shrink Deathmatch"
MUTATION.GameRules = "CJBGameRules_DM" -- Derive from our C++ gamerules DM class
MUTATION.Help = [[Kill other players, score points. Lower ranked players are smaller and harder to hit.]]

-- Set up team numbers, spawns...
local TEAM_PLAYERS			= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints[TEAM_PLAYERS] = {"jb_spawn_all"}

-- Register teams
function MUTATION:SetupTeams()
	teams.Register( TEAM_PLAYERS, "Players", Colour( 255, 50, 50 ) )	
end