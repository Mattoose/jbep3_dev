"""
The following methods are related to game packages
The can insert factions, load entities, etc
"""
import sys, os
import traceback
import srcmgr
from kvdict import LoadFileIntoDictionaries, kv2dict
# from srcbase import KeyValuesDumpAsDevMsg
from collections import defaultdict
import inspect
from fields import SetupClassFields, GetAllFields

from core.dispatch import receiver
from core.signals import prelevelinit, prelevelshutdown, gamepackageloaded, gamepackageunloaded
from core.usermessages import usermessage, usermessage_shared
from gamerules import GameRules
from particles import ShouldLoadSheets, ReadParticleConfigFile, DecommitTempMemory
from entities import GetAllClassnames, GetClassByClassname

# Server specific
if isserver:
    from entities import gEntList, RespawnPlayer
    from utils import UTIL_IsCommandIssuedByServerAdmin, UTIL_Remove, UTIL_GetPlayers
    from gameinterface import CReliableBroadcastRecipientFilter, CSingleUserRecipientFilter, concommand, FCVAR_CHEAT, AutoCompletion

# Store
dbgamepackages      = {}

#
# Level init
#
if isserver:
    @receiver(prelevelinit)
    def LevelInit(sender, **kwargs):
        # Load and add the res file (containing information about the map)
        resfilename = 'maps/%s.res' % (srcmgr.levelname)
        values = LoadFileIntoDictionaries(resfilename)
        if values and values.get(srcmgr.levelname, None):
            values = values.get(srcmgr.levelname, None)

            AddToDownloadables(resfilename)

            # Add the minimap material
            minimap_material = values.get('minimap_material', None)
            if minimap_material:
                # Todo: Check if missing?
                AddToDownloadables('materials/%s.vmt' % (minimap_material))
                AddToDownloadables('materials/%s.vtf' % (minimap_material))

@receiver(prelevelshutdown)
def LevelShutdown(sender, **kwargs):
    # Clear all techinfo
#    from core.abilities.info import dbid
#    for name, pkg in dbgamepackages.iteritems():
#        for abi_name, abi in pkg.db[dbid].iteritems():
#            abi.techinfo.clear()
            
    # Use level shutdown to purge all loaded packages on the client 
    if isclient:
        packages = set(dbgamepackages.keys())
        done = set()
        for name in packages:
            if dbgamepackages[name].loaded:
                done |= UnLoadGamePackage(name)
    
#
# DB's
#
dblist = defaultdict( lambda : {} )

# BaseInfoMetaclass registers the class        
class BaseInfoMetaclass(type):
    def __new__(cls, name, bases, dct):
        # Create the new cls
        newcls = type.__new__(cls, name, bases, dct)
        
        # Parse fields
        SetupClassFields(newcls)
        
        # Auto generate name if specified
        if 'name' not in dct and newcls.autogenname:
            newcls.name = '%s__%s' % (newcls.__module__, newcls.__name__)
        
        # If no mod name is give, but we do have a name, then use the newcls module as modname
        if not newcls.modname and newcls.name:
            newcls.modname = newcls.__module__
        
        # Might be a 'fallback' info object that is not registered
        if newcls.modname != None and not newcls.donotregister:
            modname = newcls.modname.split('.')[0]
            
            # Add to our gamepackage for loading/unloading
            # Overwrite old one
            dbgamepackages[modname].db[newcls.id][newcls.name] = newcls
            
            # Add to the active list if our gamepackage is loaded   
            if dbgamepackages[modname].loaded:
                dblist[newcls.id][newcls.name] = newcls
                newcls.OnLoaded()  
        return newcls
        
class BaseInfo(object):
    """ Base object for registering units, abilities, gamerules, etc
        into a game package. """
    __metaclass__ = BaseInfoMetaclass
    
    donotregister = True
    id = None
    modname = None
    name = ""
    autogenname = False
    
    # Default method implementations
    @classmethod 
    def OnLoaded(info):
        pass
    @classmethod 
    def OnUnLoaded(info):
        pass

# Build list of available game packages
def BuildGamePackageList():
    # TODO: Make a better system to detect game packages.
    for d in os.listdir('python/'):
        fullpath = os.path.join('python/', d)
        if not os.path.isdir(fullpath):
            continue
        # Core is a special case right now
        if d == 'core':
            RegisterGamePackage(name='core')  
        try:
            __import__(d)
        except:
            continue
