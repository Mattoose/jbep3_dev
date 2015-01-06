include( "shared.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

function GM:SelectDefaultTeam()
	if math.random(1,2) == 1 then
		return TEAM_RED
	else
		return TEAM_GREEN
	end
end