GM.Name = "Battle Royale"
GM.Developer = "Team BBB"
GM.BaseGamemode = "base"

TEAM_SPECTATORS = 1
TEAM_PLAYERS = 2

function GM:InitTeams()
	team.Register( TEAM_PLAYERS, "Players", Color( 255, 60, 60 ) )
end