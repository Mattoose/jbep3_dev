MUTATION.Title = "Battle Royale"
MUTATION.GameRules = "CJBGameRules_BR"
MUTATION.RoundBased = true
MUTATION.FriendlyFire = false
MUTATION.Help = [[Kill your friends.]]

local TEAM_RED			= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_RED] = {"jb_spawn_all","info_player_deathmatch"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_RED, 	"Players", 	Colour( 255, 50, 50 ) )	
end