
GM.currentState = nil
local states = {}
local transitionTime = -1

-- State Management
function GM:InState( stateName ) 
	local queryState = states[ stateName ]
	return queryState ~= nil and queryState == self.currentState
end

function GM:ChangeState( newState, ... )
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
		incomingState:Enter( self, ... )
	end
end

function GM:CanTransition() 
	if transitionTime < 0 then return false end
	return CurTime() > transitionTime
end

function GM:SetTransitionDelay( newTime ) 
	transitionTime = CurTime() + newTime
end

local function StopMusicEndRound( gm ) 
	gm:ChangeState( "PostRound" )
	game.BroadcastSound( 0, "AI_BaseNPC.SentenceStop" ) -- Stops sounds (replace me)
end

local function TimeLimitPassed( gm )

	local timeLimit = FindConVar( "mp_timelimit" ):GetFloat() * 60

	if( timeLimit <= 0 ) then
		return false
	end
	
	if( CurTime() - gm.StartTime >= timeLimit ) then
		return true
	end

	return false

end

-- 
-- Pregame state
-- Server has < 2 active players
--
states.PreGame = {}
function states.PreGame:Enter( gm )
	game.DestroyRoundTimer()
end

function states.PreGame:Think( gm )
	if gm:CountActivePlayers() >= 2 then
		gm:ChangeState( "WaitingForPlayers" )
	end
end

-- 
-- Waiting for players 
-- Waiting for additional players to join once we have the right amount
--
states.WaitingForPlayers = {}
function states.WaitingForPlayers:Enter( gm )
    gm:SetTransitionDelay( 30 )
    game.CreateRoundTimer( 30 )
end

function states.WaitingForPlayers:Think( gm )

	-- Players left while waiting
	if gm:CountActivePlayers() < 2 then
		gm:ChangeState( "PreGame" )
	end

	-- Time passed or developer is switched on
	if gm:CanTransition() or FindConVar( "developer" ):GetInt() >= 1 then
		gm.StartTime = CurTime()
		gm:ChangeState( "PreRound" )
	end

end

--
-- Preround state
-- >= 2 active players, waiting a short time before entering main round
--
states.PreRound = {}
function states.PreRound:Enter( gm )

	-- Check to see if the time limit has passed before starting the round
	if( TimeLimitPassed( gm ) ) then
		gm:ChangeState( "PostGame" )
		return nil
	end

    game.CleanUpMap() -- Reset the map
	
	gm:RespawnPlayers( true ) -- Respawn everyone
    gm:SetTransitionDelay( 5 )
    game.CreateRoundTimer( 5 )

    -- Pick snakes


    -- Freeze everyone briefly
    --gm:FreezePlayers( true )

end

function states.PreRound:Think( gm )
	-- If there's < 2 players, return to pregame.
	if gm:CountActivePlayers() < 2 then gm:ChangeState( "PreGame" ) end
	if gm:CanTransition() then gm:ChangeState( "Round" ) end
end

function states.PreRound:Leave( gm )
   	-- Ensure players are unfrozen
	--gm:FreezePlayers( false )
end

--
-- Round 
-- Players currently battling until timer expires or 1 player left alive
--
states.Round = {}
local nextBananaTimes = {}
function states.Round:Enter( gm )

	game.CreateRoundTimer( 30 )

	gm:RespawnPlayers( false )
	--gm:UnfreezePlayers()

	nextBananaTimes = {}

end

function states.Round:Think( gm )

	-- If snakes are all dead then monkeys win
	local snakes = player.GetTeam( TEAM_SNAKE )
	local snakeAliveCount = 0

	for _, v in pairs( snakes ) do
		if( v:IsAlive() ) then
			snakeAliveCount = snakeAliveCount + 1
		end
	end

	if( snakeAliveCount <= 0 ) then
		gm:ChangeState( "PostRound", TEAM_MONKEY )
	end

	-- Time limit means Snake has survived and won
	if( game.HasRoundTimeExpired() ) then
		gm:ChangeState( "PostRound", TEAM_SNAKE )
	end

	-- For each alive player, see if we want to emit a banane from a Snake
	for _, v in ipairs( player.GetAlive( TEAM_SNAKE ) ) do

		if( not nextBananaTimes[ v:EntIndex() ] or nextBananaTimes[ v:EntIndex() ] >= CurTime() ) then

			local force = v:GetAimVector()
			
			force.z = 0
			force = force:Normalize()

			force = force * 100
			force.z = 150

			util.TempEnt_Gib( "models/props/cs_italy/bananna.mdl", v:WorldSpaceCenter(), force, util.RandomAngularImpulse( -360, 360 ), 15 )
			nextBananaTimes[ v:EntIndex() ] = math.RemapValClamped( v:GetAbsVelocity():Length(), 0, 300, 2.0, 0.3 ) * math.random( 0.8, 1.2 )

		end

	end
	
end

function states.Round:Leave( gm )
	game.DestroyRoundTimer()
	nextBananaTimes = {}
end
-- 
-- PostRound
-- A player has won, waiting a short time before returning to PreRound
--
states.PostRound = {}
function states.PostRound:Enter( gm, winner )

	print("Team" .. winner .. " won\n")
	game.BroadcastSound( 0, "JB.MusicWin" .. winner )

	-- If snake won we'll want to increase the snake players' scores and give them a bonus for winning
	if( winner == TEAM_SNAKE ) then

		for _, v in ipairs( player.GetAll() ) do

			if( v:GetTeamNumber() == TEAM_SNAKE ) then			
				v:IncrementScore( 1 )
				v:SetHealth( 5000 )
			else
				v:SetSpeedMod( 0.3 )
			end

		end

	end

	game.DestroyRoundTimer()
    gm:SetTransitionDelay( 15 )

end

function states.PostRound:Think( gm )
	if gm:CanTransition() then gm:ChangeState( "PreRound" ) end
end

-- 
-- PostGame
-- Time limit has been hit, freezing players, displaying scores and waiting
-- before changing to nextmap
--
states.PostGame = {}

function states.PostGame:Enter( gm )
	game.GoToIntermission()
end