#
# Loading/unloading game packages
#    
def LoadGamePackage(package_name, informclient=True):
    """ Load a game package (a set of units, abilities, gamerules, etc). """
    # Check if the package is already loaded
    try:
        if dbgamepackages[package_name].loaded:
            return
    except KeyError:
        pass    # Clearly not loaded
        
    # Now load
    try:
        # Import the package
        __import__( package_name )
        
        # Read particle files (once only, annoyingly slow on reloading a package. TODO: Make it an option)
        particles = dbgamepackages[package_name].particles
        if particles and not dbgamepackages[package_name].loadedonce:
            #ShouldLoadSheets(isclient)
            map(lambda p: ReadParticleConfigFile(p), particles) 
            DecommitTempMemory()
            
        # Load dependencies
        for d in dbgamepackages[package_name].dependencies:
            LoadGamePackage(d, False)
        
        # Import everything that must be registered from within the module
        if hasattr(sys.modules[package_name], 'LoadGame'):
            sys.modules[package_name].LoadGame()
        
        # Add abilities/factions/units from the db's
        for k, v in dbgamepackages[package_name].db.iteritems():
            for k2, info in v.iteritems():
                dblist[k][info.name] = info
                info.OnLoaded()        
        
        # Now say we are loaded
        dbgamepackages[package_name].loaded = True
        dbgamepackages[package_name].loadedonce = True
    except ImportError:
        PrintWarning('Failed to load game package %s\n' % (package_name))
        traceback.print_exc()
        return
        
    # Change callbacks
    responses = gamepackageloaded.send_robust(None, packagename=package_name)
    for r in responses:
        if isinstance(r[1], Exception):
            PrintWarning('Error in receiver %s (module: %s): %s\n' % (r[0], r[0].__module__, r[1]))
        
    # Inform clients
    if isserver and informclient and srcmgr.levelinit == True:
        if dbgamepackages[package_name].isserveronly:
            filter = CReliableBroadcastRecipientFilter()
            SendGamePackage(filter, package_name)
        else:
            ClientLoadPackage(package_name)

def UnLoadGamePackage(package_name, informclient=True):
    """ Unloads a game package. This means all the units, 
        abilities, gamerules, etc will not show up anymore.
        It does not delete the references or anything. """
    additional_unloads = set()
    # Check if the package is already not loaded
    try:
        if dbgamepackages[package_name].loaded == False:
            PrintWarning( 'Game package %s is not loaded\n' % (package_name))
            return additional_unloads
    except KeyError:
        PrintWarning( 'Game package %s is not loaded\n' % (package_name))
        return additional_unloads # Doesn't exist, so not loaded
        
    # Unload dependencies
    for gp in dbgamepackages.keys():
        if gp == package_name:
            continue
        if dbgamepackages[gp].loaded and package_name in dbgamepackages[gp].dependencies:
            additional_unloads.add(gp)
            additional_unloads |= UnLoadGamePackage(gp, False)  
        
    # Unload
    try:
        for k, v in dbgamepackages[package_name].db.iteritems():
            # Remove abilities/factions/units from the db's
            for k2, info in v.iteritems():
                info.OnUnLoaded()
                del dblist[k][info.name]

        # Call unload method
        if isserver or not dbgamepackages[package_name].isserveronly:
            if hasattr(sys.modules[package_name], 'UnloadGame'):
                sys.modules[package_name].UnloadGame()
        dbgamepackages[package_name].loaded = False
    except:
        PrintWarning('Failed to unload game package %s\n' % (package_name))
        traceback.print_exc()  
        
    # Dispatch callbacks
    responses = gamepackageunloaded.send_robust(None, packagename=package_name)
    for r in responses:
        if isinstance(r[1], Exception):
            PrintWarning('Error in receiver %s (module: %s): %s\n' % (r[0], r[0].__module__, r[1]))
            
    # Inform clients
    if isserver and informclient and srcmgr.levelinit == True:
        ClientUnloadPackage(package_name)
    return additional_unloads
    
def GetDependencies(package_name): 
    dependencies = set()
    for gp in dbgamepackages.keys():
        if gp == package_name:
            continue
        if package_name in dbgamepackages[gp].dependencies:
            dependencies.add(gp)
            dependencies |= GetDependencies(gp)  
    return dependencies
    
