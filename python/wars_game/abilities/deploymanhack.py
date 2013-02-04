from core.abilities import AbilityInstant
from core.units import unitpopulationcount, GetMaxPopulation

if isserver:
    from core.units import BaseBehavior

class AbilityDeployManhack(AbilityInstant):
    # Info
    name = 'deploymanhack'
    displayname = '#CombDepManhack_Name'
    description = '#CombDepManhack_Description'
    image_name = 'vgui/combine/abilities/deploymanhack'
    rechargetime = 35.0
    population = 1
    costs = [[('requisition', 1)], [('kills', 1)]]
    activatesoundscript = '#deploymanhacks'
    hidden = True
    
    @classmethod 
    def GetRequirements(info, player, unit):
        requirements = super(AbilityDeployManhack, info).GetRequirements(player, unit)
        ownernumber = player.GetOwnerNumber()

        if info.population:
            # Check population count
            if unitpopulationcount[ownernumber]+info.population > GetMaxPopulation(ownernumber):
                requirements.add('population')
        return requirements
        
    # Ability
    def DoAbility(self):
        self.SelectGroupUnits()
        self.PlayActivateSound()
        n = self.TakeResources(refundoncancel=True, count=len(self.units))
        if not n:
            self.Cancel(cancelmsg='#Ability_NotEnoughResources')
            return
        for unit in self.units[0:n]:
            unit.DoAnimation(unit.ANIM_DEPLOYMANHACK)
            unit.AbilityOrder(ability=self)
        self.SetRecharge(self.units)
        self.Completed()
        
    if isserver:
        behaviorgeneric_action = BaseBehavior.ActionAbilityWaitForActivity
    serveronly = True
        
    
    