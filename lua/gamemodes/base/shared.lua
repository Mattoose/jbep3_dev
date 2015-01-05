GM.Name = "Base Gamemode"
GM.Developer = "Team BBB"

TEAM_SPECTATORS = 1
TEAM_PLAYERS = 2

function GM:Init()
end

function GM:InitTeams()
	team.Register( TEAM_PLAYERS, "Players" )
end