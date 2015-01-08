local mutator = {}

mutator.Name = "#JB_BR_Title"
mutator.Description = "#JB_BR_Description"

mutator.ItemPool = {
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

function mutator:GiveItems()

	-- start off with a full list
	local pool = {}
	
	for k, v in ipairs( self.ItemPool ) do
		pool[ k ] = v
	end

	for k, v in pairs( player.GetAll() ) do
		-- filter out any spectators
		if v:GetTeamNumber() == TEAM_PLAYERS then
			
			-- make sure we have items, we'll want to fill it up again if none are left
			if( #pool <= 0 ) then
				for k, v in ipairs( self.ItemPool ) do
					pool[ k ] = v
				end
			end
		
			-- pick a random item on the list
			local idx = math.random( #pool )
			local randItem = pool[ idx ]
			
			-- give it to the player
			local fists = v:GiveNamedItem( "weapon_fists" )
			local weapon = v:GiveNamedItem( randItem )	
			
			v:Weapon_Switch( weapon )
			v:Weapon_SetLast( fists )
			
			Msg( "Giving "..tostring(v).." ".. tostring(weapon) .. "\n" )
			
			-- remove this from the list so players get "unique" weapons
			table.remove( pool, idx )
			
		end
	end
	
end

function mutator:Think()

end

function mutator:PlayerWon( winningPlayer )

end

mutators:Register( "default", mutator )

