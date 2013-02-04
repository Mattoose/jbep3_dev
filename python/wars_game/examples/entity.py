from entities import CBaseEntity, entity, CreateEntityByName, DispatchSpawn

# Before each entity class you must use the entity decorator
# This will link the class to an entity name
@entity('test_entity')
class ExampleEnt( CBaseEntity ):
    def __init__(self):
        super(ExampleEnt, self).__init__()
        print('Custom entity created in python!')
    
    def Spawn(self):
        """ Called after the keyvalues are applied. Most of the initialization code should be added here. """    
        super(ExampleEnt, self).Spawn()

    def UpdateOnRemove(self):
        """ Called when the entity is about to be removed. Add your cleanup code here """    
        super(ExampleEnt, self).UpdateOnRemove()
     
    @staticmethod    
    def InitEntityClass(cls):
        """ A special method for python entities. This is called in two cases
            1. When the Entity factory is created
            2. When the map changes
            This function can be used to initialize static data that only needs to be defined once per level.
            For example animation events change on map change and need to be reinitialized. """   
        pass 

# Spawn one entity using the name to which the class is linked
# The entity will be added to a global list. As long as the entity is in that list, the entity is alive
# To remove the entity use: ent.Remove() or utils.UTIL_Remove(ent)
# To completely destroy the entity the reference count to the entity must be zero, so don't create references everywhere
ent = CreateEntityByName("test_entity")
DispatchSpawn(ent)
ent.Activate() 
