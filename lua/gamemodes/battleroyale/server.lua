include( "shared.lua" )
include( "states.lua" )
include( "mutator.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

-- Include mutator scripts
for k, v in pairs( filesystem.FilesInDirectory( "lua/gamemodes/battleroyale/mutators" ) ) do
	include( "mutators/" .. v )
end

-- Variables
GM.ChosenKothArea = nil
GM.ActiveMutator = nil
GM.StartTime = 0
GM.roundsSinceLastMutator = 0

local pending1v1 = {}
local next1v1Time = 0

function GM:Init()
	self:ChangeState( "PreGame" )
	self.StartTime = CurTime()
end

function GM:SelectDefaultTeam()
	return TEAM_PLAYERS
end

function GM:Think()
	-- Pass a think to our current state
	if self.currentState ~= nil and self.currentState.Think ~= nil then
		self.currentState:Think( self )
	end

	-- 1v1 speechlines
	if next1v1Time < CurTime() and #pending1v1 > 0 then
		next1v1Time = CurTime() + 3
		pending1v1[1]:SpeakConcept( JB_CONCEPT_BR_1V1 )
		table.remove( pending1v1, 1 )
	end
end

-- Only respawn in PreGame or PreRound
function GM:PlayerCanRespawn( pl )	
	return self:InState( "PreGame" ) or self:InState( "PreRound" )
end

-- Only give players items if they're in the pregame
function GM:PlayerDefaultItems( pl )
	if self:InState( "PreGame" ) then pl:GiveAllWeapons() end
end

-- Some mutators may force a certain set of player models
function GM:ForcePlayerModel( pl )

	if( self.ActiveMutator and self.ActiveMutator.PlayerModels and #self.ActiveMutator.PlayerModels > 0 ) then
		return self.ActiveMutator.PlayerModels[ #self.ActiveMutator.PlayerModels ]
	end
	
	return nil
	
end

function GM:OverridePickupLifetime()
	return 600 -- Last for whole round
end

function GM:ScaleHitboxDamage( pl, hitbox, info )
	
	-- check if the mutator wants to make any damage changes
	if( self:InState( "Round" ) and self.ActiveMutator ~= nil and self.ActiveMutator.ScaleHitboxDamage ~= nil ) then
		return self.ActiveMutator:ScaleHitboxDamage( pl, hitbox, info )
	end

	return false
	
end

function GM:PlayerDamageTaken( pl, info, health )

	-- see if mutator wants to do with the event of a player being damaged
	if( self:InState( "Round" ) and not pl:ValidPossess() and self.ActiveMutator ~= nil and self.ActiveMutator.PlayerDamageTaken ~= nil ) then
		self.ActiveMutator:PlayerDamageTaken( pl, info, health )
	end
	
end

function GM:PlayerKilled( pl, info )

	-- see if mutator wants to do with the event of a player dying
	if( self:InState( "Round" ) and not pl:ValidPossess() and self.ActiveMutator ~= nil and self.ActiveMutator.PlayerKilled ~= nil ) then
		self.ActiveMutator:PlayerKilled( pl, info )
	end

	-- Shout about kills
	local attacker = info:GetAttacker()
	local alivePlayers = self:AlivePlayers()
	local totalAlivePlayers = #alivePlayers
	if totalAlivePlayers > 2 and attacker:IsPlayer() then
		attacker:SpeakConceptDelayed( JB_CONCEPT_BR_KILL, 0.75 )
	elseif totalAlivePlayers == 2 then
		next1v1Time = CurTime() + 1
		for k, v in pairs( alivePlayers ) do
			table.insert( pending1v1, v )
		end
	end
end

-- pick a mutator to use this round
function GM:SelectMutator()

	-- Reset
	self.ActiveMutator = nil

	-- The chance for a mutator round goes up the more normal rounds we have in a row
	if ( math.random() <= math.Bias( math.min( 0.1 * self.roundsSinceLastMutator, 1 ), 0.35 ) ) then
		self.roundsSinceLastMutator = 0
		self.ActiveMutator = mutators:GetRandom()
	end
	
	-- We want to force a specific mutator
	if( self.Cvars.ForceMutator:GetString() ~= "" ) then
		self.ActiveMutator = mutators:Get( self.Cvars.ForceMutator:GetString() )
	end
	
	-- None selected, go to default mutator
	if( self.ActiveMutator == nil ) then
		self.ActiveMutator = mutators:Get( "default" )
		self.roundsSinceLastMutator = self.roundsSinceLastMutator + 1
	end
	
	-- send intro text
	util.ChatPrintAll( self.ActiveMutator.Name )
	util.ChatPrintAll( self.ActiveMutator.Description )

	-- Display intro
	if ( self.ActiveMutator ~= mutators:Get( "default" ) ) then
		temp.ShowRoundIntro( self.ActiveMutator.Name, self.ActiveMutator.Description )
	end

end

-- Player has won the round
function GM:PlayerWon( pl, inzone )

	-- Show the appropriate chat message
	if( inzone ) then
		util.ChatPrintAll( "#JB_BR_InZoneSingle", pl:GetPlayerName() )
	else
		util.ChatPrintAll( "#JB_BR_PlayerWon", pl:GetPlayerName() )
	end
	
	-- Increment score
	pl:IncrementScore( 1 )
	temp.BroadcastSound( 0, "JB.Stomped" )
	
	-- Call through to mutator to see if they want to do anything
	if( self.ActiveMutator and self.ActiveMutator.PlayerWon ~= nil ) then
		self.ActiveMutator:PlayerWon( pl )
	end

	-- Make them chatter
	pl:SpeakConceptDelayed( JB_CONCEPT_BR_WINNER, math.randomfloat( 1, 2 ) );
			
end

-- Misc
function GM:AlivePlayers()
	local alive = {}

	for k, v in pairs( player.GetAll() ) do
		-- Only count players on TEAM_PLAYERS and who aren't possessing as alive
		if v:IsAlive() and v:GetTeamNumber() == TEAM_PLAYERS and not v:ValidPossess() then
			table.insert( alive, v )
		end
	end

	return alive
end

function GM:FreezePlayers( bFreeze )
    for k, v in pairs( self:AlivePlayers() ) do
    	if bFreeze then
    		v:AddCondition( JB_CONDITION_FROZEN )
		else
    		v:RemoveCondition( JB_CONDITION_FROZEN )
		end
    end
end