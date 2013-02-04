from core.abilities import AbilityInstant
if isserver:
    from core.units import BaseBehavior

class AbilityDispel(AbilityInstant):
    # Info
    name = "dispel"
    rechargetime = 1
    energy = 45
    displayname = "#RebDispel_Name"
    description = "#RebDispel_Description"
    image_name = 'vgui/rebels/abilities/dispel'
    hidden = True
    defaultautocast = True
    
    # Ability
    def DoAbility(self):
        self.SelectGroupUnits()
        units = self.TakeEnergy(self.units)
        for unit in units:
            unit.DoAnimation(unit.ANIM_VORTIGAUNT_DISPEL)
            unit.AbilityOrder(ability=self)
        self.SetRecharge(units)
        self.Completed()
        
    @classmethod
    def CheckAutoCastOnEnemy(info, unit):
        if not info.CanDoAbility(None, unit=unit):
            return False
        if unit.senses.CountEnemiesInRange(unit.DISPELRANGE) > 5:
            unit.DoAbility(info.name)
            return True
        return False
        
    if isserver:
        behaviorgeneric_action = BaseBehavior.ActionAbilityWaitForActivity
        
    # This ability object won't be created on the executing client
    serveronly = True