from srcbase import Color
import playermgr
from gamerules import GameRules
from fields import BaseField, GetField

from attributemgr_shared import IsAttributeFiltered
import types
from gameinterface import ConVarRef
from core.usermessages import usermessage, SendUserMessage, CSingleUserRecipientFilter

if isserver:
    from utils import UTIL_GetCommandClient
    from gameinterface import ConCommand, FCVAR_CHEAT
    from entities import GetClassByClassname
else:
    from vgui.tools import attributemodifiertool, playermodifiertool
    
sv_cheats = ConVarRef('sv_cheats')

# Client messages
@usermessage()
def UnitInfoClear(unitname, **kwargs):
    attributemodifiertool.unitpanel.Clear(unitname)
    
@usermessage()
def UnitInfoSetAttr(apply, unitname, fieldname, default, **kwargs):
    if apply:
        ApplyUnitAttribute(unitname, fieldname, default)
    attributemodifiertool.unitpanel.SetAttribute(unitname, fieldname, default)
    
@usermessage()
def ClassInfoClearAttr(unitname, **kwargs):
    attributemodifiertool.classpanel.Clear(unitname)
    
@usermessage()
def ClassInfoSetAttr(apply, unitname, fieldname, default, **kwargs):
    attributemodifiertool.classpanel.SetAttribute(unitname, fieldname, default)
    
@usermessage()
def PlayerInfoSetAttr(apply, name, fieldname, default, **kwargs):
    if apply:
        ApplyPlayerAttribute(name, fieldname, default)
    playermodifiertool.playerpanel.SetAttribute(name, fieldname, default)
    
# Apply attribute types
def ApplyUnitAttribute(unitname, keyname, rawvalue):
    info = GetUnitInfo(unitname, fallback=None)
    if not info:
        return  

    field = GetField(info, keyname)
    if not field:
        PrintWarning( 'No field for %s' % (keyname) )
        return
    field.Set(info, rawvalue)
    
def ApplyClassAttribute(unitname, keyname, rawvalue):
    info = GetUnitInfo(unitname, fallback=None)
    if not info:
        return  
    cls = GetClassByClassname(info.cls_name)
    if not cls:
        PrintWarning( 'ApplyClassAttribute: no such class name %s\n' % (info.cls_name) )
        return
    field = GetField(cls, keyname)
    if not field:
        PrintWarning( 'No field for %s' % (keyname) )
        return
    field.Set(cls, rawvalue)
    
def ApplyPlayerAttribute(ownernumber, keyname, rawvalue):
    playerinfo = playermgr.dbplayers[ownernumber]
    SetAttribute(playerinfo, keyname, rawvalue)
        
