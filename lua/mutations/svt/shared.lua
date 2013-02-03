MUTATION.Title = "Snake Vs Terrorists"
MUTATION.GameRules = "CJBGameRules_SVT"
MUTATION.RoundBased = true
MUTATION.FriendlyFire = false
MUTATION.Help = [[As snake, either kill all terrorists or capture the kerotan frogs, marked on your hud.

As a terrorist, either eliminate snake or stop him from reaching the kerotan frogs.]]

TEAM_SNAKE			= TEAM_SPECTATOR + 1
TEAM_TERRORIST		= TEAM_SPECTATOR + 2

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_SNAKE] = {"jb_spawn_svt_snake"}
MUTATION.SpawnPoints[TEAM_TERRORIST] = {"jb_spawn_svt_terrorist"}


function MUTATION:SetupTeams()

	teams.Register( TEAM_SNAKE, 		"Snake", 		Colour( 185, 220, 255 ) )
	teams.Register( TEAM_TERRORIST, 	"Terrorists", 	Colour( 255, 50, 50 ) )
	
end