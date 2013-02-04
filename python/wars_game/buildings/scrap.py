from srcbase import DAMAGE_NO
from vmath import Vector
from core.buildings import UnitBaseBuilding as BaseClass, WarsBuildingInfo
from entities import entity, FOWFLAG_BUILDINGS_NEUTRAL_MASK
from fields import IntegerField
import random

if isserver:
    from core.resources import GiveResources, MessageResourceIndicator
    from entities import CBaseAnimating, CreateEntityByName, DispatchSpawn
else:
    from wars_game.hud import HudBuildScrap
    
@entity('scrap_marker', networked=True,
        studio='models/buildings/build_256_256_96.mdl')
class ScrapMarker(BaseClass):
    """ Scrap marker. Contains scrap. """
    if isserver:
        def Precache(self):
            super(ScrapMarker, self).Precache()
            
            for p in self.big_scrap_models:
                self.PrecacheModel(p)
            for p in self.medium_scrap_models:
                self.PrecacheModel(p)
            for p in self.small_scrap_models:
                self.PrecacheModel(p)
                
        def Spawn(self):
            self.SetUnitType('scrap_marker')
        
            super(ScrapMarker, self).Spawn()
            
            # Spawn random models
            for i in range(0, random.randint(1, 3)):
                self.CreateDummy( {
                    'modelname' : self.medium_scrap_models[random.randint(0, len(self.medium_scrap_models)-1)],
                    'offset' : Vector(random.uniform(-96.0, 96.0), random.uniform(-96.0, 96.0), 0.0),
                } )
            for i in range(0, random.randint(3, 6)):
                self.CreateDummy( {
                    'modelname' : self.small_scrap_models[random.randint(0, len(self.small_scrap_models)-1)],
                    'offset' : Vector(random.uniform(-96.0, 96.0), random.uniform(-96.0, 96.0), 0.0),
                } )
                
            self.scrap = self.totalscrap

            self.takedamage = DAMAGE_NO
            
        def GetScrap(self):
            if not self.scrap:
                return None
            scrap = CreateEntityByName('scrap')
            DispatchSpawn(scrap)
            self.scrap -= 1
            if not self.scrap:
                self.SetThink(self.SUB_Remove, gpGlobals.curtime)
            return scrap
        
    # Show a custom panel when this is the only selected building    
    if isclient:
        # Called when this is the only selected unit
        # Allows the unit panel class to be changed
        def UpdateUnitPanelClass(self):
            self.unitpanelclass = HudBuildScrap
                
                
    fowflags = FOWFLAG_BUILDINGS_NEUTRAL_MASK
    scrap = IntegerField(networked=True)
    totalscrap = IntegerField(value=100, networked=True)
    
    big_scrap_models = [
        "models/combine_apc_destroyed_gib01.mdl",
        "models/props_vehicles/car001a_hatchback.mdl",
        "models/props_vehicles/car001b_hatchback.mdl",
        "models/props_vehicles/car002a.mdl",
        "models/props_vehicles/car002b.mdl",
        "models/props_vehicles/car003a.mdl",
        "models/props_vehicles/car003b.mdl",
        "models/props_vehicles/car004a.mdl",
        "models/props_vehicles/car004b.mdl",
        "models/props_vehicles/generatortrailer01.mdl",
    ]

    medium_scrap_models = [
        "models/props_c17/FurnitureBathtub001a.mdl",
        "models/props_c17/FurnitureCouch001a.mdl",
        "models/props_c17/substation_circuitbreaker01a.mdl",
        "models/props_c17/substation_transformer01d.mdl",
        "models/props_c17/TrapPropeller_Engine.mdl",
        "models/props_canal/boat002b.mdl",
        #"models/props_canal/winch002.mdl", ?
        "models/props_citizen_tech/windmill_blade002a.mdl",
        "models/props_citizen_tech/windmill_blade004a.mdl",
        "models/props_combine/Cell_01_pod_cheap.mdl",
        "models/props_combine/headcrabcannister01b.mdl",
        "models/props_combine/plazafallingmonitor.mdl",
        "models/props_wasteland/laundry_dryer001.mdl",
        "models/props_wasteland/laundry_dryer002.mdl",
        "models/props_wasteland/prison_bedframe001a.mdl",
        "models/props_c17/oildrum001.mdl",
    ]

    small_scrap_models = [
        "models/items/item_item_crate.mdl",
        "models/props_c17/canister01a.mdl",
        "models/props_c17/canister02a.mdl",
        "models/props_c17/canister_propane01a.mdl",
        "models/props_c17/metalPot001a.mdl",
        "models/props_c17/pulleywheels_large01.mdl",
        "models/props_interiors/SinkKitchen01a.mdl",
        "models/props_junk/gascan001a.mdl",
        "models/props_junk/MetalBucket01a.mdl",
        "models/props_junk/PlasticCrate01a.mdl",
        "models/props_junk/PropaneCanister001a.mdl",
        "models/props_junk/MetalBucket02a.mdl",
        "models/props_junk/TrafficCone001a.mdl",
        "models/props_junk/bicycle01a.mdl",
        "models/props_lab/monitor01a.mdl",
        "models/props_lab/monitor02.mdl",
        "models/props_wasteland/controlroom_monitor001a.mdl",
    ]

class ScrapMarkerInfo(WarsBuildingInfo):
    name        = "scrap_marker"
    cls_name    = "scrap_marker"
    image_name = "vgui/units/unit_shotgun.vmt"
    #modelname = 'models/buildings/build_256_256_96.mdl'
    modellist = ScrapMarker.big_scrap_models
    displayname = "#ScrapMarker_Name"
    description = "#ScrapMarker_Description"
 
if isserver:
    @entity('scrap')
    class Scrap(CBaseAnimating):
        def Precache(self):
            self.PrecacheModel(self.modelname)
            super(Scrap, self).Precache()
            
        def Spawn(self):
            self.Precache()
            self.SetModel(self.modelname)
            super(Scrap, self).Spawn()
            
        def AddResourcesAndRemove(self, ownernumber):
            MessageResourceIndicator(self.GetOwnerEntity().GetOwnerNumber(), self.GetAbsOrigin(), 'Scrap +1')
            GiveResources(ownernumber, [('scrap', 1)], firecollected=True)
            self.Remove()
            
        modelname = 'models/lamarr.mdl'
