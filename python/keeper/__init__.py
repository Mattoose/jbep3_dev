from gamemgr import RegisterGamePackage, LoadGamePackage, UnLoadGamePackage
from srcmgr import ImportSubMods, ReloadSubMods
from core.dispatch import receiver
from core.signals import postlevelinit
from core.gamerules import SetGamerules
from core.factions import FactionInfo
from gameinterface import concommand, engine, FCVAR_CHEAT

if isserver:
    from core.signals import clientactive

RegisterGamePackage(
        name=__name__,
        dependencies=['core'],
)  

def LoadFactions():
    class FactionKeeperInfo(FactionInfo):
        name = 'keeper'
        displayname = 'Keeper'
        hud_name = 'keeper_hud'
        startbuilding = ''
        startunit = 'unit_imp'
        resources = []
        
def LoadGame():
    import signals
    import common
    import light
    import taskqueue
    import player
    import levelloader
    
    import blockhovereffect
    import block
    import tiles
    
    import rooms
    import rooms.createroom
    import rooms.lair
    import rooms.treasureroom
    import rooms.hatchery
    import rooms.training
    
    import keeperworld
    import pickupableobject
    import gold
    import game

    import portal
    import heart
 
    import units
    import units.basekeeper
    if isserver:
        import units.behavior
    import units.imp
    import units.parasite
    import units.drone
    import units.buzzer
    import units.grub
    import units.marine
    
    import spells
    ImportSubMods(spells)
    
    if isclient:
        import hud
        ImportSubMods(hud)
    
    gold.LoadDKResources()
    LoadFactions()
        
def ReloadGame():
    LoadGame()
    
    print('Reloading keeper package (client: %s)' % (str(isclient)))
    
    import keeperworld
    currentlevel = keeperworld.lastlevel

    reload(signals)
    reload(common)
    reload(light)
    reload(taskqueue)
    reload(player)
    reload(levelloader)
    
    # Blocks, tiles and rooms
    reload(tiles)
    reload(blockhovereffect)
    reload(block)
    
    reload(rooms.createroom)
    reload(rooms.lair)
    reload(rooms.treasureroom)
    reload(rooms.hatchery)
    reload(rooms.training)
    reload(rooms)
    
    # The world and gamerules
    reload(keeperworld)
    reload(game)
    
    reload(pickupableobject)
    reload(gold)
    reload(portal)
    reload(heart)
    
    # Minions
    if isserver:
        reload(units.behavior)
    reload(units.basekeeper)
    reload(units.imp)
    reload(units.parasite)
    reload(units.drone)
    reload(units.buzzer)
    reload(units.marine)
    reload(units.grub)
    reload(units)

    # Spells
    ReloadSubMods(spells)
    reload(spells)
    
    # Interface
    if isclient:
        ReloadSubMods(hud)
        
    LoadFactions()
    
    if currentlevel:
        import keeperworld
        keeperworld.nextlevel = currentlevel
        print('Setting keeperworld back to current level %s' % (currentlevel))
    
if isserver:
    @receiver(postlevelinit)
    def PostLevelInit(sender, **kwargs):
        import srcmgr
        if srcmgr.levelname.startswith('dk_'):
            LoadGamePackage('keeper')
            SetGamerules('keeper')
        else:
            UnLoadGamePackage('keeper')
    
    @receiver(clientactive)
    def ClientActive(sender, client, **kwargs):
        import srcmgr
        if srcmgr.levelname.startswith('dk_'):
            client.ChangeFaction('keeper')
            
    def ApplyGameSettings(settings):
        game = settings['game'][0]
        mode = game['mode'][0]
        map = settings['map'][0]
        
        mapcommand = map['mapcommand'][0]
        
        if mode == 'swarmkeeper':
            mission = game['mission'][0]
            
            import keeperworld
            keeperworld.nextlevel = mission
            
            engine.ServerCommand('%s dk_map reserved\n' % (mapcommand))
            
            return True

    @concommand('sk_loadmap', flags=0)#flags=FCVAR_CHEAT)
    def SKLoadMap(args):
        import keeperworld
        keeperworld.nextlevel = args.ArgS()
        print('sk_loadmap: Loading %s' % (keeperworld.nextlevel))
        engine.ServerCommand('map dk_map\n')
