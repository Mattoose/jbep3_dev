local mutator = {}

mutator.Base = "default_bullets"
mutator.Name = "#JB_BR_RoundTypeVampirism_Title"
mutator.Description = "#JB_BR_RoundTypeVampirism_Desc"
mutator.ExtraTime = 30

mutator.PlayerConditions = { JB_CONDITION_INFINITE_AMMO, JB_CONDITION_NO_HEALTH_RATIONS }

function mutator:PlayerDamageTaken( pl, info, health )

	local attacker = info:GetAttacker()
	
	if( attacker and attacker:IsPlayer() ) then
		attacker:SetHealth( math.min( attacker:GetHealth() + math.min( info:GetDamage(), health ), 999 ) )
	end
	
end

mutators:Register( "vampirism", mutator )

