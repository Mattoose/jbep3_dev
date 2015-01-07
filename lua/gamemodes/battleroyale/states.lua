
GM.currentState = nil
local states = {}
local transitionTime = -1

-- State Management
function GM:InState( stateName ) 
	local queryState = states[ stateName ]
	return queryState ~= nil and queryState == self.currentState
end

function GM:ChangeState( newState )
	-- If we're in an existing state, exit
	if self.currentState ~= nil and self.currentState.Leave ~= nil then 
		self.currentState:Leave( self ) 
	end 

	-- Ensure we're not changing into an invalid state
	local incomingState = states[ newState ]
	if incomingState == nil then
		Warning( "Tried to change to unknown state "..newState.."\n" )
		return
	end

	self.currentState = incomingState
	Msg( "Entered state "..newState.."\n" )

	-- Fire Enter if it exists
	if incomingState.Enter ~= nil then
		incomingState:Enter( self )
	end
end

function GM:CanTransition() 
	if transitionTime < 0 then return false end
	return CurTime() > transitionTime
end

function GM:SetTransitionDelay( newTime ) 
	transitionTime = CurTime() + newTime
end

-- 
-- Pregame state
-- Server has < 2 active players
--
states.PreGame = {}
function states.PreGame:Enter( gm )
	temp.DestroyRoundTimer()
end

function states.PreGame:Think( gm )
	if gm:CountActivePlayers() >= 2 then
		gm:ChangeState( "PreRound" )
	end
end

--
-- Preround state
-- >= 2 active players, waiting a short time before entering main round
--
states.PreRound = {}
function states.PreRound:Enter( gm )
    temp.CleanUpMap() -- Reset the map
    gm:RespawnPlayers( true ) -- Respawn everyone
    gm:SetTransitionDelay( 5 )
end

function states.PreRound:Think( gm )
	-- If there's < 2 players, return to pregame.
	if gm:CountActivePlayers() < 2 then gm:ChangeState( "PreGame" ) end
	if gm:CanTransition() then gm:ChangeState( "Round" ) end
end

--
-- Round 
-- Players currently battling until timer expires or 1 player left alive
--
states.Round = {}
function states.Round:Enter( gm )
	global.ChatPrintAll( "Fight!" )
    gm:RespawnPlayers( false ) -- Respawn dead players
	temp.CreateRoundTimer( 60 )
	
	for k, v in pairs( gm:AlivePlayers() ) do
		if v:GetTeamNumber() == TEAM_PLAYERS then
			gm:DistributeItems( v )
		end
	end
end

function states.Round:Think( gm )
	local timeLeft = temp.GetRoundTimeLength()
	local alivePlayers = gm:AlivePlayers()
	local totalAlivePlayers = #alivePlayers

	if totalAlivePlayers <= 1 or timeLeft <= 0 then
		gm:FindWinner()
	end
end

function states.Round:Leave( gm )
	temp.DestroyRoundTimer()
end

-- 
-- PostRound
-- A player has won, waiting a short time before returning to PreRound
--
states.PostRound = {}
function states.PostRound:Enter( gm )
    gm:SetTransitionDelay( 5 )
end

function states.PostRound:Think( gm )
	if gm:CanTransition() then gm:ChangeState( "PreRound" ) end
	-- TODO: Timelimit expiry checks
end

-- 
-- PostGame
-- Time limit has been hit, freezing players, displaying scores and waiting
-- before changing to nextmap
--
states.PostGame = {}