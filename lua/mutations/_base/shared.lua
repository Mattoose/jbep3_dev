-- Title of the mutation, used in game description unless overridden
BASE.Title = "Base Mutation"
BASE.GameRules = "CJBGameRules"

BASE.Help = [[BASE MESSAGE]]

-- Custom teams start from TEAM_CUSTOM... or else.
TEAM_PLAYERS 	= 	TEAM_CUSTOM

-- Set up spawns for the teams.
BASE.SpawnPoints = {}
BASE.SpawnPoints[TEAM_PLAYERS] = {"jb_spawn_all"}

function BASE:SetupTeams()

	-- We don't need to set up spectator teams.
	teams.Register( TEAM_PLAYERS, "Players", Colour( 255, 50, 50 ) )
	
end

function BASE:PlayerRelationship( pPlayer)

end
