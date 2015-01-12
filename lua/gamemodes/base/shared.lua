GM.Name = "Base Gamemode"
GM.Description = ""
GM.Developer = "Team BBB"

GM.TeamPlay = false
GM.SelectableTeams = false

TEAM_SPECTATORS = 1
TEAM_RED = 2
TEAM_GREEN = 3

function GM:Init()
end

-- Set up teams in here
function GM:InitTeams()
	team.Register( TEAM_RED, "Red Players", Color( 255, 0, 0 ) )
	team.Register( TEAM_GREEN, "Green Players", Color( 0, 255, 0 ) )
end

-- Relationship between Players
function GM:PlayerRelationship( player, target )
	return nil -- Default Source behaviour
end