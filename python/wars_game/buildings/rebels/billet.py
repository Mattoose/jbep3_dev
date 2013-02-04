from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity

@entity('build_reb_billet', networked=True)
class RebelsBillet(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -350, 32)    
    
# Register unit
class BilletInfo(WarsBuildingInfo):
    name = "build_reb_billet" 
    cls_name = "build_reb_billet"
    displayname = '#BuildRebBillet_Name'
    description = '#BuildRebBillet_Description'
    image_name  = 'vgui/rebels/buildings/build_reb_billet'
    modelname = 'models/structures/resistance/billet.mdl'
    costs = [('requisition', 2)]
    health = 200
    buildtime = 25.0
    population = 0 # Billet itself does not take population
    providespopulation = 8
    abilities   = {
        8 : 'cancel',
    }
    sound_select = 'build_reb_billet'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_population'])