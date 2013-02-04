from core.abilities import AbilityTargetGroup
from entities import MouseTraceData, D_HT
    
def NeedsConstructOrRepair(target):
    needsconstruct, reason = NeedsConstruct(target)
    if needsconstruct: return needsconstruct, reason
    return NeedsRepair(target)
    
def NeedsConstruct(target):
    if not target or not target.IsUnit() or not target.isbuilding:
        return False, '#Ability_InvalidTarget'
        
    if target.constructionstate != target.BS_CONSTRUCTED and not target.autoconstruct:
        return True, None
        
    return False, '#AbilityConstruct_NoConstReq'
    
def NeedsRepair(target):
    if not target or not target.IsUnit() or not target.isbuilding:
        return False, '#Ability_InvalidTarget'
        
    if target.constructionstate != target.BS_CONSTRUCTED:
        return False, '#AbilityConstruct_NotConstr'
        
    if target.health >= target.maxhealth:
        return False, '#AbilityConstruct_FullHP'
        
    return True, None
    
class AbilityConstruct(AbilityTargetGroup):
    # Info
    name = "construct"
    image_name = 'vgui/abilities/construct.vmt'
    rechargetime = 0
    displayname = "#AbilityConstruct_Name"
    description = "#AbilityConstruct_Description"
    defaultautocast = True

    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata
            target = data.ent
            if not target or self.unit.IRelationType(target) == D_HT:
                self.Cancel(cancelmsg='Invalid target')
                return
                
            if self.insertinfront:
                alwaysqueue = True
                idx = 0
            else:
                alwaysqueue = False
                idx = None
            
            needsconstruct, reason = NeedsConstruct(target)
            needsrepair, reason2 = NeedsRepair(target)
            if needsconstruct:
                for unit in self.units:
                    self.behaviorgeneric_action = unit.behaviorgeneric.ActionConstruct
                    unit.AbilityOrder(target=target, ability=self, alwaysqueue=alwaysqueue, idx=idx)
                self.Completed()
            elif needsrepair:
                for unit in self.units:
                    self.behaviorgeneric_action = unit.behaviorgeneric.ActionRepair
                    unit.AbilityOrder(target=target, ability=self, alwaysqueue=alwaysqueue, idx=idx)
                self.Completed()
            else:
                self.Cancel(cancelmsg=reason2)
                
    @classmethod
    def OverrideOrder(cls, unit, data, player):
        if unit.orders:
            return False
        needscr, reason = NeedsConstructOrRepair(data.ent)
        if needscr:
            if isserver:
                unit.DoAbility('construct', [('leftpressed', data)])
            return True
        return False
            
    @classmethod
    def CheckAutoCastOnIdle(info, unit):
        if unit.orders or unit.activeability:
            return False
        for i in range(0, unit.senses.CountSeenOther()):
            other = unit.senses.GetOther(i)
            if not other:
                continue
            needscr, reason = NeedsConstructOrRepair(other)
            if needscr:
                leftpressed = MouseTraceData()
                leftpressed.ent = other
                unit.DoAbility(info.name, [('leftpressed', leftpressed)], autocasted=True)
                return True
        return False
        
    @classmethod
    def TryRepairTarget(info, unit, target):
        needscr, reason = NeedsConstructOrRepair(target)
        if needscr:
            leftpressed = MouseTraceData()
            leftpressed.ent = target
            unit.DoAbility(info.name, [('leftpressed', leftpressed)], autocasted=True)
            return True
        return False
                
    CheckAutoCastOnEnemy = CheckAutoCastOnIdle
        