def ReLoadGamePackageInternal(package_name):
    # Unload myself (also unloads the dependencies)
    loaded = dbgamepackages[package_name].loaded
    loadedonce = dbgamepackages[package_name].loadedonce
    #if not loaded:
        # Load to ensure the modules are registered
    #    LoadGamePackage(package_name, False)

    loadeddep = UnLoadGamePackage(package_name, False)
    deps = GetDependencies(package_name)
    
    # Reload myself
    try:
        reload(sys.modules[package_name])
        dbgamepackages[package_name].loadedonce = loadedonce
        if hasattr(sys.modules[package_name], 'LoadGame'): # Call load game to ensure registering the modules
            sys.modules[package_name].LoadGame()
        if hasattr(sys.modules[package_name], 'UnloadGame'): # Call unload in case in expects that after a load
            sys.modules[package_name].UnloadGame()
            
        if hasattr(sys.modules[package_name], 'ReloadGame'):
            sys.modules[package_name].ReloadGame()
    except:
        PrintWarning("Failed to reload game package %s\n" % (package_name))
        raise   
        
    # Reload dependencies
    for gp in deps:
        if not dbgamepackages[gp].loadedonce:
            continue
        ReLoadGamePackageInternal(gp)
        
    # Load this package
    if loaded:
        LoadGamePackage(package_name)
        # Load the deps that were loaded
        for gp in loadeddep:
            LoadGamePackage(gp)

def ReLoadGamePackage(package_name):
    """ For developing. NOTE: it only reloads the package partly and is maintained manually """
    deps = GetDependencies(package_name)
    
    active_gamerules = None
    oldtechnodes = []
    #from core.abilities import GetTechNode
    from entities import CBasePlayer
    
    # The following could fail if one of the shutdown functions contains an error.
    # Reload regardless if this fails!
    try:
        # Get ref to all old tech nodes
        for name, info in dblist['abilities'].iteritems():
            oldtechnodes.append(info.techinfo)
            
        # In case the package we are reloading is not loaded yet, load it and keep it loaded (for convenience).
        if not dbgamepackages[package_name].loaded:
            LoadGamePackage(package_name, False)
        
        # Make sure the gamepackage + dependencies were at least one time loaded
        for gp in deps:
            if not dbgamepackages[gp].loadedonce:
                continue
            if not dbgamepackages[gp].loaded:
                LoadGamePackage(gp, False)
                UnLoadGamePackage(gp, False)
                
        # If the current amerules is in one of the packages of the dependencies, then clear gamerules
        from core.gamerules import ClearGamerules, SetGamerules
        if GameRules():
            try:
                modname = dblist['gamerules'][GameRules().info.name].modname.split('.')[0]
                if modname in deps or modname == package_name:
                    active_gamerules = GameRules().info.name
                    ClearGamerules()
            except KeyError:    # Might happen after a failed reload. Remember active gamerules after a failed reload? Otherwise we have no gamerules.
                pass
                
        # Make sure the hud is destroyed
        if isclient:
            from core.factions import DestroyHud
            DestroyHud()
    except:
        traceback.print_exc()
            
    # Do the reloading
    ReLoadGamePackageInternal(package_name)
    
    # Inform clients ( before reactivating the gamerules, because the gamerules sends a message to the client )
    if isserver and not dbgamepackages[package_name].isserveronly and srcmgr.levelinit == True:
        ClientReloadPackage(package_name)
        
    # Reactivate the gamerules if it was loaded
    if isserver and active_gamerules != None:
        SetGamerules(active_gamerules)
        
    # Figure out if the player class entity got reloaded. In that case we should respawn the player.
    if isserver:
        for player in UTIL_GetPlayers():
            RespawnPlayer(player, player.GetClassname())
                
    '''
    # TODO: Restore all tech
    for otninfo in oldtechnodes:
        for o, otn in otninfo.iteritems():
            tn = GetTechNode(otn.name, o)
            if not tn:
               continue
            tn.available = otn.available
            tn.techenabled = otn.techenabled
            tn.showonunavailable = otn.showonunavailable
            tn.successorability = otn.successorability
    '''
    
    # Restore hud
    #if isclient:
        #from core.factions import CreateHud
        #CreateHud(CBasePlayer.GetLocalPlayer().GetFaction())
        
class GamePackageInfo(object):
    """ Stores info about a game package """
    def __init__(self, name, dependencies=[], particles=[], isserveronly=False):
        super(GamePackageInfo, self).__init__()
        self.name = name
        self.dependencies = dependencies
        self.particles = particles
        self.loaded = False
        self.loadedonce = False # Used for determing if we need to reload (dev only)
        self.db = defaultdict(lambda : {})
        self.isserveronly = isserveronly
        
