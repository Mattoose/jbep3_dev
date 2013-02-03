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


function MUTATION:PlayerSpawn( pPlayer ) 

	local iOurScore = pPlayer:GetFrags();
	local iMinScore = iOurScore;
	local iMaxScore = iOurScore;
	
	for iIndex,pPlayer in pairs( teams.GetPlayers( TEAM_PLAYERS ) ) do
		
		local iThisScore = pPlayer:GetFrags();
		
		if ( iThisScore > iMaxScore ) then
			iMaxScore = iThisScore
		elseif ( iThisScore < iMinScore ) then
			iMinScore = iThisScore
		end	
		
	end	
	
	pPlayer:SetPlayerScale( util.RemapValClamped( iOurScore, iMinScore, iMaxScore, 0.4, 1.0 ) ) 
	
end