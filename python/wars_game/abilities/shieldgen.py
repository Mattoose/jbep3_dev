from core.abilities import AbilityBase, AbilityTarget

# Connect to another generator
class AbilityGenConnectInfo(AbilityTarget):
    # Info
    name = 'genconnect'
    image_name = 'vgui/abilities/ability_unknown.vmt'
    rechargetime = 0
    displayname = '#CombGenConnect_Name'
    description = '#CombGenConnect_Description'
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()
            gen = data.ent
            
            if not gen or not gen.IsUnit() or gen.unitinfo != self.unit.unitinfo or gen == self.unit:
                # TODO: Inform player
                return
                
            # Check range
            dist = (self.unit.GetAbsOrigin() - gen.GetAbsOrigin()).Length2D()
            if dist > self.unit.maxgenrange:
                # TODO: Inform user
                return
                
            # Connect or destroy
            if self.unit.GetLink(gen):
                self.unit.DestroyLink(self.unit.GetLink(gen))
            else:
                self.unit.CreateLink(gen)
                
# Destroy all links of this generator
class AbilityGenDestroyLinks(AbilityBase):
    # Info
    name = "gendestroylinks"
    image_name = 'vgui/abilities/ability_unknown.vmt'
    rechargetime = 0
    displayname = "#CombGenDestroyLinks_Name"
    description = "#CombGenDestroyLinks_Description"
    hidden = True
    
    # Ability
    def Init(self):
        super(AbilityGenDestroyLinks, self).Init()
        
        self.SelectGroupUnits()
        for unit in self.units:
            unit.DestroyAllLinks()
        
    serveronly = True # Do not instantiate on the client