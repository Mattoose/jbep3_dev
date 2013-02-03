MUTATION.Title = "Scientist Survival (Working Title)"
MUTATION.GameRules = "CJBGameRules_Survival"
MUTATION.RoundBased = true
MUTATION.FriendlyFire = false
MUTATION.Help = [[Survive the onslaught of mad scientists.]]

local TEAM_PLAYERS		= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_PLAYERS] = {"jb_spawn_all","info_player_deathmatch"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_PLAYERS, 	"Players", 	Colour( 255, 50, 50 ) )	
end