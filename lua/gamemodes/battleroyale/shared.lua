GM.Name = "Battle Royale"
GM.Developer = "Team BBB"
GM.BaseGamemode = "base"

TEAM_PLAYERS = 2

-- ConVars
GM.Cvars = {}
GM.Cvars.ForceMutator = CreateConVar( "sv_br_forcemutator", "", FCVAR_NOTIFY + FCVAR_REPLICATED )
GM.Cvars.ForceWeapon = CreateConVar( "sv_br_forceweapon", "", FCVAR_NOTIFY + FCVAR_REPLICATED )
GM.Cvars.EnableMutators = CreateConVar( "sv_br_mutators_enabled", "1", FCVAR_NOTIFY + FCVAR_REPLICATED )
GM.Cvars.MutatorBias = CreateConVar( "sv_br_mutator_bias", "0.35", FCVAR_NOTIFY + FCVAR_REPLICATED )
GM.Cvars.RoundTimeMin = CreateConVar( "sv_br_roundtime_min", "60", FCVAR_NOTIFY + FCVAR_REPLICATED )
GM.Cvars.RoundTimeMax = CreateConVar( "sv_br_roundtime_max", "110", FCVAR_NOTIFY + FCVAR_REPLICATED )

function GM:InitTeams()
	team.Register( TEAM_PLAYERS, "Players", Color( 255, 60, 60 ) )
end