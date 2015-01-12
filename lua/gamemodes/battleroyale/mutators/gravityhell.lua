local mutator = {}

mutator.Base = "default"
mutator.Name = "Gravity Hell"
mutator.Description = "High speed, zero friction, extreme gravity tripmines"
mutator.ItemPool = { "weapon_gravtripmine" }
mutator.PlayerConditions = { JB_CONDITION_INFINITE_MAGAZINE, JB_CONDITION_AUTOSTAND }

function mutator:RoundStart()
	FindConVar( "sv_friction" ):SetValue( 0 )
	FindConVar( "jb_wep_gravtrip_sucktime" ):SetValue( 20 )
	FindConVar( "jb_wep_gravtrip_radius" ):SetValue( 1600 )
	FindConVar( "jb_wep_gravtrip_force" ):SetValue( -300 )
end

function mutator:RoundEnd()
	FindConVar( "sv_friction" ):Revert()
	FindConVar( "jb_wep_gravtrip_sucktime" ):Revert()
	FindConVar( "jb_wep_gravtrip_radius" ):Revert()
	FindConVar( "jb_wep_gravtrip_force" ):Revert()
end

function mutator:OnWeaponAssigned( pl, weap )
	pl:SetSpeedMod( 2.5 )
end

mutators:Register( "gravityhell", mutator )

