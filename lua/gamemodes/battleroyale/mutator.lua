mutators = {}
mutators.mutators = {}

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

function mutators:Get( name )
	return self.mutators[ name ]
end