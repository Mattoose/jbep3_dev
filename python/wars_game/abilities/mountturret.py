from core.abilities import AbilityTarget

def CanMountTurret(unit, target):
    if not target or target.IsWorld():
        return False, '#Ability_InvalidTarget'
    
    # TODO: Need better check for testing if it is a turret
    try:
        if not target.ismountableturret:
            return False, '#MountTur_NotATurret'
    except AttributeError:
        return False, '#MountTur_NotATurret'
        
    # Can't mount turret of someone else
    if unit.GetOwnerNumber() != target.GetOwnerNumber():
        return False, '#MountTur_NotMine'
        
    # Should be constructed
    if not target.constructionstate is target.BS_CONSTRUCTED:
        return False, '#MountTur_NotConstructed'

    # Check if not yet occupied
    if target.controller:
        return False, '#MountTur_AlreadyMounted'
        
    return True, None

if isserver:
    from core.units.intention import BaseAction
    from core.units import BehaviorGeneric

    class ActionMountTurret(BehaviorGeneric.ActionAbility):
        def CheckNearTurret(self):
            # Check turret alive
            if not self.turret or not self.turret.IsAlive():
                self.outer.ClearOrder(dispatchevent=False)
                return self.ChangeTo(self.behavior.ActionIdle, "Turret went None. Died?")
                
            # Check if we are on the manpoint
            dist = (self.turret.manpoint - self.outer.GetLocalOrigin()).Length2D()
            if dist > self.TOLERANCE:
                return self.SuspendFor(self.behavior.ActionMoveTo, "Moving to manpoint (dist: %d)" % (dist), self.turret.manpoint, self.TOLERANCE-1)
            
            # Enter the mount action
            return self.SuspendFor(ActionControlTurret, "On manpoint, start control turret", self.turret)
            
        def OnStart(self):
            self.turret = self.order.target
            return self.CheckNearTurret()
            
        def OnResume(self):
            return self.CheckNearTurret()
            
        TOLERANCE = 8.0
            
    class ActionControlTurret(BaseAction):
        def Init(self, turret):
            self.turret = turret.GetHandle()
        
        def OnStart(self):
            # Take movement control
            self.outer.navigator.StopMoving()
            self.outer.aimoving = True
            self.outer.Mount()
            self.firetime = 0.0
            if self.turret:
                self.turret.OnStartControl(self.outer)
                self.turret.yawturnspeed = self.outer.yawspeed
        
        def OnEnd(self):
            # Give back movement control and clear facing
            self.outer.Dismount()
            self.outer.aimoving = False
            self.outer.navigator.idealyaw = -1
            if self.turret:
                self.turret.enemy = None
                self.turret.OnLeftControl()
        
        def Update(self):
            outer = self.outer
            turret = self.turret
            
            # Check turret alive
            if not turret or not turret.IsAlive():
                return self.Done("Turret went None. Died?")

            # Update facing yaw
            if outer.navigator.idealyaw != turret.aimyaw:
                outer.navigator.idealyaw = turret.aimyaw
            
            # Update turret enemy (turret will always point to the target)
            # Use the sensing component of the turret, since it is setup to detect within the range of the turret
            # TODO: Maybe clamp turret sensing to our own sensing? However might not be needed since the fog of war already takes care of that.
            turret.senses.PerformSensing()
            turret.UpdateEnemy(turret.senses)
            enemy = turret.enemy
            
            # Fire if in our aim cone
            if enemy:
                attackinfo = turret.unitinfo.AttackTurret
                dist = (enemy.GetAbsOrigin() - turret.GetAbsOrigin()).Length2D()
                if dist < attackinfo.range and outer.FInAimCone(enemy, attackinfo.cone):    
                    self.firetime += outer.think_freq
                    bulletcount = 0

                    while self.firetime > attackinfo.attackspeed:
                        bulletcount += 1
                        self.firetime -= attackinfo.attackspeed
                    if bulletcount:
                        self.turret.Fire(bulletcount, outer)
            
            return self.Continue()
            
class AbilityMountTurret(AbilityTarget):
    # Info
    name = 'mountturret'
    displayname = '#MountTur_Name'
    description = '#MountTur_Description'
    image_name = 'vgui/abilities/mountturret'
    hidden = True
    
    @classmethod
    def OverrideOrder(cls, unit, data, player):
        canmount, reason = CanMountTurret(unit, data.ent)
        if canmount:
            if isserver:
                unit.DoAbility('mountturret', [('leftpressed', data)])
            return True
        return False
        
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.player.GetMouseData()

            target = data.ent if (data.ent and not data.ent.IsWorld()) else None
            
            canmount, reason = CanMountTurret(self.unit, target)
            if not canmount:
                self.Cancel(cancelmsg=reason)
                return

            self.unit.AbilityOrder(ability=self, target=target, position=data.endpos)
            self.Completed()
                
        behaviorgeneric_action = ActionMountTurret
