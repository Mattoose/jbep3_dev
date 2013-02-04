from srcbase import SOLID_BBOX, FSOLID_NOT_STANDABLE, EF_NOSHADOW
from core.abilities import AbilityTarget
from core.units import CreateUnit, UnitBase, UnitInfo
from entities import entity, FOWFLAG_UNITS_MASK

if isserver:
    from core.units import UnitCombatSense

@entity('unit_scan', networked=True)
class Scan(UnitBase):
    def ShouldDraw(self):
        return False
        
    def IsSelectableByPlayer(self, player, target_selection):
        return False
        
    def GetIMouse(self):
        return None
        
    if isserver:
        def Spawn(self):
            super(Scan, self).Spawn()
            
            self.SetSolid(SOLID_BBOX)
            self.AddSolidFlags(FSOLID_NOT_STANDABLE)
            self.AddEffects(EF_NOSHADOW)
            self.SetCanBeSeen(False)
            
            self.senses = UnitCombatSense(self)
            
            self.SetThink(self.ScanThink, gpGlobals.curtime)
            
        def UpdateOnRemove(self):
            # ALWAYS CHAIN BACK!
            super(Scan, self).UpdateOnRemove()
            
            del self.senses
        
        def ScanThink(self):
            self.senses.PerformSensing()
            self.SetNextThink(gpGlobals.curtime + 0.1)
            
        def SetScanDuration(self, scanduration=10.0):
            self.SetThink(self.SUB_Remove, gpGlobals.curtime + scanduration, 'ScanDuration')

    fowflags = FOWFLAG_UNITS_MASK
    detector = True
    
class UnitScanInfo(UnitInfo):
    name = 'unit_scan'
    cls_name = 'unit_scan'
    viewdistance = 1200.0
    health = 0
    minimaphalfwide = 0 # Don't draw on minimap
    
class AbilityScan(AbilityTarget):
    # Info
    name = "scan"
    displayname = "#RebScan_Name"
    description = "#RebScan_Description"
    image_name = 'vgui/rebels/abilities/scan'
    hidden = True
    energy = 50
    rechargetime = 2.0
    scanduration = 10.0
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata

            if not self.ischeat:
                if not self.TakeEnergy(self.unit):
                    self.Cancel()
                    return
                
            pos = data.groundendpos
            pos.z += 512.0
            unit = CreateUnit('unit_scan', pos, owner_number=self.player.GetOwnerNumber())
            unit.SetScanDuration(self.scanduration)
            self.Completed()
            