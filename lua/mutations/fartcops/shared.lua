MUTATION.Title = "Fart Cops"
MUTATION.GameRules = "CJBGameRules_FartCops"
MUTATION.RoundBased = false
MUTATION.FriendlyFire = true
MUTATION.Help = [[Farts only. Toot on your friends. BE THE FART COPS.]]

local TEAM_GREEN			= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_GREEN] = {"jb_spawn_all","info_player_deathmatch"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_GREEN, 	"Players", 	Colour( 11, 255, 11 ) )	
end