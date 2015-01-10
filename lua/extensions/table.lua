-- Useful extensions for table

require( "table" )

-- Inherits from tBase, only copies missing data
function table.inherit( tTable, tBase )
	-- If we have no base, return main table
	if ( tBase == nil ) then return tTable end

	-- Copy base values 
	for k, v in pairs( tBase ) do 
		-- Only copy if it doesn't exist in our dest table
		if ( tTable[k] == nil ) then
			tTable[k] = v
		end
	end
	
	-- Store a copy of our base table within our destination
	tTable.baseClass = tBase
	
	return tTable
end

-- table dump
function table.dump( tTable, iIndent )
	if not iIndent then iIndent = 0 end
	if iIndent > 10 then return end

	for k, v in pairs( tTable ) do
		format = string.rep( "  ", iIndent ) .. tostring( k ) .. ": "

		if type( v ) == "table" then
			print( format .. "\n" )
			table.dump( v, iIndent + 1 )
		else
			print( format .. tostring( v ) .. "\n" )
		end
	end
end

-- Contains
function table.containsValue( tTable, value )
	for k, v in pairs( tTable ) do
		if ( v == value ) then return true end
	end

	return false
end