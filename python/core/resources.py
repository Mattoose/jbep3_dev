""" Resource management WARS game """
from collections import defaultdict
import copy

from srcbase import RegisterTickMethod, UnregisterTickMethod
from core.dispatch import receiver
from core.signals import prelevelinit, postlevelinit, postlevelshutdown, playerchangedownernumber, FireSignalRobust
from core.usermessages import usermessage
from utils import UTIL_ListPlayersForOwnerNumber

if isserver:
    from core.usermessages import SendUserMessage, CRecipientFilter, CSingleUserRecipientFilter
    from utils import UTIL_PlayerByIndex, UTIL_GetCommandClient
    from gameinterface import concommand, FCVAR_CHEAT, AutoCompletion
    from entities import gEntList
    from core.signals import clientactive, resourceupdated, resourcecollected
else:
    from core.signals import resourceset
    
resources = defaultdict(lambda : defaultdict(lambda : 0)) # [ownernumber][resourcetype]
resourceslast = defaultdict(lambda : defaultdict(lambda : 0)) # Use by update function

# User messages
@usermessage(messagename='updateresource')
def ClientUpdateResource(ownernumber, resourcetype, amount, **kwargs):
    resources[ownernumber][resourcetype] = amount
    FireSignalRobust(resourceset, ownernumber=ownernumber, type=resourcetype, amount=amount)
        
# Resource handlers
def DefaultTakeResource(ownernumber, resource):
    UpdateResource(ownernumber, resource[0], -resource[1])
    
def DefaultGiveResource(ownernumber, resource):
    UpdateResource(ownernumber, resource[0], resource[1])
    
def GrubTakeResources(ownernumber, resource):  
    n = resource[1]
    grub = gEntList.FindEntityByClassname(None, "unit_antliongrub")
    while grub and n > 0:
        if not grub.IsMarkedForDeletion() and grub.IsResource() and grub.GetOwnerNumber() == ownernumber:
            grub.Remove()
            n -= 1
        grub = gEntList.FindEntityByClassname(grub, "unit_antliongrub")

def GrubGiveResources(ownernumber, resource): 
    # Find an antlion colony, then add grubs
    colony = gEntList.FindEntityByClassname(None, "build_ant_colony")
    if not colony:
        PrintWarning('GrubGiveResources: No antlion colony found to give grubs to\n')
        return
    colony.AddGrubs(resource[1])
    
def CheckClientResources():
    #print('Updating client resources')
    for ownernumber, ownresources in resources.iteritems():
        for type, amount in ownresources.iteritems():
            if resourceslast[ownernumber][type] != amount:
                UpdateClientsResource(ownernumber, type)
                resourceslast[ownernumber][type] = amount
    
if isserver:
    # Level init
    @receiver(prelevelinit)
    def LevelInit(sender, **kwargs):
        InitializeResources()
        RegisterTickMethod(CheckClientResources, 0.2)
   
if isserver:   
    @receiver(postlevelshutdown)
    def LevelShutdown(sender, **kwargs):
        try:
            UnregisterTickMethod(CheckClientResources)
        except:
            print('core.resources: Already unregistered')

if isserver:
    @receiver(clientactive)
    def ClientActive(sender, client, **kwargs):
        UpdateAllClientResources(client)
    
# Resource methods    
def InitializeResources():
    global resources
    # Usage: resources[OWNER_NUMBER][RESOURCE_TYPE]
    resources.clear()
    resourceslast.clear()
    
def ResetResource(type):
    for ownernumber in resources.iterkeys():
        resources[ownernumber][type] = 0
        resourceslast[ownernumber][type] = 0
    
def UpdateResource(ownernumber, type, amount):
    resources[ownernumber][type] += amount
    FireSignalRobust(resourceupdated, ownernumber=ownernumber, type=type, amount=amount)
    
def SetResource(ownernumber, type, amount):
    resources[ownernumber][type] = amount
    
def HasEnoughResources(costs, ownernumber):
    """ Returns if the player has enough resources by checking
        the list of costs
        
        Input:
        costs - a list containing tuples of the form (cost, amount)
    """
    for resource in costs:
        if resource[1] > resources[ownernumber][resource[0]]:
            return False
    return True
    
def FindFirstCostSet(c, ownernumber):
    """ Returns the first list of costs in the Cost class satisfying
        the resources the player has.
        
        Input:
        c - an instance of C.
    """
    for l in c:
        if HasEnoughResources(l, ownernumber):
            return l
    return None
    
