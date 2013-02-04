from vmath import VectorNormalize, Vector
from core.abilities import AbilityTarget, AbilityUpgrade

if isserver:
    from entities import CreateEntityByName, DispatchSpawn
    from core.units import BaseBehavior
        
if isserver:
    class ActionThrowGrenade(BaseBehavior.ActionAbility):
        def Update(self):
            outer = self.outer
            
            target = self.order.target if (self.order.target and not self.order.target.IsWorld()) else self.order.position
            
            # In range?
            dist = (outer.GetAbsOrigin() - self.order.position).Length2D()
            if dist > 1024.0:
                return self.SuspendFor(self.behavior.ActionMoveInRange, 'Moving into grenade throw range', self.order.position, maxrange=1024.0) 
                
            # Facing?
            if not outer.FInAimCone(target, self.facingminimum):
                return self.SuspendFor(self.behavior.ActionFaceTarget, 'Not facing target', target, self.facingminimum)

            self.throwedgrenade = True
            outer.DoAnimation(outer.ANIM_THROWGRENADE)
            return self.SuspendFor(self.behavior.ActionWaitForActivity, 'Executing attack', self.outer.animstate.specificmainactivity )
            
        def OnEnd(self):
            super(ActionThrowGrenade, self).OnEnd()
            
            if not self.throwedgrenade:
                self.order.ability.Cancel()

        def OnResume(self):
            if self.throwedgrenade:
                self.order.ability.SetRecharge(self.outer)
                self.order.ability.Completed()
                self.outer.ClearOrder(dispatchevent=False)
            return super(ActionThrowGrenade, self).OnResume()
            
        throwedgrenade = False
        facingminimum = 0.7
        
# Spawns a grenade
class AbilityGrenade(AbilityTarget):
    # Info
    name = "grenade"
    image_name = 'vgui/abilities/ability_grenade.vmt'
    rechargetime = 5
    costs = [[('requisition', 1)], [('kills', 1)]]
    displayname = "#AbilityGrenade_Name"
    description = "#AbilityGrenade_Description"
    techrequirements = ['grenade_unlock']
    activatesoundscript = '#grenade'
    
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata
            
            if self.ischeat:
                playerpos = self.player.GetAbsOrigin() + self.player.GetCameraOffset() 
                vecShootDir = data.endpos - playerpos
                VectorNormalize( vecShootDir )
                grenade = CreateEntityByName("grenade_frag" )
                grenade.SetAbsOrigin(playerpos)
                DispatchSpawn(grenade)  
                grenade.SetVelocity( vecShootDir * 10000.0, Vector(0, 0, 0) )
                grenade.SetTimer( 2.0, 2.0 - grenade.FRAG_GRENADE_WARN_TIME )
                self.Completed()
                return

            pos = data.groundendpos
            target = data.ent
            
            if not self.TakeResources(refundoncancel=True):
                self.Cancel(cancelmsg='#Ability_NotEnoughResources', debugmsg='not enough resources')
                return

            self.unit.AbilityOrder(position=pos,
                        target=target,
                        ability=self)
            self.SetNotInterruptible()
            
        behaviorgeneric_action = ActionThrowGrenade
        
    '''
    # Silly test
    @classmethod
    def CheckAutoCastOnEnemy(info, unit):
        print 'checking grenade autocast'
        if info.CanDoAbility(info, None, unit=unit):
            enemy = unit.enemy
            from entities import MouseTraceData
            leftpressed = MouseTraceData()
            leftpressed.endpos = enemy.GetAbsOrigin()
            leftpressed.groundendpos = enemy.GetAbsOrigin()
            leftpressed.ent = enemy
            unit.DoAbility(info.name, mouse_inputs=[('leftpressed', leftpressed)])
            return True
        return False
    '''
        
    infoprojtextures = [{'texture' : 'decals/testeffect'}]
    allowmultipleability = True
    
class OverrunAbilityGrenade(AbilityGrenade):
    name = "overrun_grenade"
    techrequirements = ['or_tier2_research']
    hidden = True
    
# Unlock for grenade
class AbilityGrenadeUnlock(AbilityUpgrade):
    name = 'grenade_unlock'
    displayname = '#AbilityGrenadeUnlock_DisplayName'
    description = '#AbilityGrenadeUnlock_Description'
    image_name = "vgui/abilities/ability_grenade.vmt"
    buildtime = 120.0
    costs = [[('kills', 5)], [('requisition', 5)]]
        
