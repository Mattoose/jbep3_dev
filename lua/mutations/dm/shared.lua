MUTATION.Title = "Deathmatch"
MUTATION.GameRules = "CJBGameRules_DM"
MUTATION.Help = [[Kill other players, score points.]]

local TEAM_PLAYERS			= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_PLAYERS] = {"jb_spawn_all"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_PLAYERS, "Players", Colour( 255, 50, 50 ) )	
end