def TakeResources(ownernumber, costs):
    """ Takes resources for the player.
    
        Arguments:
        costs - a list containing tuples of the form (cost, amount)
    """
    if not costs:
        return
    for resource in costs:
        if resource[1] > 0:
            resource_types[resource[0]][0](ownernumber, resource)
            
def GiveResources(ownernumber, costs, firecollected=False):
    """ Gives resources to the player.
    
        Arguments:
        costs - a list containing tuples of the form (cost, amount)
    """
    if not costs:
        return
    for resource in costs:
        if resource[1] > 0:
            resource_types[resource[0]][1](ownernumber, resource)
            if firecollected:
                FireSignalRobust(resourcecollected, ownernumber=ownernumber, type=resource[0], amount=resource[1])
            
if isserver:
    def FullResourceUpdatePlayers():
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if player == None:
                continue    
            UpdateAllClientResources(player)
        
    def UpdateAllClientResources(client):
        filter = CSingleUserRecipientFilter(client)
        filter.MakeReliable()        
        for type, value in resource_types.iteritems():
            SendResourceInfo(filter, client.GetOwnerNumber(), type)        
        
    def UpdateClientsResource(ownernumber, type):
        """ For each player with this ownernumber update resource of the given type """
        filter = CRecipientFilter()
        filter.MakeReliable() 
        for i in range(1, gpGlobals.maxClients+1):
            player = UTIL_PlayerByIndex(i)
            if player == None:
                continue
            if player.GetOwnerNumber() == ownernumber:
                filter.AddRecipient(player)
        SendResourceInfo(filter, ownernumber, type)
        
    def SendResourceInfo(filter, ownernumber, type):
        ClientUpdateResource(ownernumber, type, resources[ownernumber][type], filter=filter)           

    @receiver(playerchangedownernumber)
    def PlayerChangedOwnerNumber(sender, player, oldownernumber, **kwargs):
        # If the old owner number is the same as the new one, we just spawned
        # In this case we use ClientActive already, so don't send again.
        if player.IsConnected() and player.GetOwnerNumber() != oldownernumber:
            UpdateAllClientResources(player)
    
    def MessageResourceIndicator(ownernumber, origin, text=''):
        # Temp import here, needs fix. Move to utils?
        players = UTIL_ListPlayersForOwnerNumber(ownernumber)
        filter = CRecipientFilter()
        filter.MakeReliable()
        map(filter.AddRecipient, players)
        msg = [origin, text] if text else [origin]
        SendUserMessage(filter, 
            'resourceindicator', 
            msg) 
else:
    FullResourceUpdatePlayers = None
    UpdateAllClientResources = None
    UpdateClientsResource = None
    SendResourceInfo = None
    PlayerChangedOwnerNumber = None
    MessageResourceIndicator = None
    
# Available resources
RESOURCE_GRUB = 'grubs'
RESOURCE_KILLS = 'kills'
RESOURCE_REQUISITION = 'requisition'
RESOURCE_POWER = 'power'
RESOURCE_SCRAP = 'scrap'

resource_types = defaultdict( lambda: (DefaultTakeResource, DefaultGiveResource) )
resource_types[RESOURCE_GRUB] = (GrubTakeResources, GrubGiveResources)

# Defines costs
class C(list):
    def __init__(self, costname=None, value=None):
        super(C, self).__init__()
        if costname:
            self.append([(costname, value)])
        
    def __and__(self, other):
        if not isinstance(other, C):
            raise TypeError(other)
        c = copy.deepcopy(self)
        if other:
            c[-1].extend(other[0])
            if len(other) > 1:
                c.extend(other[1:len(other)])
        return c
        
    def __or__(self, other):
        if not isinstance(other, C):
            raise TypeError(other)
        c = copy.deepcopy(self)
        c.extend(other)
        return c
        
# Commands for testing
if isserver:
    @concommand('wars_giveresource', 'Give resource', FCVAR_CHEAT,
                                    completionfunc=AutoCompletion(lambda: resource_types.keys()))
    def cc_wars_giveresource(args):
        try:
            resource = (args[1], int(args[2]))
        except:
            print('Usage: wars_giveresource [resourcetype] [amount]')
            return
        player = UTIL_GetCommandClient()
        resource_types[resource[0]][1](player.GetOwnerNumber(), resource)
