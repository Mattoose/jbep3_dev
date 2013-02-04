from vmath import VectorNormalize, Vector
from core.abilities import AbilityTarget, AbilityUpgrade
from entities import MouseTraceData

if isserver:
    from entities import CreateEntityByName, DispatchSpawn
    from core.units import BaseBehavior
        
if isserver:
    class ActionHeal(BaseBehavior.ActionAbility):
        def Update(self):
            outer = self.outer
            
            target = self.order.target
            abi = self.order.ability
            autocasted = abi and abi.autocasted
            
            needsheal, reason = NeedsHealing(target)
            if not target or not needsheal:
                if self.outer.curorder == self.order:
                    self.outer.ClearOrder(dispatchevent=False)
                return self.ChangeToIdle('No target')
            
            # In range?
            dist = (outer.GetAbsOrigin() - self.order.position).Length2D()
            if dist > 48.0:
                return self.SuspendFor(self.behavior.ActionMoveInRange, 'Moving into heal range', self.order.position, maxrange=48.0) 
                
            # Facing?
            if not outer.FInAimCone(target, self.facingminimum):
                return self.SuspendFor(self.behavior.ActionFaceTarget, 'Not facing target', target, self.facingminimum)

            outer.healtarget = target
            self.healedtarget = True
            outer.DoAnimation(outer.ANIM_HEAL)
            outer.Heal() # Temporary do Heal here, animation event is broken in asw atm (blame Steve)
            return self.SuspendFor(self.behavior.ActionWaitForActivity, 'Playing heal animation', self.outer.animstate.specificmainactivity )
            
        def OnEnd(self):
            super(ActionHeal, self).OnEnd()
            
            if not self.healedtarget:
                self.order.ability.Cancel()

        def OnResume(self):
            if self.healedtarget:
                self.order.ability.Completed()
                self.outer.ClearOrder(dispatchevent=False)
            return super(ActionHeal, self).OnResume()
            
        healedtarget = False
        facingminimum = 0.7
        
def NeedsHealing(target):
    if not target or not target.IsAlive() or not target.IsUnit() or target.isbuilding:
        return False, '#Ability_InvalidTarget'
        
    if target.health >= target.maxhealth:
        return False, '#RebHeal_TargetFullHP'
        
    return True, None
    
# Spawns a grenade
class AbilityHeal(AbilityTarget):
    # Info
    name = "heal"
    rechargetime = 5.0
    energy = 35.0
    displayname = "#RebHeal_Name"
    description = "#RebHeal_Description"
    image_name = 'vgui/rebels/abilities/heal'
    defaultautocast = True
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata
            
            if self.ischeat:
                self.Completed()
                return

            pos = data.groundendpos
            target = data.ent
            
            if not self.unit:
                self.Cancel()
                return
                
            needsheal, reason = NeedsHealing(target)
            if not needsheal:
                self.Cancel(cancelmsg=reason)
                return
                
            if not self.TakeResources(refundoncancel=True):
                self.Cancel(cancelmsg='Ability_NotEnoughResources')
                return

            self.unit.AbilityOrder(position=pos,
                        target=target,
                        ability=self)
            self.SetNotInterruptible()
            
        behaviorgeneric_action = ActionHeal
        
    @classmethod
    def CheckAutoCastOnIdle(info, unit):
        if unit.orders:
            return False
        for i in range(0, unit.senses.CountSeenOther()):
            other = unit.senses.GetOther(i)
            if not other:
                continue
            needsheal, reason = NeedsHealing(other)
            if needsheal:
                leftpressed = MouseTraceData()
                leftpressed.groundendpos = other.GetAbsOrigin()
                leftpressed.ent = other
                unit.DoAbility(info.name, [('leftpressed', leftpressed)], autocasted=True)
                return True
        return False
        
    #infoprojtextures = [{'texture' : 'decals/testeffect'}]
    allowmultipleability = True
    