# Attribute edit commands
if isserver:
    # Method that sends all attributes of an obj + baseclasses
    def SendAllAttributes(fnsetter, obj, unitname, filterflags, sendfilter, stopbasecls, done):
        for name, field in obj.__dict__.iteritems():
            if not isinstance(field, BaseField):
                continue
            if IsAttributeFiltered(name, field, filterflags):
                continue
            if name in done:
                continue
            done.append(name)
            fnsetter(False, unitname, field.name, str(field.default), filter=sendfilter)

        if obj in stopbasecls:
            return
            
        # Recursive call all bases
        for base in obj.__bases__:
            SendAllAttributes(fnsetter, base, unitname, filterflags, sendfilter, stopbasecls, done)

    # ================ Unit info ================
    def cc_unitinfo_requestall(args):
        # Get requesting player
        player = UTIL_GetCommandClient()
        if not player:
            return
            
        # Check. Can only use if cheats are on or if we are in the sandbox gamemode
        if not sv_cheats.GetBool() and not GameRules().info.name == 'sandbox':
            print("Can't use cheat command unitinfo_requestall in multiplayer, unless the server has sv_cheats set to 1.")
            return
        
        # Grab the info
        info = GetUnitInfo(args[1], fallback=None)
        if not info:
            PrintWarning("unitinfo_requestall: Invalid unit %s" % (args[1]))
            return
            
        # Filter flags
        filterflags = int(args[2])
            
        # Make a filter
        filter = CSingleUserRecipientFilter(player)
        filter.MakeReliable()
        
        # Tell player to clear old
        UnitInfoClear(info.name, filter=filter)
        
        # Send each attribute. Cannot happen in one message, since it easily goes over the max 256 bytes
        SendAllAttributes(UnitInfoSetAttr, info, info.name, filterflags, filter, [], [])
        
    unitinfo_requestall = ConCommand('unitinfo_requestall', cc_unitinfo_requestall, "")    

    def cc_unitinfo_setattr(args):
        # Get requesting player
        player = UTIL_GetCommandClient()
        if not player:
            return
            
        # Check. Can only use if cheats are on or if we are in the sandbox gamemode
        if not sv_cheats.GetBool() and not GameRules().info.name == 'sandbox':
            print("Can't use cheat command unitinfo_setattr in multiplayer, unless the server has sv_cheats set to 1.")
            return
            
        # Grab the info
        info = GetUnitInfo(args[1], fallback=None)
        if not info:
            PrintWarning("unitinfo_setattr: Invalid unit %s" % (args[1]))
            return
            
        # Apply
        ApplyUnitAttribute(args[1], args[2], args[3]) 
        UnitInfoSetAttr(True, info.name, args[2], args[3])
        
    unitinfo_setattr = ConCommand('unitinfo_setattr', cc_unitinfo_setattr, "")
    
    # ================ Class info ================ 
    def cc_classinfo_requestall(args):
        # Get requesting player
        player = UTIL_GetCommandClient()
        if not player:
            return
            
        # Check. Can only use if cheats are on or if we are in the sandbox gamemode
        if not sv_cheats.GetBool() and not GameRules().info.name == 'sandbox':
            print("Can't use cheat command classinfo_requestall in multiplayer, unless the server has sv_cheats set to 1.")
            return
            
        # Grab the info
        info = GetUnitInfo(args[1], fallback=None)
        if not info:
            PrintWarning("classinfo_requestall: Invalid unit %s" % (args[1]))
            return
            
        # Grab the class
        cls = GetClassByClassname(info.cls_name)
        if not cls:
            PrintWarning("classinfo_requestall: Invalid unit clas %s" % (info.cls_name))
            return
            
        # Filter flags
        filterflags = int(args[2])
        
        # Make a filter
        filter = CSingleUserRecipientFilter(player)
        filter.MakeReliable()
        
        # Tell player to clear old
        ClassInfoClearAttr(info.name, filter=filter) 
        
        # Send each attribute. Cannot happen in one message, since it easily goes over the max 256 bytes
        SendAllAttributes(ClassInfoSetAttr, cls, info.name, filterflags, filter, [UnitBase], [])

    classinfo_requestall = ConCommand('classinfo_requestall', cc_classinfo_requestall, "")    
    
    def cc_classinfo_setattr(args):
        # Get requesting player
        player = UTIL_GetCommandClient()
        if not player:
            return
            
        # Check. Can only use if cheats are on or if we are in the sandbox gamemode
        if not sv_cheats.GetBool() and not GameRules().info.name == 'sandbox':
            print("Can't use cheat command classinfo_setattr in multiplayer, unless the server has sv_cheats set to 1.")
            return
            
        # Grab the info
        info = GetUnitInfo(args[1], fallback=None)
        if not info:
            PrintWarning("classinfo_settattr: Invalid unit %s" % (args[1]))
            return
        
        # Apply
        ApplyClassAttribute(args[1], args[2], args[3])
        ClassInfoSetAttr(True, info.name, args[2], args[3])  

    classinfo_setattr = ConCommand('classinfo_setattr', cc_classinfo_setattr, "")
    
    # ================ Player info ================ 
    def cc_playerinfo_setattr(args):
        # Get requesting player
        player = UTIL_GetCommandClient()
        if not player:
            return
            
        # Check. Can only use if cheats are on or if we are in the sandbox gamemode
        if not sv_cheats.GetBool() and not GameRules().info.name == 'sandbox':
            print("Can't use cheat command playerinfo_setattr in multiplayer, unless the server has sv_cheats set to 1.")
            return
            
        # Apply
        ApplyPlayerAttribute(int(args[1]), args[2], args[3])
        PlayerInfoSetAttr(True, int(args[1]), args[2], args[3])

    playerinfo_setattr = ConCommand('playerinfo_setattr', cc_playerinfo_setattr, "")
    