#        
# Register methods  
#    
def RegisterGamePackage(name, 
                        dependencies=[],
                        particles=None):
    """ Register a new game package.
        Call this in the __init__.py of your new game package.
        
        In your __init__.py you must implement the following methods:
        LoadGamePackage() 
        UnloadGamePackage()
        ReloadGamePackage()
        
        Your gamepackage is imported on both the client and server side.
    """
    dbgamepackages[name] = GamePackageInfo(name=name, 
                                           dependencies=list(dependencies),
                                           particles=particles)

if isserver:
    def RegisterServerOnlyGamePackage(name, 
                            dependencies=[],
                            particles=None):
        """ Register a new server side only game package.
            Works the same as RegisterGamePackage, except
            it is only imported on the server side. It will
            automatically send all definitions to the client 
            on load (restricted to fields only).
        """
        dbgamepackages[name] = GamePackageInfo(name=name, 
                                               dependencies=list(dependencies),
                                               particles=particles,
                                               isserveronly=True)

# Methods for sending the required info of a game package to the client
# TODO: Could consider splitting this from the gamemgr module?
if isserver:
    def FindBaseClass(info, skippackagename):
        if not info.modname:
            modname = info.__module__.split('.')[0]
        else:
            modname = info.modname.split('.')[0]
            
        if modname in dbgamepackages.keys():
            if not dbgamepackages[modname].isserveronly:
                return info
        elif modname != skippackagename:
            return info
            
        if not info.__bases__:
            return None
        return FindBaseClass(info.__bases__[0], skippackagename)
            
    def SendGamePackage(filter, package_name):
        # First send a message to create a new package
        CreateGamePackage(package_name, filter=filter)
        
        # Send all required unit, ability and gamerules definitions
        for k, v in dbgamepackages[package_name].db.iteritems():
            # Only send abilities and gamerules
            # NOTE: units are also abilities, so they are also send.
            if k not in ('gamerules', 'abilities'):
                continue
            for name, info in v.iteritems():
                # Start a new definition
                StartNewDefinition(name, filter=filter)
                
                #print 'sending %s' % (info)
                # Just send all fields for now
                for field in GetAllFields(info):
                    ModifyDefinition(field.name, field.default, filter=filter)
                
                # Finalize definition
                baseclass = FindBaseClass(info, package_name)
                FinalizeDefinition(package_name, baseclass.__module__, baseclass.__name__, filter=filter)
                
        # This will load the package on the client
        FinalizeGamePackage(package_name, filter=filter)

@usermessage()
def CreateGamePackage(package_name, **kwargs):
    dbgamepackages[package_name] = GamePackageInfo(name=package_name, 
                               dependencies=list(),
                               isserveronly=True)

@usermessage()
def FinalizeGamePackage(package_name, **kwargs):
    # Add abilities/factions/units from the db's
    for k, v in dbgamepackages[package_name].db.iteritems():
        for k2, info in v.iteritems():
            dblist[k][info.name] = info
            info.OnLoaded()        

    dbgamepackages[package_name].loaded = True
    dbgamepackages[package_name].loadedonce = True
    
    # Dispatch signal
    responses = gamepackageloaded.send_robust(None, packagename=package_name)
    for r in responses:
        if isinstance(r[1], Exception):
            PrintWarning('Error in receiver %s (module: %s): %s\n' % (r[0], r[0].__module__, r[1]))

definition = None

@usermessage()
def StartNewDefinition(name, **kwargs):
    global definition
    definition = {}
    definition['name'] = name
    
@usermessage()
def ModifyDefinition(name, value, **kwargs):
    global definition
    definition[name] = value
    
@usermessage()
def FinalizeDefinition(package_name, module, baseclassname, **kwargs):
    global definition
    mod = __import__(module)
    baseclass = getattr(sys.modules[module], baseclassname)
    
    class NewDefinition(baseclass):
        modname = package_name
        
        class __metaclass__(baseclass.__metaclass__):
            def __new__(cls, name, bases, dct):
                dct.update(definition)
                return baseclass.__metaclass__.__new__(cls, name, bases, dct)

                    
#
# Methods for making the client load the game packages
#
@usermessage()
def ClientLoadPackage(packagename, **kwargs):
    LoadGamePackage(packagename)
@usermessage()
def ClientUnloadPackage(packagename, **kwargs):
    UnLoadGamePackage(packagename)
