
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

local function StopMusicEndRound( gm ) 
	gm:ChangeState( "PostRound" )
	temp.BroadcastSound( 0, "AI_BaseNPC.SentenceStop" ) -- Stops sounds (replace me)
end

-- 
-- Waiting for players 
-- Just loaded, wait a little bit before playing
--
states.WaitingForPlayers = {}
function states.WaitingForPlayers:Enter( gm )
    gm:SetTransitionDelay( 45 )
end

function states.WaitingForPlayers:Think( gm )
	if gm:CanTransition() then gm:ChangeState( "PreGame" ) end

	-- If developer mode is on, skip...
	if FindConVar( "developer" ):GetInt() >= 1 then
		print( "Skipping waiting for players, developer mode enabled." )
		gm:ChangeState( "PreGame" )
	end
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
local unfreezeTime = -1
states.PreRound = {}
function states.PreRound:Enter( gm )
    temp.CleanUpMap() -- Reset the map
	
	gm:SelectMutator()
    gm:RespawnPlayers( true ) -- Respawn everyone
    gm:SetTransitionDelay( 5 )
    temp.CreateRoundTimer( 5 )

    -- Freeze everyone briefly
    unfreezeTime = CurTime() + 1.5
    gm:FreezePlayers( true )
end

function states.PreRound:Think( gm )
	-- If there's < 2 players, return to pregame.
	if gm:CountActivePlayers() < 2 then gm:ChangeState( "PreGame" ) end
	if gm:CanTransition() then gm:ChangeState( "Round" ) end

	-- Check for unfreeze
	if unfreezeTime < CurTime() and unfreezeTime > 0 then
    	gm:FreezePlayers( false )
    	unfreezeTime = -1
	end
end

function states.PreRound:Leave( gm )
   	-- Ensure players are unfrozen
	gm:FreezePlayers( false )
end

