from core.abilities import AbilityTargetGroup

class AbilityCharge(AbilityTargetGroup):
    # Info
    name = "charge"
    image_name = 'vgui/abilities/charge.vmt'
    rechargetime = 1
    displayname = "#AbilityCharge_Name"
    description = "#AbilityCharge_Description"
    hidden = True
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()
            
            target = data.ent
            if target and target.IsWorld():
                target = None
            
            for unit in self.units:
                self.behaviorgeneric_action = unit.behaviorgeneric.ActionPreChargeMove
                unit.AbilityOrder(
                            position=data.endpos,
                            target=target,
                            ability=self)
            self.SetRecharge(self.units)
            self.Completed()