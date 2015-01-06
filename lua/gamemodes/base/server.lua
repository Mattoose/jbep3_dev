include( "shared.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

-- Assigned team when clicking join game
function GM:SelectDefaultTeam()
	if math.random(1,2) == 1 then
		return TEAM_RED
	else
		return TEAM_GREEN
	end
end

-- Text displayed in server browser tab
function GM:GetGameDescription()
	return GAMEMODE.Name
end

function GM:Think()
end
	