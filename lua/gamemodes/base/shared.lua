GM.Name = "Base Gamemode"
GM.Developer = "Team BBB"

TEAM_SPECTATORS = 1
TEAM_RED = 2
TEAM_GREEN = 3

function GM:Init()
end

function GM:InitTeams()
	team.Register( TEAM_RED, "Red Players", Color( 255, 0, 0 ) )
	team.Register( TEAM_GREEN, "Green Players", Color( 0, 255, 0 ) )
end