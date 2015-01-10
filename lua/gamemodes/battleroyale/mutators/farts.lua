local mutator = {}

mutator.Base = "default"
mutator.Name = "#JB_BR_RoundTypeFart_Title"
mutator.Description = "#JB_BR_RoundTypeFart_Desc"

mutator.ItemPool = { "weapon_pistol" }

mutators:Register( "farts", mutator )

function mutator:OnWeaponEquipped( pl, weap )
	if( weap ) then
		weap:AddCondition( JB_WEAPON_CONDITION_NO_PRIMARY )
	end
end