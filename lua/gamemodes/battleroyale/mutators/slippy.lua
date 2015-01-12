local mutator = {}

mutator.Base = "default"
mutator.Name = "Slippy"
mutator.Description = "Zero friction, double speed"

function mutator:RoundStart()
	FindConVar( "sv_friction" ):SetValue( 0 )
end

function mutator:RoundEnd()
	FindConVar( "sv_friction" ):Revert()
end

function mutator:OnWeaponAssigned( pl, weap )
	pl:SetSpeedMod( 2.5 )
end

mutators:Register( "slippy", mutator )

