from core.abilities import AbilityBase

class AbilityRevolutionaryFervor(AbilityBase):
    name = 'revolutionaryfervor'
    displayname = "#RebRevFervor_Name"
    description = "#RebRevFervor_Description"
    image_name = 'vgui/rebels/abilities/revolutionaryfervor'
    hidden = True # Hidden from abilitypanel
    accuracybonus = 0.5
    
    @classmethod
    def OnUnitThink(info, unit):
        try:
            active = unit.revolutionaryfervoractive
        except AttributeError:
            unit.revolutionaryfervoractive = False
            unit.revolutionaryfervornextcheck = 0.0
            
        if unit.revolutionaryfervornextcheck > gpGlobals.curtime:
            return
            
        if len(unit.senses.GetOthers(unit.GetUnitType())) < 4:
            if unit.revolutionaryfervoractive:
                unit.accuracy -= info.accuracybonus
                unit.overrideaccuracy = unit.accuracy # Let client know
                unit.revolutionaryfervoractive = False
                unit.revolutionaryfervornextcheck = gpGlobals.curtime + 0.5
            return
        
        if not unit.revolutionaryfervoractive:
            unit.accuracy += info.accuracybonus
            unit.overrideaccuracy = unit.accuracy # Let client know
            unit.revolutionaryfervoractive = True
            unit.revolutionaryfervornextcheck = gpGlobals.curtime + 0.5
        