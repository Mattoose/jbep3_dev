-- Gamemode module
local _G = _G
local table = table

module("gamemode")

local gamemodes = {}

-- Register a gamemode
function register( tMode, sName, sBase )
	-- If it's already regisered, bail
	if ( gamemodes[ sName ] ~= nil ) then 
		return
	end

	-- Inherit from a base mode if it exists
	if sBase ~= sName then
		local tBase = gamemodes[ sBase ]
		if ( tBase ~= nil ) then
			tMode = table.inherit( tMode, tBase )
		else
			_G.print( "Error deriving gamemode, "..sBase.." not found.\n" )
		end
	end
	
	-- Add a self accessor

	-- Dump us into the gamemodes table
	_G.print( "Registered gamemode '"..sName.."' (derived from "..sBase..")\n" )
	gamemodes[ sName ] = tMode
end

-- Call a gamemode method
function call( sName, ... )
	-- Some sanity checking
	if ( _G.GAMEMODE == nil) then
		return
	end

	if _G.GAMEMODE[ sName ] == nil then
		_G.print( "Gamemode function "..sName..", not found! Please add me to the base gamemode!\n" )
		return
	end

	-- TODO: Pass through hook system

	-- Call func
	local funcToCall = _G.GAMEMODE[ sName ]
	return funcToCall( _G.GAMEMODE, ... )
end

-- Gets gamemode from our local table, called by engine
function get( sName )
	return gamemodes[ sName ]
end

-- Checks if a gamemode by this name is registered
function isRegistered( sName )
	return gamemodes[ sName ] ~= nil
end