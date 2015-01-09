include( "shared.lua" )

function GM:Init()
end

function GM:GetTimerSubText()
	-- TODO: Localize me!
	local iAlivePlayers = 0
	for k, v in pairs( player.GetAll() ) do
		if v:IsAlive() then 
			iAlivePlayers = iAlivePlayers + 1
		end
	end

	if iAlivePlayers > 1 then
		return iAlivePlayers.." players remaining"
	elseif iAlivePlayers == 1 then
		return iAlivePlayers.." player remaining"
	else
		return ""
	end
end
