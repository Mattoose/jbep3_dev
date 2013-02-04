from core.abilities import AbilityBase

class AbilityInfiltrate(AbilityBase):
    # Info
    name = "infiltrate"
    rechargetime = 2.0
    displayname = "#RebInfiltrate_Name"
    description = "#RebInfiltrate_Description"
    image_name = 'vgui/rebels/abilities/infiltrate'
    hidden = True
    cloakallowed = True
    
    # Ability Code
    def Init(self):
        super(AbilityInfiltrate, self).Init()
        
        # Just do the ability on creation ( == when you click the ability slot )
        self.SelectGroupUnits()
        
        # Cloak all if one is not cloaked
        # Only uncloak if all units in the selection are cloaked
        cloak = False
        for unit in self.units:
            if not unit.cloaked:
                cloak = True
        
        for unit in self.units:
            if not cloak:
                unit.UnCloak()
            else:
                unit.Cloak()
        self.Completed()
        
    serveronly = True # Do not instantiate on the client