GM.Name = "Battle Royale"
GM.Developer = "Team BBB"
GM.BaseGamemode = "base"

TEAM_PLAYERS = 2

-- ConVars
GM.Cvars = {}
GM.Cvars.ForceMutator = CreateConVar( "sv_br_forcemutator", "", FCVAR_NOTIFY + FCVAR_REPLICATED )

function GM:InitTeams()
	team.Register( TEAM_PLAYERS, "Players", Color( 255, 60, 60 ) )
end