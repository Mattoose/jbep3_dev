"""
A central module for dealing with hotkeys.
The main goal is how to deal with hotkeys for abilities 
since they change dynamically based on the unit selection.
"""
import srcmgr
srcmgr.VerifyIsClient() # Only on client, sends commands to the server

from srcbase import RegisterTickMethod
from entities import C_HL2WarsPlayer
from gameinterface import ConCommand, engine, ConVar, FCVAR_ARCHIVE, ConVarRef
from core.abilities import DoAbility, ClientDoAbility
from core.units import GetUnitInfo, NoSuchAbilityError
from core.signals import clientconfigchanged

import traceback 
import os

cl_active_config = ConVarRef('cl_active_config')

class BaseHotkeySystem(object):
    # List of characters that are possible bound to a hotkey
    hotkeys_characters = [
        'q', 'w', 'e', 'r',
        'a', 's', 'd', 'f',
        'z', 'x', 'c', 'v',
    ]

    def __init__(self):
        # Create a ConCommand for each character
        self.hotkeys = {}
        for char in self.hotkeys_characters:
            down = ConCommand( "+hotkey_%s" % (char), self.HandleHotKeyIntern, "Hotkey %s" % (char) )
            up = ConCommand( "-hotkey_%s" % (char), self.HandleHotKeyIntern, "Hotkey %s" % (char) )
            self.hotkeys[char] = (down, up)
        self.InstallHotKeys()
        
        clientconfigchanged.connect(self.ClientConfigChanged)
        
    def Destroy(self):
        self.hotkeys = {} # Release references to the system
        clientconfigchanged.disconnect(self.ClientConfigChanged)
        
    def ClientConfigChanged(self, *args, **kwargs):
        self.InstallHotKeys()
        
    def InstallHotKeys(self):
        """ Overrides your rts config in an annoying way. """
        activeconfig = cl_active_config.GetString()
        
        # Set to rts config
        cl_active_config.SetValue('config_rts')
        
        # Bind hotkeys
        for hotkey in self.hotkeys_characters:
            engine.ExecuteClientCmd('bind "%s" "+hotkey_%s"' % (hotkey, hotkey))
        engine.ExecuteClientCmd('host_writeconfig') # Update our config
        
        # Restore active config
        cl_active_config.SetValue(activeconfig)
            
    def HandleHotKeyIntern(self, args):
        command = args[0]
        char = command.split('_')[1]
        keydown = command[0] == '+'
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
            
        self.hotkeydown = keydown
            
        if not keydown:
            if self.activeability:
                self.activeability.hotkeysystem = None
                self.activeability = None
            return
            
        self.HandleHotKey(player, char)
            
    def HandleHotKey(self, player, char):
        print 'Handling hotkey: %s' % (char)
        
    def GetHotkeyForAbility(self, abi_info, slot):
        return None
        
    def ContinueAbility(self, abi):
        abi.hotkeysystem = None
        self.continueabidata = (abi.player, abi.name, abi.unittype)
        self.activeability = None 
        # Delay by one frame to avoid problems with mouse events
        RegisterTickMethod(self.DoContinueAbility, 0.0, False)
            
    def DoContinueAbility(self):
        data = self.continueabidata
        self.activeability = ClientDoAbility(data[0], data[1], data[2])
        if self.activeability:
            self.activeability.hotkeysystem = self
        
    activeability = None
    hotkeydown = False
    continueabidata = None
    
class GridHotkeySystem(BaseHotkeySystem):
    """ Like in the SC2 grid option, hotkeys/abiltiies are mapped into a grid."""
    gridhotkeys_char_to_slot = {
        'q' : 0, 'w' : 1, 'e' : 2, 'r' : 3,
        'a' : 4, 's' : 5, 'd' : 6, 'f' : 7, 
        'z' : 8, 'x' : 9, 'c' : 10, 'v' : 11, 
    }
    gridhotkeys_slot_to_char = dict(zip(gridhotkeys_char_to_slot.values(), gridhotkeys_char_to_slot.keys()))
    
    def HandleHotKey(self, player, char):
        if char in self.gridhotkeys_char_to_slot.keys():
            self.HandleGridHotkey(player, char)
        
    def HandleGridHotkey(self, player, char):
        if self.activeability:
            self.activeability.hotkeydown = False
            self.activeability = None
        
        unittype = player.GetSelectedUnitType()
        if not unittype:
            return
        
        unitinfo = GetUnitInfo(unittype, fallback=None)
        if not unitinfo:
            return
        
        abislot = self.gridhotkeys_char_to_slot[char]
        
        # Retrieve the active hud abilities map
        try:
            abilitiesmap = player.hudabilitiesmap[-1]
        except (AttributeError, IndexError):
            abilitiesmap = unitinfo.abilities
            
        # Must be in the map
        if abislot not in abilitiesmap:
            return
        
        # Get ability info
        try:
            abiinfo = unitinfo.GetAbilityInfo(abilitiesmap[abislot], player.GetOwnerNumber())
        except NoSuchAbilityError:
            return
            
        if not abiinfo:
            return

        self.activeability = ClientDoAbility(player, abiinfo, unitinfo.name)
        if self.activeability:
            self.activeability.hotkeysystem = self
            
    def GetHotkeyForAbility(self, abiinfo, slot):
        return self.gridhotkeys_slot_to_char[slot]
        
class SemanticHotkeySystem(BaseHotkeySystem):
    def __init__(self):
        super(SemanticHotkeySystem, self).__init__()
        
# The current hotkey system. Do not import directly (since it might change due the convar below).
hotkeysystem = None

def HotKeyConvarChanged(var, old_value, f_old_value):
    global hotkeysystem
    newsystem = var.GetString()
    
    try:
        if newsystem == 'grid':
            hotkeysystem = GridHotkeySystem()
        elif newsystem == 'semantic':
            hotkeysystem = SemanticHotkeySystem()
        else:
            print('HotKeyConvarChanged: Invalid system %s, defaulting to grid' % (newsystem))
            hotkeysystem = GridHotkeySystem()
    except:
        PrintWarning('Failed to install the hotkey system.\n')
        traceback.print_exc()
        
hotkeysystemvar = ConVar('hotkeysystem', 'grid', FCVAR_ARCHIVE, "Hotkey system", HotKeyConvarChanged)

HotKeyConvarChanged(hotkeysystemvar, '-', 0.0)
