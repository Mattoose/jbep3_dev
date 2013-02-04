""" Maps an attribute name to a class. """
import gamemgr
from fields import StringField
if isclient:
    from vgui import localize
    
# Attribute db
dbid = 'attributes'
dbattributes = gamemgr.dblist[dbid]

# Attribute info entry
class AttributeInfoMetaClass(gamemgr.BaseInfoMetaclass):
    def __new__(cls, name, bases, dct):
        newcls = gamemgr.BaseInfoMetaclass.__new__(cls, name, bases, dct)
        
        if isclient:
            # Localize fields 
            if not newcls.displayname:
                newcls.displayname = newcls.name
            if newcls.displayname and newcls.displayname[0] == '#':
                displayname = localize.Find(newcls.displayname)
                newcls.displayname = displayname.encode('ascii') if displayname else newcls.name
                
            # Create description
            for k, v in newcls.dmgmodifiers.iteritems():
                newcls.description += '    Against %s: %s\n' % (k, v.desc)
                
            if newcls.description:
                newcls.description = newcls.name + '\n' + newcls.description
                
            '''
            if newcls.description and newcls.description[0] == '#':
                description = localize.Find(newcls.description)
                if description:
                    newcls.description = description.encode('ascii')
            '''
        return newcls
            
class AttributeInfo(gamemgr.BaseInfo):
    __metaclass__ = AttributeInfoMetaClass
    donotregister = False
    id = dbid
    
    #: Name shown in hud.
    #: In case the name starts with #, it is considered a localized string.
    displayname = StringField(value='', noreset=True)
    
    description = ''

    #: Dictionary with damage modifiers against other attributes.
    dmgmodifiers = {}
    
def ConstantBonusDamage(damage):
    f = lambda dmginfo: dmginfo.AddDamage(damage)
    f.desc = 'Bonus damage %s' % (damage)
    return f
    
def ScaleBonusDamage(scale):
    f = lambda dmginfo: dmginfo.ScaleDamage(scale)
    f.desc = 'Scales damage %d%%' % (scale*100)
    return f
    
# Some base attributes that do nothing, but are used to classify units.
class LightAttributeInfo(AttributeInfo):
    name = 'light'
    
class HeavyAttributeInfo(AttributeInfo):
    name = 'heavy'
    
class CreatureAttributeInfo(AttributeInfo):
    name = 'creature'
    
class SynthAttributeInfo(AttributeInfo):
    name = 'synth'
    
class BuildingAttributeInfo(AttributeInfo):
    name = 'building'

# Test attributes
class RPGAttribute(AttributeInfo):
    name = 'rpg'
    
    dmgmodifiers = { 
        'building' : ConstantBonusDamage(100),
    }
    
class SlashAttribute(AttributeInfo):
    name = 'slash'
    
    dmgmodifiers = { 
        'light' : ConstantBonusDamage(25),
    }
    
class BulletAttribute(AttributeInfo):
    name = 'bullet'
    
    dmgmodifiers = { 
        'light' : ConstantBonusDamage(3),
    }
    
class ShockAttribute(AttributeInfo):
    name = 'shock'
    
    dmgmodifiers = { 
        'heavy' : ConstantBonusDamage(3),
    }