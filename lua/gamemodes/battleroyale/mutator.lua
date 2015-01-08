mutators = {}
mutators.mutators = {}

-- Register mutator by name
function mutators:Register( name, tbl )
	
	if( self.mutators[ name ] ~= nil ) then
		print( "Trying to register already existing mutator " .. name .. "\n" )
		return
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
function mutator:Count()
	return #self.mutators
end

-- Returns a random mutator EXCEPT default
function mutator:GetRandom()

	local mutnames = {}
	
	for k, v in pairs( self.mutators ) do
		if k ~= "default" then -- exclude default
			table.insert( mutnames, k )
		end
	end
	
	return mutnames[ math.random( #mutnames ) ]

end