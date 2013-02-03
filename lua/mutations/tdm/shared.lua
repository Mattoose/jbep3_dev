MUTATION.Title = "Team Deathmatch"
MUTATION.GameRules = "CJBGameRules_TDM"
MUTATION.Help = [[Kill the other team.]]

TEAM_TDM_RED			= TEAM_SPECTATOR + 1
TEAM_TDM_BLUE			= TEAM_SPECTATOR + 2

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_TDM_RED] = {"jb_spawn_deathmatch_red"}
MUTATION.SpawnPoints[TEAM_TDM_BLUE] = {"jb_spawn_deathmatch_blue"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_TDM_RED, "Red", Colour( 255, 50, 50 ) )	
	teams.Register( TEAM_TDM_BLUE, "Blue", Colour( 150, 150, 255 ) )	
end