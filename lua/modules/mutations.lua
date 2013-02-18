--
-- Our mutations module
-- Handles the mutation, calling appropriate hooks etc.
-- (you probably don't want to touch this, used by the engine)

local tostring = tostring
local pcall = pcall
local con = con
local table = table
local type = type
local pairs = pairs
local Warning = Warning

module("mutations")

local MutationsIndex = {}

--Used by the engine for when we want to call mutation hooks.
--Returns the value(s) given by the hook, puts them on the stack
--to be read engine side.

function call( func, mut, ... )
	
	if ( not mut ) then return nil end
	
	if ( not mut[func] ) then return nil end
	
	local status, results = pcall( mut[func], mut, ... )
	
	if ( not status ) then 	
		Warning( "[Lua] Failed to load \""..tostring(func).."\" (".. results ..")" )
		return nil		
	end
	
	if ( type( results ) == "table" ) then -- If it's a table
		return table.unpack( {results} ) -- Add the unpacked results to stack
	else -- otherwise
		return results -- just put it straight on
	end
	
end

function inherit( mut, base )

	for k, v in pairs( base ) do
		mut[k] = v
	end
	
	mut.Base = base	
	
end