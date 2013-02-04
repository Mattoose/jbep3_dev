from entities import networked, entity

from core.units import UnitInfo, UnitBaseCombat as BaseClass, UnitBaseAirLocomotion

if isserver:
    from core.units import UnitCombatAirNavigator
    
@networked
class UnitBaseScanner(BaseClass):
    aiclimb = False
    LocomotionClass = UnitBaseAirLocomotion
    if isserver:
        NavigatorClass = UnitCombatAirNavigator
    
    def __init__(self):
        super(UnitBaseScanner, self).__init__()
        self.savedrop = 2048.0
        self.maxclimbheight = 2048.0
        self.testroutestartheight = 2048.0
        
    def Spawn(self):    
        super(UnitBaseScanner, self).Spawn()
        
        self.locomotion.desiredheight = 400.0
        
    projectedtexturedist = 600.0
        
@entity('unit_cscanner', networked=True)
class UnitScanner(UnitBaseScanner):
    pass
    
@entity('unit_observer')
class UnitObserver(UnitScanner):
    def Spawn(self):
        super(UnitObserver, self).Spawn()
        
        self.Cloak()
        
    cloakenergydrain = 0
    detector = True
    
class ScannerInfo(UnitInfo):
    name = 'unit_scanner'
    displayname = '#CombScanner_Name'
    description = '#CombScanner_Description'
    cls_name = 'unit_cscanner'
    modelname = 'models/combine_scanner.mdl'
    health = 30
    buildtime = 15.0
    costs = [('requisition', 2), ('power', 2)]
    sai_hint = set(['sai_unit_scout'])
    
class ObserverInfo(UnitInfo):
    name = 'unit_observer'
    displayname = '#CombObserver_Name'
    description = '#CombObserver_Description'
    image_name = 'vgui/combine/units/unit_observer'
    cls_name = 'unit_observer'
    modelname = 'models/combine_scanner.mdl'
    health = 30
    buildtime = 35.0
    costs = [('requisition', 2), ('power', 5)]
    sai_hint = set(['sai_unit_scout'])
    