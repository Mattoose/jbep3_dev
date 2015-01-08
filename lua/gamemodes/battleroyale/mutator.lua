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
			table.insert( mutnames, k )
		end
	end
	
	return mutnames[ math.random( #mutnames ) ]

end