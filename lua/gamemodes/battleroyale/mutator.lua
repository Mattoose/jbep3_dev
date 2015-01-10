mutators = {}
mutators.mutators = {}

-- Register mutator by name
function mutators:Register( name, tbl )
	
	if( self.mutators[ name ] ~= nil ) then
		print( "Trying to register already existing mutator " .. name .. "\n" )
		return
	end
	
	-- Inherit table values from base
	if( tbl.Base ~= nil ) then
		tbl.BaseClass = self:Get( tbl.Base )
		
		-- Valid base mutator
		if( tbl.BaseClass ~= nil ) then
			-- Copy stuff from base if not overridden
			for k, v in pairs( tbl.BaseClass ) do
				if( tbl[k] == nil ) then
					if k == "IsBase" then -- Change IsBase value to false
						tbl[k] = false
					else
						tbl[k] = v
					end
				end
			end
		end
	end
	
	-- give some default values if they don't exist
	if( tbl.Name == nil ) then
		tbl.Name = name
	end
	
	-- default description
	if( tbl.Description == nil ) then
		tbl.Description = "GIVE " .. name .. " A DESCRIPTION!"
	end
	
	-- insert into table
	self.mutators[ name ] = tbl
	print( "Registered mutator " .. name .. "\n" )
	
end

-- Get mutator table by name
function mutators:Get( name )
	return self.mutators[ name ]
end

-- Number of registered mutators
function mutators:Count()
	return #self.mutators
end

-- Returns a random mutator EXCEPT default
function mutators:GetRandom()

	local mutnames = {}
	
	for k, v in pairs( self.mutators ) do
		if k ~= "default" and v.IsBase ~= true then -- exclude default
			table.insert( mutnames, v )
		end
	end
	
	return mutnames[ math.random( #mutnames ) ]

end

-- Default mutator
local mutator = {}

mutator.IsBase = false
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

mutator.PlayerModels = {}
mutator.PlayerConditions = {}

mutator.Cvars = {}

function mutator:GiveItems()

	-- start off with a full list
	local pool = {}
	
	for k, v in ipairs( self.ItemPool ) do
		pool[ k ] = v
	end

	for k, v in pairs( player.GetAll() ) do
		-- filter out any spectators
		if v:GetTeamNumber() == TEAM_PLAYERS then
			
			local weapon = nil
			
			if( GAMEMODE.Cvars.ForceWeapon:GetString() ~= "" ) then
			
				-- weapon is forced, just give that one
				local fists = v:GiveNamedItem( "weapon_fists" )
				weapon = v:GiveNamedItem( GAMEMODE.Cvars.ForceWeapon:GetString() )	
				
				v:Weapon_Switch( weapon )
				v:Weapon_SetLast( fists )				
				
			else
			
				-- make sure we have items, we'll want to fill it up again if none are left
				if( #self.ItemPool > 0 and #pool <= 0 ) then
					for k, v in ipairs( self.ItemPool ) do
						pool[ k ] = v
					end
				end
			
				-- Some mutators (eg jousting) may not give any weapons
				if( #pool > 0 ) then
				
					-- pick a random item on the list
					local idx = math.random( #pool )
					local randItem = pool[ idx ]
					
					-- give it to the player
					local fists = v:GiveNamedItem( "weapon_fists" )
					weapon = v:GiveNamedItem( randItem )	
					
					Msg( "Giving "..tostring(v).." ".. tostring(weapon) .. "\n" )
					
					if weapon ~= nil then v:Weapon_Switch( weapon ) end
					if fists ~= nil then v:Weapon_SetLast( weapon ) end
										
					-- remove this from the list so players get "unique" weapons
					table.remove( pool, idx )
					
				end
			end
			
			-- Add player conditions that will be defined by derived mutators
			for _, cond in ipairs( self.PlayerConditions ) do
				v:AddCondition( cond )
			end
			
			-- Call function you can derive in other modes to add other stuff (like high HP)
			self:OnWeaponAssigned( v, weapon )
			
		end
	end
	
end

-- Called at the start when weapon is given
function mutator:OnWeaponAssigned( pl, weap )

end

-- Called when when we are given a weapon at any moment (eg start of round, from a pickup)
function mutator:OnPlayerEquipped( pl, weap )

end

function mutator:ScaleHitboxDamage( pl, hitbox, info )
	return false
end

function mutator:Think()

end

function mutator:PlayerWon( winningPlayer )

end

mutators:Register( "default", mutator )

-- This mutator is only intended as a base and contains only weapons that fire bullets (useful for big head, high HP)
local bmutator = {}

bmutator.Base = "default"
bmutator.IsBase = true

bmutator.ItemPool = {
	"weapon_ax47",
	"weapon_beretta",
	"weapon_doublebarrel",
	"weapon_goldpistols",
	"weapon_mosin",
	"weapon_mp5k",
	"weapon_p90",
	"weapon_pistol",
	"weapon_railgun",
	"weapon_ruger",
	"weapon_saa",
	"weapon_shotgun",
	"weapon_tmp",
	"weapon_vintorez",
}

mutators:Register( "default_bullets", bmutator )


