include( "shared.lua" )
include( "states.lua" )

AddClientFile( "client.lua" )
AddClientFile( "shared.lua" )

GM.PlayedAsSnake = {}

function GM:Init()
	self:ChangeState( "PreGame" )
end

function GM:Precache()
	util.PrecacheScriptSound( "JB.SVMMusic" )
	util.PrecacheModel( "models/props/cs_italy/bananna.mdl" )
end

-- Assigned team when clicking join game
function GM:SelectDefaultTeam()
	return TEAM_MONKEY
end

function GM:Think()

	-- Pass a think to our current state
	if self.currentState ~= nil and self.currentState.Think ~= nil then
		self.currentState:Think( self )
	end

end

function GM:PlayerInitialSpawn( pl )

	-- clear the state that remembers if they've played as snake or not
	if( self.PlayedAsSnake[ pl:EntIndex() ] ) then
		table.remove( self.PlayedAsSnake, pl:EntIndex() )
	end

end

function GM:PlayerCanRespawn( pl )

	-- Monkeys get respawns
	if( pl:GetTeamNumber() == TEAM_MONKEY) then
		return not self:InState( "PostRound" )
	end

	return self:InState( "PreGame" ) or self:InState( "WaitingForPlayers" ) or self:InState( "PreRound" )

end

function GM:IsSpawnPointValid( point, pl )

	if( pl:GetTeamNumber() == TEAM_MONKEY ) then

		if( self:InState( "Round" ) ) then
			return ( point:GetClassname() == "jb_spawn_all" )
		else
			return ( point:GetClassname() == "jb_spawn_svt_terrorist" )
		end

	end

	return true

end

function GM:PlayerDefaultItems( pl )

	if( pl:GetTeamNumber() == TEAM_MONKEY ) then

		pl:GiveNamedItem( "weapon_fists" )

		pl:SetScale( self.Cvars.MonkeyScale:GetFloat() )
		pl:SetSpeedMod( math.RemapValClamped( self:CountActivePlayers(), 2, 20, self.Cvars.MaxMonkeySpeed:GetFloat(), self.Cvars.MinMonkeySpeed:GetFloat() ) )
		pl:SetHealth( self.Cvars.MonkeyHealth:GetInt() )

	else

		pl:GiveNamedItem( "weapon_knife" )
		pl:GiveNamedItem( "weapon_ruger" )
		pl:GiveNamedItem( "weapon_grenade" )
		pl:GiveNamedItem( "weapon_satchel" )
		pl:GiveNamedItem( "weapon_tripmine" )

		pl:GiveAmmo( 150, "ruger" )
		pl:GiveAmmo( 2, "grenades" )
		pl:GiveAmmo( 2, "satchel" )
		pl:GiveAmmo( 4, "tripmine" )

	end

	pl:AddCondition( JB_CONDITION_NODIVE )
	pl:AddCondition( JB_CONDITION_NO_HEALTH_RATIONS )

end

function GM:CanPlayerDropWeapons( pl, death )
	return false
end

function GM:ForcePlayerModel( pl )

	if( pl:GetTeamNumber() == TEAM_SNAKE ) then
		return "models/player/bigboss.mdl"
	end

	return "models/player/ape.mdl"

end

-- Return true here to stop the default hitbox scaling
function GM:PlayerDamageTaken( pl, info, health )

end

function GM:GetDamageAdjustments( pl, info )

end

function GM:PlayerKilled( pl, info )
	
end