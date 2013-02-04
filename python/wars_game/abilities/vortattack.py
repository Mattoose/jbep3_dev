from srcbase import DMG_SHOCK
from core.abilities import AbilityTargetGroup
from entities import MouseTraceData
from core.units import UnitInfo

class AbilityVortAttack(AbilityTargetGroup):
    # Info
    name = "vortattack"
    displayname = "#RebVortAtt_Name"
    description = "#RebVortAtt_Description"
    image_name = 'vgui/rebels/abilities/vortattack'
    hidden = True
    energy = 20
    rechargetime = 1.2
    defaultautocast = True
    
    # Ability
    if isserver:
        def ExecuteVortAttack(self, unit):
            try:
                return unit.vortattack
            except AttributeError:
                return False
                    
        def DoAbility(self):
            data = self.mousedata

            target = data.ent if (data.ent and not data.ent.IsWorld()) else None

            for unit in self.units:
                if self.ExecuteVortAttack(unit):
                    if self.TakeEnergy(unit):
                        unit.DoAnimation(unit.ANIM_RANGE_ATTACK1)
                        self.SetRecharge(unit)
                else:
                    if target:
                        self.unit.AttackOrder(ability=self, enemy=target)
                    
            self.Completed()
   
class VortAttack(UnitInfo.AttackBase):
    damage = 50
    damagetype = DMG_SHOCK
    minrange = 0.0
    maxrange = 820.0
    attackspeed = AbilityVortAttack.rechargetime
    cone = 0.7
    
    def CanAttack(self, unit, enemy):
        if not unit.abilitycheckautocast[unit.abilitiesbyname[AbilityVortAttack.name].uid]:
            return False
        return unit.CanRangeAttack(enemy.WorldSpaceCenter()) and AbilityVortAttack.CanDoAbility(None, unit=unit)
        
    def Attack(self, unit, enemy):
        leftpressed = MouseTraceData()
        leftpressed.ent = unit.enemy
        unit.vortattack = True
        unit.DoAbility(AbilityVortAttack.name, [('leftpressed', leftpressed)])
        unit.vortattack = False
        return True
        