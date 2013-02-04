from vmath import VectorNormalize, Vector
from core.abilities import AbilityTarget
from entities import FClassnameIs

if isserver:
    from wars_game.ents.prop_combine_ball import CreateCombineBall
    
    from core.units import BehaviorGeneric
    
    # Action
    class ActionDoShootCombineBall(BehaviorGeneric.ActionAbility):
        def OnStart(self):
            return self.SuspendFor(ActionShootCombineBall, 'Shooting ball', self.order)
            
        def OnResume(self):
            if self.outer.curorder == self.order:
                self.outer.ClearOrder(dispatchevent=False)
            return super(ActionDoShootCombineBall, self).OnResume()
            
        def OnEnd(self):
            super(ActionDoShootCombineBall, self).OnEnd()
            
            if not self.order.ability.stopped:
                self.order.ability.Cancel()

    class ActionShootCombineBall(BehaviorGeneric.ActionMoveInRangeAndFace):
        def Init(self, order):
            if order.target:
                super(ActionShootCombineBall, self).Init(order.target, 1024.0)
            else:
                super(ActionShootCombineBall, self).Init(order.position, 1024.0)
            
            self.ability = order.ability
            
        def Update(self):
            if not self.target:
                self.ability.Cancel()
                return self.Done('Lost target')
            return super(ActionShootCombineBall, self).Update()
            
        def OnInRangeAndFacing(self):
            self.outer.activeweapon.SecondaryAttack()
            self.ability.TakeResources()
            self.ability.SetRecharge(self.outer)
            self.ability.Completed()
            return self.Done('Fired')

# Spawns a combine ball
class AbilityCombineBall(AbilityTarget):
    # Info
    name = "combineball"
    displayname = '#CombBall_Name'
    description = '#CombBall_Description'
    image_name = 'vgui/abilities/ability_ar2orb.vmt'
    image_dis_name = 'vgui/abilities/ability_ar2orb.vmt'
    costs = [[('requisition', 1)], [('kills', 1)]]
    rechargetime = 10
    #techrequirements = ['combineball_unlock']
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()
            
            if self.ischeat:
                vecShootDir = data.endpos - self.player.GetAbsOrigin()
                VectorNormalize( vecShootDir )
                
                CreateCombineBall( self.player.GetAbsOrigin(), vecShootDir * 10000.0, 10, 150, 4, self.player )
                self.Completed()
                return
                
            if not self.TakeResources(refundoncancel=True):
                self.Cancel(cancelmsg='#Ability_NotEnoughResources')
                return

            target = data.ent if (data.ent and not data.ent.IsWorld()) else None
            self.unit.AbilityOrder(ability=self, target=target, position=data.endpos)
            self.SetNotInterruptible()

        behaviorgeneric_action = ActionDoShootCombineBall
        
    @classmethod    
    def GetRequirements(info, player, unit):
        requirements = set()
        activeweapon = unit.activeweapon
        if not activeweapon or not FClassnameIs(activeweapon, 'weapon_ar2'):
            requirements.add('requirear2')
        return requirements | super(AbilityCombineBall, info).GetRequirements(player, unit)
        
    @classmethod    
    def ShouldShowAbility(info, unit):
        activeweapon = unit.activeweapon
        if not activeweapon or not FClassnameIs(activeweapon, 'weapon_ar2'):
            return False
        return super(AbilityCombineBall, info).ShouldShowAbility(unit)
        
# Unlock for ar2 ball?
# class AbilityCombineBallUnlock(AbilityUpgrade):
    # name = 'combineball_unlock'
    # displayname = '#CombBallUnlock_DisplayName'
    # description = '#CombBallUnlock_Description'
    # image_name = "vgui/abilities/ability_ar2orb.vmt"
    # buildtime = 10.0
    # costs = [[('kills', 5)], [('requisition', 5)]]
