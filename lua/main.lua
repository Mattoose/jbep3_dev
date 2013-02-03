-- Hello.

-- global defines -- move these out?

STATE_ACTIVE = 0
STATE_WELCOME = 1
STATE_PICKINGTEAM = 2
STATE_DEATH_ANIM = 3
STATE_OBSERVER_MODE = 4

HUD_PRINTNOTIFY		= 1
HUD_PRINTCONSOLE	= 2
HUD_PRINTTALK		= 3
HUD_PRINTCENTER		= 4

TEAM_INVALID = -1
TEAM_UNASSIGNED = 0
TEAM_SPECTATOR = 1
TEAM_CUSTOM = 2

function table.copy(t) --todo, move this to an extension i guess
	local t2 = {}
	for k,v in pairs(t) do
		t2[k] = v
	end
	return t2
end

function merge(t1, t2)
    for k, v in pairs(t2) do
        if (type(v) == "table") and (type(t1[k] or false) == "table") then
            merge(t1[k], t2[k])
        else
            t1[k] = v
        end
    end
    return t1
end
