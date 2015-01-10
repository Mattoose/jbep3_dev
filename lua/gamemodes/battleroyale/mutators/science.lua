local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeScience_Title"
mutator.Description = "#JB_BR_RoundTypeScience_Desc"

mutator.ItemPool = { "weapon_shotgun_scientist" }
mutator.PlayerModels = { "models/player/bms_scientist.mdl" }

mutators:Register( "science", mutator )

local nextScientistSpawn = 0

function mutator:RoundStart()
	nextScientistSpawn = CurTime() + 30
end

function mutator:Think()

	if( CurTime() >= nextScientistSpawn ) then
		local randomPlace = navmesh.GetRandomEmptyNavArea()

		if( randomPlace ) then
			local scientist = CreateEntityByName( "npc_scientist_chase")
			local pos = randomPlace:GetCenter() + Vector( 0, 0, 12 )
			local hidingSpots = randomPlace:GetHidingSpots()

			if( hidingSpots and #hidingSpots > 0 ) then
				pos = hidingSpots[ math.random( #hidingSpots ) ].pos
			end

			scientist:SetAbsOrigin( pos )
			scientist:Spawn()
			scientist:DropToFloor()
		end

		nextScientistSpawn = CurTime() + math.random( 7, 15 )
	end

end