from core.abilities import AbilitySwitchWeapon, AbilityUpgrade

# Unlock upgrades for ar2 and sg weapons
class WeaponAr2Unlock(AbilityUpgrade):
    name = 'weaponar2_unlock'
    displayname = '#WeaponAr2Unlock_Name'
    description = '#WeaponAr2Unlock_Description'
    image_name = "vgui/abilities/weaponar2_unlock"
    buildtime = 120.0
    costs = [[('kills', 5)], [('requisition', 5)]]
    
class WeaponSGUnlock(AbilityUpgrade):
    name = 'weaponsg_unlock'
    displayname = '#WeaponSGUnlock_Name'
    description = '#WeaponSGUnlock_Description'
    image_name = "vgui/abilities/weaponsg_unlock"
    buildtime = 120.0
    costs = [[('kills', 5)], [('requisition', 5)]]

# Switch abilities that require the above abilities
class WeaponSwitchAr2Info(AbilitySwitchWeapon):
    name = 'weaponswitch_ar2'
    displayname = '#WeaponAR2Switch_Name'
    description = '#WeaponAR2Switch_Description'
    image_name = 'vgui/abilities/weaponswitch_ar2'
    weapon = 'weapon_ar2'
    #techrequirements = ['weaponar2_unlock']
  
class WeaponSwitchSGInfo(AbilitySwitchWeapon):
    name = 'weaponswitch_shotgun'
    displayname = '#WeaponSGSwitch_Name'
    description = '#WeaponSGSwitch_Description'
    image_name = 'vgui/abilities/weaponswitch_shotgun'
    weapon = 'weapon_shotgun'
    #techrequirements = ['weaponsg_unlock']
    
