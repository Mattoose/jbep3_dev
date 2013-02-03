include("shared.lua")

function MUTATION:SelectDefaultTeam( pPlayer )
	return TEAM_PLAYERS	
end

function MUTATION:GiveDefaultItems( pPlayer ) 
	
	pPlayer:GiveNamedItem( "weapon_pistol" );
	pPlayer:GiveAmmo( 80, "glock" );
	pPlayer:GiveNamedItem( "weapon_mp5" );
	pPlayer:GiveAmmo( 30, "mp5" );
	pPlayer:GiveNamedItem( "weapon_crowbar" );
	
end