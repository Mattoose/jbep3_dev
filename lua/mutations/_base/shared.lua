BASE.Title = "Base Mutation"

TEAM_PLAYERS 	= 	FIRST_GAME_TEAM

-- Set up spawns for the teams.
BASE.SpawnPoints = {}
BASE.SpawnPoints[TEAM_PLAYERS] = {"jb_spawn_all"}

function BASE:SetupTeams()

	-- We don't need to set up spectator teams.
	teams.Register( TEAM_PLAYERS, "Players", Colour( 255, 50, 50 ) )
	
end
