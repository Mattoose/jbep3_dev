
include("shared.lua")

function MUTATION:SVT_DefaultWeapons( pPlayer ) 

	if ( pPlayer:GetTeam() == TEAM_SNAKE ) then
	
		pPlayer:GiveNamedItem( "weapon_box" )		
		pPlayer:GiveNamedItem( "weapon_knife" )		
		pPlayer:GiveNamedItem( "weapon_ruger" )		
		pPlayer:GiveAmmo( 40, "ruger" )		
		pPlayer:GiveNamedItem( "weapon_handgun" )		
		pPlayer:GiveAmmo( 1000, "handgun" )		
		pPlayer:GiveNamedItem( "weapon_satchel" )
		pPlayer:GiveAmmo( 1, "satchel" )
		pPlayer:GiveAmmo( 1, "decoy" )
		
		pPlayer:GiveNamedItem( "weapon_chaff" )
		pPlayer:GiveNamedItem( "weapon_flashbang" )
		pPlayer:GiveNamedItem( "weapon_smokegrenade" )
		
	else
	
		pPlayer:GiveNamedItem( "weapon_crowbar" )		
		pPlayer:GiveNamedItem( "weapon_pistol" )		
		pPlayer:GiveNamedItem( "weapon_p90" )		
		pPlayer:GiveNamedItem( "weapon_tripmine" )
		pPlayer:GiveAmmo( 1, "tripmine" )
		
	end
	
end

function MUTATION:SVT_ExtraWeapons( pPlayer, fWeaponBalance, iTotalPlayers )

	-- Add armor for snake, reduce health for terrorists.
	-- Scale this off total players. 
	if ( pPlayer:GetTeam() == TEAM_SNAKE ) then	
	
		-- pPlayer:SetArmorValue( util.RemapValClamped( iTotalPlayers, 2, 24, 0, 100 ) ) -- At 2 players, 0 armor. At 24 players, 100 armor.	
		
	else	
	
		pPlayer:SetHealth( util.RemapValClamped( iTotalPlayers, 15, 29, 100, 65 ) ) -- At 15 players, 100 hp. At 29 players, 70 hp.
		
		-- Also remove the p90 if there's enough players
		if ( iTotalPlayers > 20 ) then		
			pPlayer:RemoveWeaponByClassname( "weapon_p90" )
			pPlayer:SelectNextBestWeapon()			
		end

		
	end
	
	-- Give out some extra weapons (and remove p90 from Ts) based on players.
	-- Scaled off a value between 0 and 1. (Used so that 1 snake v 12 terrorists will have more ammo than 2 snakes v 13 terrorists)
	if ( pPlayer:GetTeam() == TEAM_SNAKE ) then
	
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0, 0.8, 0, 2 ) ), "decoy" )
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0.5, 0.9, 0, 6 ) ) * 10 , "ruger" )
		
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0, 0.8, 0, 2 ) ), "chaffgrenades" )
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0, 0.8, 1, 3 ) ), "flashbangs" )
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0, 0.8, 0, 2 ) ), "smokegrenades" )
		
		if ( fWeaponBalance > 0.75 ) then		
			pPlayer:GiveAmmo( 1, "satchel" )
		end	
		
	else
	
		pPlayer:GiveAmmo( math.floor( util.RemapValClamped( fWeaponBalance, 0, 0.8, 1, 2 ) ) * 15 , "glock" )
		
	end
	
end


function MUTATION:SVT_MapSkin( sMap )
	--[[
	1 = Normal
	2 = Arctic Warfare
	3 = Jungle
	]]--

	if ( sMap == "cs_assault" ) then return 1 end
	if ( sMap == "cs_havana" ) then return 1 end
	if ( sMap == "cs_italy" ) then return 1 end
	if ( sMap == "cs_militia" ) then return 3 end
	if ( sMap == "cs_office" ) then return 2 end
	if ( sMap == "de_aztec" ) then return 3 end
	if ( sMap == "de_cbble" ) then return 1 end
	if ( sMap == "de_chateau" ) then return 1 end
	if ( sMap == "de_dust" ) then return 1 end
	if ( sMap == "de_dust2" ) then return 1 end
	if ( sMap == "de_inferno" ) then return 1 end
	if ( sMap == "de_nuke" ) then return 1 end
	if ( sMap == "de_piranesi" ) then return 3 end
	if ( sMap == "de_port" ) then return 1 end
	if ( sMap == "de_prodigy" ) then return 3 end
	if ( sMap == "de_tides" ) then return 3 end
	if ( sMap == "de_train" ) then return 1 end
	
	return 0;
end