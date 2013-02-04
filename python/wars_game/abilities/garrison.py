from core.abilities import AbilityTargetGroup
if isserver:
    from core.units import BaseBehavior, BehaviorGeneric
    
if isserver:
    class ActionGarrisonBuilding(BehaviorGeneric.ActionAbility):
        def OnStart(self):
            return self.SuspendFor(ActionDoGarrisonBuilding, 'Moving in range', self.order.target)
            
        def OnEnd(self):
            # Give back movement control to locomotion component
            self.outer.aimoving = False
            
        def OnResume(self):
            if self.outer.garrisoned:
                self.outer.navigator.StopMoving()
                self.outer.aimoving = False
            return super(ActionGarrisonBuilding, self).OnResume()
            
        def OnNewEnemy(self, enemy):
            if self.outer.garrisoned:
                return self.SuspendFor(self.behavior.ActionAttackNoMovement, 'Enemy, lock on.', enemy)
            
    class ActionDoGarrisonBuilding(BehaviorGeneric.ActionMoveTo):
        def Init(self, target, *args, **kwargs):
            super(ActionDoGarrisonBuilding, self).Init(target, *args, **kwargs)
            
            self.target = target
            
        def OnNavComplete(self):
            target = self.target
            if target:
                target.GarrisonUnit(self.outer)
            return self.Done("NavComplete, moved to position")
            
class AbilityGarrison(AbilityTargetGroup):
    # Info
    name = "garrison"
    hidden = True
    
    @classmethod
    def OverrideOrder(cls, unit, data, player):
        ent = data.ent
        if not ent and not ent.IsUnit():
            return
        
        try:
            if not ent.garrisonable:
                return
        except AttributeError:
            return

        if ent.CanGarrisonUnit(unit):
            if isserver:
                unit.DoAbility(cls.name, [('leftpressed', data)])
            return True
        return False
        
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata
            target = data.ent

            for unit in self.units:
                unit.AbilityOrder(target=target, ability=self)
            self.Completed()
            
        behaviorgeneric_action = ActionGarrisonBuilding