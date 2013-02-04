"""Provides a python base for weapons."""
if isserver:
    from entities import CWarsWeapon as BaseClass
else:
    from entities import C_WarsWeapon as BaseClass
from core.units import UnitInfo
from kvdict import LoadFileIntoDictionaries
from gamerules import GetAmmoDef
    
class WarsWeaponBase(BaseClass):
    """ Base for weapons."""
    def __init__(self):
        super(WarsWeaponBase, self).__init__()
        
        if self.AttackPrimary:
            self.firerate = self.AttackPrimary.attackspeed
            self.maxrange1 = self.AttackPrimary.maxrange
            self.overrideammodamage = self.AttackPrimary.damage
            self.maxbulletrange = self.AttackPrimary.maxrange + 128.0
            
        if isclient:
            self.SetOverrideClassname(self.clientclassname)

    def StartRangeAttack(self):
        """ Called by units to do a range attack. """
        owner = self.GetOwner()
        owner.DoAnimation(owner.ANIM_ATTACK_PRIMARY) 
        self.PrimaryAttack()
        owner.nextattacktime = gpGlobals.curtime + self.firerate
        return False

    def StartMeleeAttack(self):
        """ Called by units to do a melee attack. """
        owner = self.GetOwner()
        owner.DoAnimation(owner.ANIM_MELEE_ATTACK1)
        self.PrimaryAttack()
        owner.nextattacktime = gpGlobals.curtime + self.firerate
        return False
        
    @staticmethod    
    def InitEntityClass(cls):
        BaseClass.InitEntityClass(cls)
        
        wpndata = LoadFileIntoDictionaries('scripts/%s.txt'% (cls.clientclassname))

        if wpndata:
            # Fill in the damage and damagetype for attacks (mainly used in the hud)
            # TODO: Maybe get rid of weapon scripts, since modifying the python code is just as easy?
            if cls.AttackPrimary:
                try:
                    primaryammo = wpndata['primary_ammo']
                    idx = GetAmmoDef().Index(primaryammo)
                except KeyError:
                    idx = -1
                    
                if idx != -1:
                    class AttackPrimary(cls.AttackPrimary):
                        name = cls.__name__
                        if cls.AttackPrimary.damage == 0:
                            damage = GetAmmoDef().PlrDamage(idx)
                        if cls.AttackPrimary.damagetype == 0:
                            damagetype = GetAmmoDef().DamageType(idx)
                    cls.AttackPrimary = AttackPrimary
            
            if cls.AttackSecondary:
                try:
                    secondaryammo = wpndata['secondary_ammo']
                    idx = GetAmmoDef().Index(secondaryammo)
                except KeyError:
                    idx = -1
                
                if idx != -1:
                    class AttackSecondary(cls.AttackSecondary):
                        name = cls.__name__
                        if cls.AttackSecondary.damage == 0:
                            damage = GetAmmoDef().PlrDamage(idx)
                        if cls.AttackSecondary.damagetype == 0:
                            damagetype = GetAmmoDef().DamageType(idx)
                    cls.AttackSecondary = AttackSecondary
            
        # Store it, just in case you want it somewhere..
        cls.wpndata = wpndata
        
    #: Overrides class name on the client. Used to read out the correct weapon script.
    clientclassname = None
    #: Used to directly cause a muzzle event, since we don't play weapon animations.
    muzzleoptions = None 
    
    # Aliases
    AttackBase = UnitInfo.AttackBase
    AttackRange = UnitInfo.AttackRange
    AttackMelee = UnitInfo.AttackMelee
    
    # Added to the list of units attacks in UnitBaseCombat.RebuildAttackInfo (if not None)
    AttackPrimary = None
    AttackSecondary = None
