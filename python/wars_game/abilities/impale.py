from core.abilities import AbilityTarget
from entities import MouseTraceData

if isserver:
    from core.units import BaseBehavior
    
    class ActionImpale(BaseBehavior.ActionAbility):
        def OnStart(self):
            return self.SuspendFor(self.behavior.ActionMoveInRange, 'Moving into target range', 
                    self.order.target, self.outer.STRIDER_STOMP_RANGE-64.0)
                    
        def OnEnd(self):
            self.order.ability.Cancel()
            if self.outer.curorder == self.order:
                self.outer.ClearOrder(dispatchevent=False)
                
        def OnResume(self):
            target = self.order.target
            outer = self.outer
            if target and (outer.GetAbsOrigin() - target.GetAbsOrigin()).Length2D() < outer.STRIDER_STOMP_RANGE-32.0:
                outer.stomptarget = target
                outer.DoAnimation(outer.ANIM_STOMPL)
                self.order.ability.Completed()
                return self.ChangeTo(self.behavior.ActionWaitForActivityTransition, 'Waiting for impale act',
                    self.outer.animstate.specificmainactivity, self.behavior.ActionIdle)
            return self.ChangeTo(self.behavior.ActionIdle, 'Failed to impale')
                
class AbilityImpale(AbilityTarget):
    # Info
    name = 'impale'
    displayname = '#CombImpale_Name'
    description = '#CombImpale_Description'
    image_name = 'vgui/combine/abilities/impale'
    hidden = True
    rechargetime = 5.0
    
    def DoAbility(self):
        data = self.mousedata

        target = data.ent if (data.ent and not data.ent.IsWorld()) else None
        if not target:
            self.Cancel(cancelmsg='#Ability_InvalidTarget')
            return

        self.unit.AbilityOrder(ability=self, target=target)
        
    if isserver:
        behaviorgeneric_action = ActionImpale
