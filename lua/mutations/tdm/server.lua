include("shared.lua")

function MUTATION:SelectDefaultTeam( pPlayer )
	
	-- Put the player on the team with the fewest players!
	
	local red_team = teams.GetPlayers( TEAM_TDM_RED );
	local blue_team = teams.GetPlayers( TEAM_TDM_BLUE );
	
	con.ColMsg( Color( 0, 255, 0 ), "Red Team: "..#red_team );
	con.ColMsg( Color( 0, 255, 0 ), "Blue Team: "..#blue_team );
	
	if ( #red_team > #blue_team ) then
		return TEAM_TDM_BLUE
	elseif ( #red_team < #blue_team ) then
		return TEAM_TDM_RED
	else
		return TEAM_TDM_RED	
	end
	
end

function MUTATION:GiveDefaultItems( pPlayer ) 
	
	pPlayer:GiveNamedItem( "weapon_pistol" );
	pPlayer:GiveAmmo( 80, "glock" );
	pPlayer:GiveNamedItem( "weapon_mp5" );
	pPlayer:GiveAmmo( 30, "mp5" );
	pPlayer:GiveNamedItem( "weapon_crowbar" );
	
end