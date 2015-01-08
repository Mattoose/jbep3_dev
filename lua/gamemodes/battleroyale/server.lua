include( "shared.lua" )
include( "states.lua" )
include( "mutator.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

for k, v in pairs( filesystem.FilesInDirectory( "lua/gamemodes/battleroyale/mutators" ) ) do
	include( "mutators/" .. v )
end

GM.ChosenKothArea = nil
GM.ActiveMutator = nil

function GM:Init()
	self:ChangeState( "PreGame" )
end

function GM:SelectDefaultTeam()
	return TEAM_PLAYERS
end

function GM:Think()
	-- Pass a think to our current state
	if self.currentState ~= nil and self.currentState.Think ~= nil then
		self.currentState:Think( self )
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

function GM:OverridePickupLifetime()
	return 600 -- Last for whole round
end

-- pick a mutator to use this round
function GM:SelectMutator()

	-- replace me with logic to pick a non-default mutator at random times
	self.ActiveMutator = mutators:Get( "default" )
	
	-- send intro text
	util.ChatPrintAll( self.ActiveMutator.Name )
	util.ChatPrintAll( self.ActiveMutator.Description )

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