import random

from entities import Disposition_t
from playermgr import relationships

from core.units import unitlistpertype
from core.strategicai import GroupRandomAttackMove, AbilityPlaceBuildingRuleRandom, AbilityPlaceBuildingRuleHintBased
from wars_game.buildings.combine import poweredlist

class GroupCaptureControlPoint(GroupRandomAttackMove):
    priority = 10
    
    curtarget = None
    
    def Init(self):
        unit = random.sample(self.units, 1)[0]
        
        # Lower group counts when there are hardly units on the map
        # Bigger counts are needed in the later stages
        enemycount = self.GetEnemyUnitCount()
        if self.curtarget and relationships[(unit.GetOwnerNumber(), self.curtarget.GetOwnerNumber())] != Disposition_t.D_NU:
            self.mincountunits = 1
            self.maxcountunits = 1
        elif enemycount < 10:
            self.maxcountunits = enemycount
            self.mincountunits = min(self.mincountunits, enemycount)
            
        super(GroupCaptureControlPoint, self).Init()
        
    def IsTargetAssignedToGroup(self, target):
        for group in self.sai.groups:
            if not group.IsSameGroup(self):
                continue
            if group.curtarget == target:
                return True
        return False
    
    def MatchesUnit(self, unit):
        if not super(GroupCaptureControlPoint, self).MatchesUnit(unit):
            return False
            
        # Can't have too many of these groups (shouldn't be needed, rather attack enemy)
        count = self.sai.groupcounts[self.name]
        if count > 2:
            return False
    
        # There must be a target
        fntestvalid = lambda cur: relationships[(unit.GetOwnerNumber(), cur.GetOwnerNumber())] != Disposition_t.D_LI and not self.IsTargetAssignedToGroup(cur)
        self.curtarget = self.FindNearest('control_point', unit.GetAbsOrigin(), filter=fntestvalid)
        if not self.curtarget:
            return False
            
        return True

    def StateActive(self):
        unit = random.sample(self.units, 1)[0]
        
        # Check if cur target is captured, in that case disband
        # Make sure we have a target
        if self.curtarget:
            if relationships[(self.sai.ownernumber, self.curtarget.GetOwnerNumber())] == Disposition_t.D_LI:
                self.DisbandGroup()
                return
        else:
            fntestvalid = lambda cur: relationships[(self.sai.ownernumber, cur.GetOwnerNumber())] != Disposition_t.D_LI
            self.curtarget = self.FindNearest('control_point', unit.GetAbsOrigin(), filter=fntestvalid)
            # If we can't find anything, disband
            if not self.curtarget:
                self.DisbandGroup()
                return
                
        targetpos = self.curtarget.GetAbsOrigin()
        grouporigin = self.GroupOrigin()
        
        # Don't need to do anything if our group is around the point and capturing
        if self.curtarget.playercapturing == unit.GetOwnerNumber() and (grouporigin - targetpos).Length2D() < 256.0:
            return
                
        # Update orders if needed
        if not unit.orders or (unit.curorder.position and (unit.curorder.position - targetpos).Length2D() > 256.0):
             self.AttackMove(targetpos)
         
class AbilityPlaceBuildingRuleHintBasedCombine(AbilityPlaceBuildingRuleHintBased):
    priority = 7
    
    def GetBuildingList(self):
        return unitlistpertype[self.sai.ownernumber]['build_comb_powergenerator']
        
    def GetAbilities(self):
        # Get ability list. Filter them here if needed.
        abilities = set()
        for abi in self.unit.sai_abilities:
            if 'sai_building_powered' in abi.sai_hint:
                abilities.add(abi)
        self.RemoveAbilitiesWithHints(set(['sai_building_powered']))
        return abilities
        
        
class AbilityPlaceBuildingRuleHintBasedCombinePowerGen(AbilityPlaceBuildingRuleRandom):
    priority = 5
    
    def GetBuildingList(self):
        # Filter power generators. Silly to place more power generators next to power generators
        buildinglist = super(AbilityPlaceBuildingRuleHintBasedCombinePowerGen, self).GetBuildingList()
        buildinglist = filter(lambda b: b.GetUnitType() != 'build_comb_powergenerator', buildinglist)
        return buildinglist
    
    def GetAbilities(self):
        # Get ability list. Filter them here if needed.
        abilities = set()
        for abi in self.unit.sai_abilities:
            if 'sai_building_powergen' in abi.sai_hint:
                abilities.add(abi)
        self.RemoveAbilitiesWithHints(set(['sai_building_powergen']))
        return abilities
    
    def GetBuildingHints(self):
        hintunitcounts = self.sai.hintunitcounts
        ownernumber = self.sai.ownernumber
        
        # The number of power gens should be about equal to the number of other buildings
        hints = set()
        if hintunitcounts['sai_building_powergen'] < 3 or int(hintunitcounts['sai_building']/2) > hintunitcounts['sai_building_powergen']:
            hints.add('sai_building_powergen')
        
        return hints
         
         