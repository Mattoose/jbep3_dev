include( "shared.lua" )
include( "states.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

function GM:Init()
	self:ChangeState( "PreGame" )
end

function GM:SelectDefaultTeam()
	return TEAM_PLAYERS
end

function GM:Think()
	-- Pass a think to our current state
	if self.currentState ~= nil and self.currentState.Think ~= nil then
		currentState:Think()
	end
end