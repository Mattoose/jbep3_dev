from core.buildings import UnitBaseGarrisonableBuilding, GarrisonableBuildingInfo

#class Bunker(UnitBaseGarrisonableBuilding):
#    pass
    
class BunkerInfo(GarrisonableBuildingInfo):
    name = 'bunker_test'
    modelname = 'models/structures/combine/barracks.mdl'
    health = 500
    attackpriority = 0
    sound_select = 'build_comb_garrison'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius