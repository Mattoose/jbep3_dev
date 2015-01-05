include( "shared.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

function GM:SelectDefaultTeam()
	return TEAM_PLAYERS
end