--
-- Round 
-- Players currently battling until timer expires or 1 player left alive
--
local nextBeepTime = 0
local iKothTimeBegin = 35
states.Round = {}
function states.Round:Enter( gm )
    gm:RespawnPlayers( false ) -- Respawn dead players
	gm.ChosenKothArea = nil
	
	gm.TotalRoundLength = math.RemapValClamped( #gm:AlivePlayers(), 2, 10, gm.Cvars.RoundTimeMin:GetFloat(), gm.Cvars.RoundTimeMax:GetFloat() )
	
	-- Mutators might want to have longer rounds, just add that
	if( gm.ActiveMutator.ExtraTime ~= nil ) then
		gm.TotalRoundLength = gm.TotalRoundLength + gm.ActiveMutator.ExtraTime
	
	temp.CreateRoundTimer( gm.TotalRoundLength )

	-- Round Music
	if ( gm.ActiveMutator ~= mutators:Get( "default" ) ) then
		temp.BroadcastSound( 0, "JB.BRMusic_SpecialRoundType" )
	else
		temp.BroadcastSound( 0, "JB.BRMusic_"..math.random( 2 ) )
	end
	
	gm.ActiveMutator:GiveItems()

	if( gm.ActiveMutator and gm.ActiveMutator.RoundStart ~= nil ) then
		gm.ActiveMutator:RoundStart()
	end
end

function states.Round:Think( gm )

	-- think in mutator
	if( gm.ActiveMutator and gm.ActiveMutator.Think ~= nil ) then
		gm.ActiveMutator:Think()
	end
	
	local timeLeft = temp.GetRoundTimeLength()
	local alivePlayers = gm:AlivePlayers()
	local totalAlivePlayers = #alivePlayers

	-- Check if we should enter KOTH mode
	local bCanEnterKothMode = totalAlivePlayers == 2 or timeLeft <= iKothTimeBegin

	if gm.ChosenKothArea == nil and bCanEnterKothMode then
		-- Choose an area
		local chosenArea = nil
		local potentialAreas = temp.GetKothAreas()
		if #potentialAreas > 0 then 
			chosenArea = potentialAreas[ math.random( #potentialAreas ) ]
		end

		if chosenArea ~= nil then
			gm.ChosenKothArea = chosenArea

			-- If we're above 35 sec, bring us down to that
			if timeLeft > iKothTimeBegin then
				temp.CreateRoundTimer( iKothTimeBegin )
			end

			-- Broadcast alarm
			temp.BroadcastSound( 0, "JB.BR_Alarm" );

			-- Chat message
			util.ChatPrintAll( "#JB_BR_GetToZone", ""..iKothTimeBegin, chosenArea:Name() )

			-- Highlight area
			chosenArea:CreateHighlight()
		end
	end

	-- Beep collars if we're getting to a zone
	if gm.ChosenKothArea ~= nil and CurTime() > nextBeepTime then
		nextBeepTime = CurTime() + math.RemapValClamped( timeLeft, iKothTimeBegin, 1, 3.5, 0.13 )

		for k,v in pairs( alivePlayers ) do
			v:EmitSound( "JB.Beep" )
		end
	end

	-- If we've hit timelimit and there's a koth zone, enter overtime
	if timeLeft <= 0 and gm.ChosenKothArea ~= nil then
		gm:ChangeState( "Overtime" ) 
		return
	end

	-- If one player remains, round is over now
	if totalAlivePlayers <= 1 or timeLeft <= 0 then
		StopMusicEndRound( gm )

		if totalAlivePlayers == 1 then -- alive player is the winner
			gm:PlayerWon( alivePlayers[1], false )
		else -- Kill everyone
			util.ChatPrintAll( "#JB_BR_NoWinner" )
			temp.BroadcastSound( 0, "weapon_pistol.Fart_Kill" )

			-- Kill players
			for k,v in pairs( alivePlayers ) do
				-- Todo, set suicide as bombcollar
				v:CommitSuicide( false, true )
			end
		end

		return
	end
	
end

function states.Round:Leave( gm )
	temp.DestroyRoundTimer()
end

--
-- Overtime 
-- > 1 player alive inside safe zone, instant kill any leavers, kill all at time limit
--
local bAnnouncedOvertime = false
states.Overtime = {}
function states.Overtime:Enter( gm )
	temp.CreateRoundTimer( 15 )
	bAnnouncedOvertime = false
end

function states.Overtime:Think( gm )

	-- think in mutator
	if( gm.ActiveMutator and gm.ActiveMutator.Think ~= nil ) then
		gm.ActiveMutator:Think()
	end
	
	local timeLeft = temp.GetRoundTimeLength()
	local alivePlayers = gm:AlivePlayers()
	local totalAlivePlayers = #alivePlayers

	-- Enumerate players in/out of koth zones
	local playersInKoth = {}
	local playersNotInKoth = {}
	if gm.ChosenKothArea ~= nil then
		for k, v in pairs( alivePlayers ) do
			if gm.ChosenKothArea:IsPlayerInBounds( v ) then
				table.insert( playersInKoth, v )
			else
				table.insert( playersNotInKoth, v )
			end
		end
	end

	-- Kill anyone outside of the zone
	for k, v in pairs( playersNotInKoth ) do
		v:CommitSuicide( false, true )
	end

	-- Update alive player count & table
	alivePlayers = gm:AlivePlayers()
	totalAlivePlayers = #alivePlayers

	-- If one single player stands, they are the winner
	if totalAlivePlayers == 1 then
		gm:PlayerWon( alivePlayers[1], true )
		StopMusicEndRound( gm )
		return
	end

	-- Nobody inside the zone = nobody wins
	if totalAlivePlayers == 0 then -- alive player is the winner
		util.ChatPrintAll( "#JB_BR_NoWinnerInZone" )
		StopMusicEndRound( gm )
		return
	end

	-- If the timelimit has reached, everyone dies.
	if timeLeft <= 0 then
		StopMusicEndRound( gm )

		util.ChatPrintAll( "#JB_BR_InZoneMultipleDies" )

		-- Kill players
		for k,v in pairs( alivePlayers ) do
			-- Todo, set suicide as bombcollar
			v:CommitSuicide( false, true )
		end
		return
	end

	-- Don't announce overtime until here, stops us shouting overtime when 
	-- it's an instant victory
	if not bAnnouncedOvertime then
		util.ChatPrintAll( "#JB_BR_Overtime" )
		temp.BroadcastSound( 0, "JB.BR_Overtime" )
		bAnnouncedOvertime = true
	end
	
end

function states.Overtime:Leave( gm )
	temp.DestroyRoundTimer()
end

-- 
-- PostRound
-- A player has won, waiting a short time before returning to PreRound
--
states.PostRound = {}
function states.PostRound:Enter( gm )
	if( gm.ActiveMutator and gm.ActiveMutator.RoundEnd ~= nil ) then
		gm.ActiveMutator:RoundEnd()
	end

    gm:SetTransitionDelay( 12 )
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