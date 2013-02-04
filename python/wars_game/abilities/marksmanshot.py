from srcbase import DMG_BULLET
from core.abilities import AbilityTarget
from entities import MouseTraceData
from core.units import UnitInfo

class AbilityMarkmanShot(AbilityTarget):
    # Info
    name = 'marksmanshot'
    displayname = '#CombMarkmanShot_Name'
    description = '#CombMarkmanShot_Description'
    image_name = 'vgui/combine/abilities/marksmanshot'
    hidden = True
    rechargetime = 3.5
    defaultautocast = True
    
    # Ability
    if isserver:
    
        def ExecuteMarkmanShot(self, unit):
            try:
                return unit.markmanshot
            except AttributeError:
                return False
                    
        def DoAbility(self):
            data = self.mousedata

            target = data.ent if (data.ent and not data.ent.IsWorld()) else None

            for unit in self.units:
                if self.ExecuteMarkmanShot(unit):
                    if self.TakeEnergy(unit):
                        unit.StartRangeAttack()
                        self.SetRecharge(unit)
                else:
                    if target:
                        self.unit.AttackOrder(ability=self, enemy=target)
                    
            self.Completed()
'''
class AttackMarkmanShot(UnitInfo.AttackBase):
    damage = 10
    damagetype = DMG_BULLET
    minrange = 0.0
    maxrange = 2048.0
    cone = 0.7
    attackspeed = AbilityMarkmanShot.rechargetime
    
    @staticmethod
    def CanAttack(unit, enemy):
        return unit.CanRangeAttack(enemy.WorldSpaceCenter()) and AbilityMarkmanShot.CanDoAbility(AbilityMarkmanShot, None, unit=unit)
        
    @staticmethod
    def Attack(unit, enemy):
        leftpressed = MouseTraceData()
        leftpressed.ent = unit.enemy
        unit.markmanshot = True
        unit.DoAbility(AbilityMarkmanShot.name, [('leftpressed', leftpressed)])
        unit.markmanshot = False
        return True
'''