-- Gamemode module
local _G = _G

module("gamemode")

local gamemodes = {}

-- Register a gamemode
function register( tMode, sName, sBase )
	-- If it's already regisered, bail
	if ( gamemodes[ sName ] ~= nil ) then 
		return
	end

	-- Inherit from a base mode if it exists
	local tBase = gamemodes[ sBase ]
	if ( tBase ~= nil ) then
		tMode = table.inherit( tMode, tBase )
	end

	-- Dump us into the gamemodes table
	_G.print( "Registered gamemode '".. sName .."'")
	gamemodes[ sName ] = tMode
end

-- Call a gamemode method
function call( sName, ... )
	-- Some sanity checking
	if ( _G.GAMEMODE == nil) then
		_G.print( "Error calling gamemode function, no gamemode loaded.\n" )
		return
	end

	if _G.GAMEMODE[ sName ] == nil then
		_G.print( "Error calling gamemode function "..sName..", not found.\n" )
		return
	end

	-- TODO: Pass through hook system

	-- Call func
	return _G.GAMEMODE[ sName ]( ... )
end

-- Gets gamemode from our local table, called by engine
function get( sName )
	return gamemodes[ sName ]
end

-- Checks if a gamemode by this name is registered
function isRegistered( sName )
	return gamemodes[ sName ] ~= nil
end