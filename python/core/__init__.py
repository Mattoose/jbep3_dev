import signals

# FIXME: Register inside gamemgr for now.
#from gamemgr import RegisterGamePackage
#RegisterGamePackage(
#        name=__name__
#)  

def LoadGame():
#    import attributes
#    import abilities
#    import factions
#    import weapons
#    import units
#    import buildings
#    if isserver: import strategicai
    import gamerules
#    import ents
#    import util
#    import hud
#    import ui
        
def UnloadGame():  
    pass 
    
def ReloadGame():
    from gamemgr import RegisterGamePackage
    RegisterGamePackage(name=__name__)

    LoadGame()
    
    # Attributes
#    reload(attributes)
#    
#    # Reload abilities
#    reload(abilities.info)
#    reload(abilities.base)
#    reload(abilities.menu)
#    reload(abilities.instant)
#    reload(abilities.cancel)
#    reload(abilities.mouseoverride)
#    reload(abilities.target)
#    reload(abilities.placeobject)
#    reload(abilities.upgrade)
#    reload(abilities.unittransform)
#    reload(abilities.attackmove)
#    reload(abilities.holdposition)
#    reload(abilities.switchweapon)
#    reload(abilities.ungarrisonall)
#    reload(abilities.debugnavdist)
#    reload(abilities)
#    
#    # Factions
#    reload(factions)
#    
#    # Temp, needs fix for:
#    #   units.base imports from hud.units
#    if isclient:
#        reload(hud.info)
#        reload(hud.abilitybutton)
#        reload(hud.infobox)
#        reload(hud.units)
#    reload(hud)
#    if isclient:
#        reload(ui.scorescreen)
#        reload(ui.winlosedialog)
#        reload(ui.resourcesdialog)
#    reload(ui)
#        
#    # Reload units
#    reload(units.info)
#    reload(units.base)
#    
#    reload(units.orders)
#    reload(units.hull )
#    reload(units.animstate)
#    reload(units.locomotion)
#    if isserver:
#        reload(units.navigator_shared)
#        reload(units.navigator)
#        reload(units.senses)
#        reload(units.intention)
#        reload(units.behavior_generic)
#        reload(units.behavior_overrun)
#    reload(units.basecombat)
#    reload(units.basehuman)
#    reload(units)
#    
#    # Reload weapons
#    reload(weapons.base)
#    reload(weapons.base_machinegun)
#    reload(weapons.base_melee)
#    reload(weapons)
#    
#    # Ents
#    if isserver:
#        reload(ents.unitmaker)
#    reload(ents.homingprojectile)
#    reload(ents.event_building_listener)
#    reload(ents.filters)
#    reload(ents.giveresources)
#    reload(ents)
#    
#    # Reload hud parts
#    if isclient:
#        #reload(hud.info)
#        #reload(hud.abilitybutton)
#        reload(hud.notifier)
#        reload(hud.rallyline)
#        #reload(hud.infobox)
#        reload(hud.groups)
#        reload(hud.resourceindicator)
#        reload(hud.abilities)
#        reload(hud.buildings)
#        reload(hud.minimap)
#        #reload(hud.units) # Already reloaded above, needs fix.
#        reload(hud.portrait)
#        reload(hud.player_names)
#        reload(hud.cunit_display)
#        reload(hud.sandbox)
#        reload(hud)
#    else:
#        reload(hud)
#
#    # Reload gamerules
    reload(gamerules.info)
    reload(gamerules.base)
    reload(gamerules.sandbox)
    reload(gamerules)
#    
#    # Reload buildings
#    reload(buildings.base)
#    reload(buildings.dummy)
#    reload(buildings.basefactory)
#    reload(buildings.func)
#    reload(buildings.baseturret)
#    reload(buildings.baseautoturret)
#    reload(buildings.basemountableturret)
#    reload(buildings.basegarrisonable)
#    reload(buildings)
#    
#    # Stratic ai
#    if isserver:
#        reload(strategicai.groups)
#        reload(strategicai.abilityrules)
#        reload(strategicai.base)
#        reload(strategicai.info)
#        reload(strategicai)
#
#    # Reload util
#    if isserver:
#        reload(util.techtree2dot)
#        reload(util.genfgd)
#    else:
#        reload(util.genimagestub)
#        reload(util.genstats)
#    reload(util)
