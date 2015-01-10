local mutator = {}
local nextUpdateTime = 0
local startTime = 0

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeInstaGhosts_Title"
mutator.Description = "#JB_BR_RoundTypeInstaGhosts_Desc"

mutator.PlayerConditions = { JB_CONDITION_INVISIBLE, JB_CONDITION_AUTOSTAND }

mutator.ItemPool = {
	"weapon_handgun_insta",
	"weapon_goldengun",
	"weapon_railgun_insta",
	"weapon_neszapper",
}

function mutator:RoundStart()
	FindConVar( "jb_sv_fartsteps" ):SetValue( true )
	startTime = CurTime()
	nextUpdateTime = CurTime() + 5.0
end

function mutator:RoundEnd()
	FindConVar( "jb_sv_fartsteps" ):Revert()
	FindConVar( "jb_sv_ig_firerate" ):Revert()
end

function mutator:Think()
	-- Increase over time
	if CurTime() > nextUpdateTime then
		nextUpdateTime = CurTime() + 5

		local alivePlayers = 0
		for k, v in pairs( player.GetAll() ) do
			if v:IsAlive() and v:GetTeamNumber() == TEAM_PLAYERS and not v:ValidPossess() then
				alivePlayers = alivePlayers + 1
			end
		end

		local timeBased = math.RemapValClamped( CurTime() - startTime, 0, 80, 1.0, 0.07 )
		local playerBased = math.RemapValClamped( alivePlayers, 12, 2, 2.0, 0.07 )

		FindConVar( "jb_sv_ig_firerate" ):SetValue( math.min( playerBased, timeBased ) )
	end
end

mutators:Register( "instaghosts", mutator )
