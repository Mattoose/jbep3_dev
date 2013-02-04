from srcbase import *
from vmath import Vector
from entities import entity
from core.units import UnitInfo, UnitBase as BaseClass, CreateUnitFancy, PrecacheUnit
from core.resources import GiveResources, RESOURCE_REQUISITION, MessageResourceIndicator
import random
import bisect

# Small helper function for selecting units to some probability distribution
# http://rosettacode.org/wiki/Probabilistic_choice#Python
def probchoice(items, probs):
    '''\
    Splits the interval 0.0-1.0 in proportion to probs
    then finds where each random.random() choice lies
    '''

    prob_accumulator = 0
    accumulator = []
    for p in probs:
        prob_accumulator += p
        accumulator.append(prob_accumulator)
 
    while True:
        r = random.random()
        yield items[bisect.bisect(accumulator, r)]

@entity('crate', networked=True)
class UnitCrate(BaseClass):
    if isserver:
        def Precache(self):
            super(UnitCrate, self).Precache()
            
            map(PrecacheUnit, self.units_weak)
            map(PrecacheUnit, self.units_med)
            map(PrecacheUnit, self.units_strong)
            map(PrecacheUnit, self.units_superstrong)
            
        def Spawn(self):
            super(UnitCrate, self).Spawn()
            
            self.SetOwnerNumber(0)
            
            self.takedamage = DAMAGE_NO
            self.SetCanBeSeen(False)

            self.SetSolidFlags(FSOLID_NOT_SOLID|FSOLID_TRIGGER)
            self.SetMoveType(MOVETYPE_NONE)
            self.SetCollisionGroup(COLLISION_GROUP_NONE)

            self.CollisionProp().UseTriggerBounds(True,1)

            self.SetTouch(self.CrateTouch)
    else:
        def Spawn(self):
            super(UnitCrate, self).Spawn()

            self.Blink(-1) # Blink infinitely
            
        def OnNewModel(self):
            super(UnitCrate, self).OnNewModel()
        
            self.ForceUseFastPath(False)
            
    def CreateRandomUnit(self, unitlist, owner):
        unittype = random.sample(unitlist, 1)[0]
        CreateUnitFancy(unittype, self.GetAbsOrigin(), owner_number=owner)
        
    def CrateTouch(self, other):
        if not other or not other.IsUnit() or other.GetOwnerNumber() < 2:
            return
            
        options = self.unitinfo.options
        type = probchoice(options[0], options[1]).next()
        ownernumber = other.GetOwnerNumber()
            
        if type == 'requisition':
            req = random.randint(3, 7)
            GiveResources(ownernumber, [(RESOURCE_REQUISITION, req)], firecollected=True)
            MessageResourceIndicator(ownernumber, self.GetAbsOrigin(), 'req +%d' % (req))
        elif type == 'unit_weak':
            self.CreateRandomUnit(self.units_weak, ownernumber)
        elif type == 'unit_med':
            self.CreateRandomUnit(self.units_med, ownernumber)
        elif type == 'unit_strong':
            self.CreateRandomUnit(self.units_strong, ownernumber)
        elif type == 'unit_superstrong':
            self.CreateRandomUnit(self.units_superstrong, ownernumber)
            
        self.Remove()
        
    def SetLifeTime(self, lifetime):
        self.SetThink(self.Remove, gpGlobals.curtime + lifetime)
        
    units_weak = ['unit_rebel_partisan', 'unit_antlion', 'unit_zombie']
    units_med = ['unit_combine', 'unit_rebel', 'unit_combine_sg', 'unit_rebel_sg', 'unit_combine_ar2', 'unit_rebel_ar2', 'unit_zombine']
    units_strong = ['unit_hunter', 'unit_vortigaunt', 'unit_poisonzombie', 'unit_combine_elite']
    units_superstrong = ['unit_strider']
    
    # Override to supress warning, don't care about eyeoffset
    customeyeoffset = Vector(0,0,0)
        
class CrateInfo(UnitInfo):
    name = 'crate'
    cls_name = 'crate'
    displayname = "#Crate_Name"
    description = "#Crate_Description"
    modelname = 'models/props_junk/wood_crate002a.mdl'
    viewdistance = 256.0
    health = 1
    
    options = (['requisition', 'unit_weak', 'unit_med', 'unit_strong', 'unit_superstrong'], 
               [0.5, 0.25, 0.149, 0.1, 0.001])
    