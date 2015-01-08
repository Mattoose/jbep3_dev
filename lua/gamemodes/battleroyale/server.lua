include( "shared.lua" )
include( "states.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

GM.ChosenKothArea = nil
local itemPool = {
	"weapon_ax47",
	"weapon_beretta",
	"weapon_bofors",
	"weapon_box",
	"weapon_catmine",
	"weapon_displacer",
	"weapon_doublebarrel",
	"weapon_drilldo",
	"weapon_frictiongrenade",
	"weapon_goldpistols",
	"weapon_gravtripmine",
	"weapon_grenade",
	"weapon_handgun",
	"weapon_hornetgun",
	"weapon_knife",
	"weapon_meloncrossbow",
	"weapon_mosin",
	"weapon_mp5k",
	"weapon_p90",
	"weapon_pistol",
	"weapon_railgun",
	"weapon_ricochet",
	"weapon_rocketcrowbar",
	"weapon_rpg",
	"weapon_ruger",
	"weapon_saa",
	"weapon_satchel",
	"weapon_shotgun",
	"weapon_shotgun_scientist",
	"weapon_shuriken",
	"weapon_speakers",
	"weapon_tmp",
	"weapon_vintorez",
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

-- Distribute items to players
function GM:DistributeItems( pl )
	local randItem = itemPool[ math.random( #itemPool ) ]
	Msg( "Giving "..tostring(pl).." "..randItem.."\n" )
	pl:GiveNamedItem( randItem )
end