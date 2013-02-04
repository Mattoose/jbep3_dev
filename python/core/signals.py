"""
Core signals.
"""
import srcmgr
from core.dispatch import Signal
from collections import defaultdict

def FireSignalRobust(s, **kwargs):
    responses = s.send_robust(None, **kwargs)
    for r in responses:
        if isinstance(r[1], Exception):
            PrintWarning('Error in receiver %s (module: %s): %s\n' % (r[0], r[0].__module__, r[1]))

class LevelInitSignal(Signal):
    """ Special signal class for levelinit signals.
    
        Takes an additional argument to immediately call if the level is already initialized.
        Convenience.
    """
    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None, callifinit=False):
        super(LevelInitSignal, self).connect(receiver, sender, weak, dispatch_uid)
        if callifinit and srcmgr.levelinit:
            receiver()
            
# The level signals are send from src_python.cpp.
# Send at level initialization before entities are spawned
prelevelinit = LevelInitSignal()
map_prelevelinit = defaultdict(lambda : LevelInitSignal())

# Send at level initialization after entities are spawned
postlevelinit = LevelInitSignal()
map_postlevelinit = defaultdict(lambda : LevelInitSignal())

# Send at level shutdown before entities are removed
prelevelshutdown = Signal()
map_prelevelshutdown = defaultdict(lambda : Signal())

# Send at level shutdown after entities are removed
postlevelshutdown = Signal()
map_postlevelshutdown = defaultdict(lambda : Signal())

if isserver:
    # Send when a new client connected
    clientactive = Signal(providing_args=["client"])
    map_clientactive = defaultdict(lambda : Signal(providing_args=["client"]))
else:
    clientspawned = Signal(providing_args=["client"])
    
    # Fired after changing the config in the keyboard page
    clientconfigchanged = Signal(providing_args=[])
    
# Send when a player changed owner number
playerchangedownernumber = Signal(providing_args=["player", "oldownernumber"])
map_playerchangedownernumber = defaultdict(lambda : Signal(providing_args=["player", "oldownernumber"]))

# Send when the player changes faction
playerchangedfaction = Signal(providing_args=["player", "oldfaction"])

# Gamepackage load/unload
gamepackageloaded = Signal(providing_args=["packagename"])
gamepackageunloaded = Signal(providing_args=["packagename"])

# List of button signals
keyspeed = Signal(providing_args=["player", "state"])
keyduck = Signal(providing_args=["player", "state"])

# Unit/selection/order related signals
pre_orderunits = Signal(providing_args=["player"])
post_orderunits = Signal(providing_args=["player"])
selectionchanged = Signal(providing_args=["player"])

unitselected = Signal(providing_args=["player", "unit"])
unitdeselected = Signal(providing_args=["player", "unit"])

groupchanged = Signal(providing_args=["player", "group"])

if isclient:
    abilitymenuchanged = Signal(providing_args=[])
    refreshhud = Signal(providing_args=[]) # General signal that indicates the units or abilities changed.
    firedping = Signal(providing_args=['pos', 'color']) # A player fired a ping signal on the minimap

# Send when player changes unit control
playercontrolunit = Signal(providing_args=["player", "unit"])
playerleftcontrolunit = Signal(providing_args=["player", "unit"])

if isserver:
    # Fired when the player resources changed (which means resource might be added or removed)
    resourceupdated = Signal(providing_args=['ownernumber', 'type', 'amount'])

    # Fired when the player collected resources. 
    # Examples: control points adds resource or scrap is collected
    # Excludes refunds
    resourcecollected = Signal(providing_args=['ownernumber', 'type', 'amount'])
    
    # Construction of a building started, canceled or finished
    buildingstarted = Signal(providing_args=['building'])
    buildingcanceled = Signal(providing_args=['building'])
    buildingfinished = Signal(providing_args=['building'])
    
    # Unit spawned (any type, always fired on creation)
    unitspawned = Signal(providing_args=['unit'])
    
    # Production of an ability started, canceled or finished at a building factory
    abilitystarted = Signal(providing_args=['building', 'info'])
    abilitycanceled = Signal(providing_args=['building', 'info'])
    abilityfinished = Signal(providing_args=['building', 'info', 'result'])
    
    # On player defeated
    playerdefeated = Signal(providing_args=['ownernumber'])
    
    # Stub
    resourceset = None
else:
    # Fired when the player resources changed
    resourceset = Signal(providing_args=['ownernumber', 'type', 'amount'])
    
# Fired when the nav mesh is loaded
navmeshloaded = Signal(providing_args=[])

'''
# Examples of several signals:
from core.dispatch import receiver

@receiver(prelevelinit)
def on_prelevelinit(sender, **kwargs):
    print "Pre Level init callback!"
    
@receiver(map_prelevelinit['wmp_forest'])
def on_prelevelinit(sender, **kwargs):
    print "Pre Level init callback wmp_forest!"
    
@receiver(postlevelinit)
def on_postlevelinit(sender, bla, **kwargs):
    print "Post Level init callback!"
    
@receiver(prelevelshutdown)
def on_prelevelshutdown(sender, **kwargs):
    print "Pre Level shutdown callback!"
    
@receiver(postlevelshutdown)
def on_postlevelshutdown(sender, **kwargs):
    print "Post Level shutdown callback!"
    
if isserver:
    @receiver(clientactive)
    def on_clientactive(sender, client, **kwargs):
        print "client active %s" % (client)
    
@receiver(playerchangedownernumber)
def on_playerchangedownernumber(sender, player, oldownernumber, **kwargs):
    print "on_playerchangedownernumber %s %s" % (player, oldownernumber)
'''