@usermessage()
def ClientReloadPackage(packagename, **kwargs):
    ReLoadGamePackage(packagename)
    
@usermessage_shared()
def ReloadParticlesPackage(package_name, **kwargs):
    particles = dbgamepackages[package_name].particles
    if particles:
        #ShouldLoadSheets(isclient)
        map(lambda p: ReadParticleConfigFile(p), particles) 
        DecommitTempMemory()
    else:
        PrintWarning("No particles for game package %s\n" % (package_name))

if isserver:
    def _ClientActive(player):
        """ Inform client about all packages that need to be imported """  
        filter = CSingleUserRecipientFilter(player)
        filter.MakeReliable()
        for package in dbgamepackages.itervalues():
            if package.loaded:
                ClientLoadPackage(package.name, filter=filter)
                
    def _ApplyGameSettings(kv):
        settings = kv
        
        for name, package in dbgamepackages.iteritems():
            if package.loaded:
                try: 
                    ApplyGameSettings = sys.modules[name].ApplyGameSettings
                except AttributeError:
                    continue
                if ApplyGameSettings(settings):
                    return True
                
        return False

#        
# The commands to load and unload a game package
#
if isserver:
    @concommand('load_gamepackage', 'Load a game package')
    def cc_load_gamepackage(args):
        if not UTIL_IsCommandIssuedByServerAdmin():
            return
        LoadGamePackage(args[1])

    @concommand('unload_gamepackage', 'Unload a game package')
    def cc_unload_gamepackage(args):
        if not UTIL_IsCommandIssuedByServerAdmin():
            return
        UnLoadGamePackage(args[1])
    
    @concommand('reload_gamepackage', 'Reload a game package')
    def cc_reload_gamepackage(args):
        if not UTIL_IsCommandIssuedByServerAdmin():
            return
        ReLoadGamePackage(args[1])
        
    @concommand('reload_gamepackage_particles', 'Reload particle systems of package')
    def cc_reload_gamepackage_particles(args):
        if not UTIL_IsCommandIssuedByServerAdmin():
            return
        ReloadParticlesPackage(args[1])
        
    
# Useful game package related commands
if isserver:
    def GetClassesForGamepackage(packagename):
        entities = GetAllClassnames()
        classes = set()
        
        for clsname in entities:
            cls = GetClassByClassname(clsname)
            if not cls:
                continue
                
            modname = cls.__module__.split('.')[0]
            
            if modname != packagename:
                continue
            
            classes.add(clsname)
        
        return classes

    @concommand('wars_pkg_remove_ents_all', 'Removes all units on the map belonging to the specified game package', FCVAR_CHEAT,
                completionfunc=AutoCompletion(lambda: dbgamepackages.keys()))
    def cc_wars_pkg_remove_ents_all(args):
        """ Removes all entities belonging to the specified game package.
        """
        if len(args) < 2:
            print("Removes all entities of the specified type\n\tArguments:   {entity_name} / {class_name}")
        else:
            # Build list of classnames
            for i in range(1, len(args)): 
                try:
                    pkg = dbgamepackages[args[i]]
                except KeyError:
                    print('Invalid package name %s' % (args[i]))
                    continue

                classes = set()
                for info in pkg.db['units'].itervalues():
                    classes.add(info.cls_name)

                # Now iterate all entities and remove
                # Otherwise remove based on name or classname
                count = 0
                ent = gEntList.FirstEnt()
                while ent != None:
                    if ent.GetClassname() in classes:
                        UTIL_Remove(ent)
                        count += 1
                    ent = gEntList.NextEnt(ent)
                    
                if count:
                    print("Removed %d entities from classes of game package %s\n" % (count, args[1]))
                else:
                    print("No entities for game package %s found.\n" % (args[1]))
                    
    @concommand('wars_print_registered', 'Prints registered things', FCVAR_CHEAT,
                completionfunc=AutoCompletion(lambda: dblist.keys()))
    def cc_wars_print_registered(args):
        try:
            component = args[1]
        except IndexError:
            print('Invalid component')
            return
            
        if component not in dblist:
            print('Invalid component %s' % (component))
            return
        register = dblist[component]
        
        for k, v in register.iteritems():
            sourcelines, startlinenumber = inspect.getsourcelines(v)
            print('Name: %s' % (k))
            print('\t%s' % (inspect.getsourcefile(v)))
            print('\t%s: %s' % (startlinenumber, sourcelines[0].rstrip()))
            print('')

# Build game package list on import
BuildGamePackageList()
