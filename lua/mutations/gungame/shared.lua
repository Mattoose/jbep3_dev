MUTATION.Title = "GunGame"
MUTATION.GameRules = "CJBGameRules_GunGame"
MUTATION.RoundBased = true
MUTATION.FriendlyFire = true
MUTATION.Help = [[In GunGame, you spawn with all weapons. Killing an enemy with a weapon will remove it from your inventory. 

The first player to run out of weapons wins.]]

local TEAM_PLAYER			= TEAM_SPECTATOR + 1

MUTATION.SpawnPoints = {}
MUTATION.SpawnPoints[TEAM_PLAYER] = {"jb_spawn_all","info_player_deathmatch"}

function MUTATION:SetupTeams()
	teams.Register( TEAM_PLAYER, 	"Players", 	Colour( 255, 50, 50 ) )	
end