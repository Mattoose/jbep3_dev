
GM.currentState = nil
local states = {}
local transitionTime = 0

-- State Management
function GM:InState( stateName ) 
	local queryState = states[ stateName ]
	return queryState ~= nil and queryState == self.currentState
end

function GM:ChangeState( newState )
	-- If we're in an existing state, exit
	if self.currentState ~= nil and self.currentState.Leave ~= nil then 
		self.currentState:Leave() 
	end 

	-- Ensure we're not changing into an invalid state
	local incomingState = states[ newState ]
	if incomingState == nil then
		Warning( "Tried to change to unknown state "..newState )
		return
	end

	self.currentState = incomingState
	Msg( "Entered state "..newState )

	-- Fire Enter if it exists
	if incomingState.Enter ~= nil then
		incomingState:Enter()
	end
end

-- States
states.PreGame = {}
states.PreRound = {}
states.Round = {}
states.PostRound = {}
states.PostGame = {}