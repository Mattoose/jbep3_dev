

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

print = function(...)		for arg,str in ipairs({...}) do  Msg(str.."\n")  end
end

require ("mutations")
require ("teams")