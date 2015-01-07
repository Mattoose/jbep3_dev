include( "shared.lua" )
include( "states.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

local itemPool = {
	"weapon_beretta",
	"weapon_pistol",
	"weapon_ruger",
	"weapon_saa",
	"weapon_goldpistols",
	"weapon_mp5k",
	"weapon_p90",
	"weapon_shotgun",
	"weapon_tmp",
	"weapon_ax47",
	"weapon_mosin" ,
	"weapon_vintorez",
	"weapon_railgun",
	"weapon_doublebarrel"
}

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

-- Misc

-- Round timer has elapsed or there's 1 player left alive
function GM:FindWinner()
	self:ChangeState( "PostRound" ) -- Change into post-round
	local alivePlayers = self:AlivePlayers()

	-- One player alive, they are the winner
	if #alivePlayers == 1 then
		local alivePlayer = alivePlayers[1]
		global.ChatPrintAll( "#JB_BR_PlayerWon", alivePlayer:GetPlayerName() )
		alivePlayer:IncrementScore( 1 )
		return
	end

	-- More than one person alive, everyone dies
	-- TODO: Only happens if there's no zones
	if #alivePlayers ~= 1 then 
		global.ChatPrintAll( "#JB_BR_NoWinner" )

		-- Kill players
		for k,v in pairs( alivePlayers ) do
			-- Todo, set suicide as bombcollar
			v:CommitSuicide( false, true )
		end

		return
	end

end

-- Distribute items to players
function GM:DistributeItems( pl )
	local randItem = itemPool[ math.random( #itemPool ) ]
	Msg( "Giving "..tostring(pl).." "..randItem.."\n" )
	pl:GiveNamedItem( randItem )
end