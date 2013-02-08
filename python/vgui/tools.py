from srcbase import KeyValues
from vgui import GetClientMode, scheme, DataType_t
from vgui.controls import Frame, Button, Label, TextEntry, ListPanel, ComboBox, PropertySheet, TreeView
from gameinterface import engine, concommand
from input import ButtonCode_t

from core.units.info import GetUnitInfo
from core.dispatch import receiver
from core.signals import gamepackageloaded, gamepackageunloaded

import playermgr
from fields import BaseField

from attributemgr_shared import IsAttributeFiltered, ReqAttrFilterFlags

# Helper
def ShowTool(tool, show):
    if not show:
        tool.SetVisible(False)
        tool.SetEnabled(False)  
    else:
        tool.SetVisible(True)
        tool.SetEnabled(True)   
        tool.RequestFocus()
        tool.MoveToFront()
        
@receiver(gamepackageloaded)
@receiver(gamepackageunloaded)
def OnGamePackageChanged(sender, packagename, **kwargs):    
    wunitpanel.OnGamePackageChanged(packagename)
    unitpanel.OnGamePackageChanged(packagename)
    abilitypanel.OnGamePackageChanged(packagename)
    attributemodifiertool.OnGamePackageChanged(packagename)
    
#
# New Awesomium panels
#
from awesomium import WPanel, viewport
class WUnitPanel(WPanel):
    htmlfile = 'ui/tools/unitpanel.html'
    jsfile = 'ui/tools/unitpanel.js'
    
    def __init__(self, *args, **kwargs):
        super(WUnitPanel, self).__init__(*args, **kwargs)
        
        self.SetVisible(False)
 
    def OnLoaded(self):
        self.LoadUnits()
        
    def OnGamePackageChanged(self, package_name):
        self.LoadUnits()
        
    def LoadUnits(self):
        from core.units.info import dbunits, GetUnitInfo
        self.element.Invoke("clearList", [])
        for unit in dbunits.values():
            if unit.hidden:
                continue
            self.element.Invoke("addUnit", [unit.name])
    
wunitpanel = WUnitPanel(viewport, 'unitpanel')

@concommand('wunitpanel', 'Show up a panel to create units (cheats)', 0)
def show_wunitpanel(args):
    ShowTool(wunitpanel, not wunitpanel.IsVisible())

#
# Base Frame for tools. Shared functionality
#
class ToolBaseFrame(Frame):
    def __init__(self, parent, panelname):
        super(ToolBaseFrame, self).__init__(parent, panelname)
        
        self.passthroughkeys = True
        self.keyspressed = []

    #
    # The following code will pass the keys to the game, so we can move around while the panel has focus
    #    
    def OnKeyCodePressed(self, code):
        super(ToolBaseFrame, self).OnKeyCodePressed(code)
        if code in self.eatkeys or not self.passthroughkeys:
            return

        binding = engine.Key_BindingForKey(code)
        if binding:
            if binding.startswith('+'):
                engine.ClientCommand(binding)
                self.keyspressed.append(binding)
            elif GetClientMode().KeyInput(1, code, binding):
                pass
        
    def OnKeyCodeReleased(self, code):
        super(ToolBaseFrame, self).OnKeyCodeReleased(code)
        if code in self.eatkeys or not self.passthroughkeys:
            return

        binding = engine.Key_BindingForKey(code)
        if binding:
            if binding.startswith('+'):
                try:
                    self.keyspressed.remove(binding)
                except ValueError:
                    pass
                binding = binding.replace('+', '-', 1)
                engine.ClientCommand(binding)
            elif GetClientMode().KeyInput(0, code, binding):
                pass
                
    def SetVisible(self, state):
        super(ToolBaseFrame, self).SetVisible(state)
    
        if not state:
            for kp in self.keyspressed:
                binding = kp.replace('+', '-', 1)
                engine.ClientCommand(binding)
            self.keyspressed = []    

    # Eat these keys, pass the rest through to the game
    eatkeys = [ButtonCode_t.KEY_SPACE]
    
#
# Tool list panel
#
class ToolListPanel(ListPanel):
    def ApplySchemeSettings(self, schemeobj):
        super(ToolListPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontdebugverysmall = schemeobj.GetFont( "DefaultVerySmall" )
        self.SetFont(hfontdebugverysmall)

# ==============================================================
# Panel for creating units, instead of having to use the unit_create command
# ==============================================================
class UnitPanel(ToolBaseFrame):
    def __init__(self):
        super(UnitPanel, self).__init__(None, 'UnitPanel')
        
        # Set scheme
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        self.SetVisible(False)
        
        self.SetTitle("Spawn Unit", False)

        # Unit list
        self.unitlist = ToolListPanel(self, "UnitList")
        self.unitlist.SetScheme(schemeobj)
        self.unitlist.SetMultiselectEnabled(False)
        self.unitlist.AddColumnHeader(0, "displayname", "Units", 200, ToolListPanel.COLUMN_RESIZEWITHWINDOW)
        
        # Place
        self.placebutton = Button( self, "PlaceButton", 'Place' )
        self.placebutton.SetScheme(schemeobj)
        self.placebutton.SetCommand('placeunit')  
        
        # Create
        self.createlabel = Label( self, "CreateLabel", "Direct: SPACE" )
        self.createlabel.SetScheme(schemeobj)
        
        # Owner number
        self.playerbox = self.UnitPanelComboBox(self, "PlayerBox", 11 , False)
        self.playerbox.SetScheme(schemeobj)
        self.playerbox.SetVisible( True )
        self.playerbox.SetEnabled( True )
        
        self.playerbox.AddItem( "-", None )
        self.playerbox.AddItem( "n", 0 )
        self.playerbox.AddItem( "e", 1 )
        self.playerbox.AddItem( "p1", 2 )
        self.playerbox.AddItem( "p2", 3 )
        self.playerbox.AddItem( "p3", 4 )
        self.playerbox.AddItem( "p4", 6 )
        self.playerbox.AddItem( "p5", 7 )
        self.playerbox.AddItem( "p6", 8 )
        self.playerbox.AddItem( "p7", 9 )
        self.playerbox.AddItem( "p8", 10 )
        
        self.LoadControlSettings("Resource/UI/UnitPanel.res")
        
    def OnGamePackageChanged(self, package_name):
        self.LoadUnits()
        
    def LoadUnits(self):
        from core.units.info import dbunits, GetUnitInfo
        self.unitlist.ClearSelectedItems() # Can't have items selected when we refresh
        self.unitlist.RemoveAll()
        for unit in dbunits.values():
            if unit.hidden:
                continue
            data = KeyValues(unit.name, 'displayname', unit.name)
            data.SetString('name', unit.name)
            self.unitlist.AddItem( data, 0, False, True )

    def ApplySchemeSettings(self, schemeobj):
        super(UnitPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontdebugverysmall = schemeobj.GetFont( "DefaultVerySmall" )
        self.createlabel.SetFont(hfontdebugverysmall)

        self.LoadUnits()
  
    def OnCommand(self, command):
        if command == 'placeunit':
            itemid = self.unitlist.GetSelectedItem(0)
            if itemid == -1: 
                # TODO: Notify user
                return
            selectedunit = self.unitlist.GetItem(itemid).GetString('name')
                
            engine.ClientCommand("wars_abi %s" % (selectedunit) )   
        else:
            super(UnitPanel, self).OnCommand(command)

    def OnKeyCodeTyped(self, code):
        super(UnitPanel, self).OnKeyCodeTyped(code)

        if code == ButtonCode_t.KEY_SPACE:
            itemid = self.unitlist.GetSelectedItem( 0 )
            if itemid == -1: 
                # TODO: Notify user
                return
            selectedunit = self.unitlist.GetItem(itemid).GetString('name')
                
            if self.playerbox.GetActiveItemUserData() != None:
                engine.ClientCommand("unit_create %s %s" % (selectedunit, self.playerbox.GetActiveItemUserData()) )   
            else:
                engine.ClientCommand("unit_create %s" % (selectedunit) )

    # ComboBox that passes the space key to it's parent
    class UnitPanelComboBox(ComboBox):
        def OnKeyCodeTyped(self, code):
            if code == ButtonCode_t.KEY_SPACE:
                self.CallParentFunction(KeyValues("KeyCodeTyped", "code", code))
                return
            super(UnitPanel.UnitPanelComboBox, self).OnKeyCodeTyped(code)
            
unitpanel = UnitPanel()   
        
@concommand('unitpanel', 'Show up a panel to create units (cheats)', 0)
def show_unitpanel(args):
    ShowTool(unitpanel, not unitpanel.IsVisible())

# ==============================================================
# Execute an ability from the list
# ==============================================================
class AbilityPanel(ToolBaseFrame):
    def __init__(self):
        super(AbilityPanel, self).__init__(None, 'AbilityPanel')
        # Set scheme
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        self.SetVisible(False)
        
        self.SetTitle("Create Ability", False)
        
        # Unit list
        self.abilitylist = ToolListPanel(self, "AbilityList")
        self.abilitylist.SetScheme(schemeobj)
        self.abilitylist.SetMultiselectEnabled(False)
        self.abilitylist.AddColumnHeader(0, "displayname", "Abilities", 200, ToolListPanel.COLUMN_RESIZEWITHWINDOW)
        
        # Place
        self.executebutton = Button( self, "ExecuteButton", 'Execute' )
        self.executebutton.SetScheme(schemeobj)
        self.executebutton.SetCommand('doability')  
        
        # Create
        self.createlabel = Label( self, "CreateLabel", "Direct: SPACE" )
        self.createlabel.SetScheme(schemeobj)
        
        self.LoadControlSettings("Resource/UI/AbilityPanel.res")
        
    def OnGamePackageChanged(self, package_name):
        self.LoadAbilities()
        
    def LoadAbilities(self):
        self.abilitylist.ClearSelectedItems() # Can't have items selected when we refresh
        self.abilitylist.RemoveAll()
        from core.abilities.info import dbabilities
        for abi in dbabilities.values():
            if abi.hidden:
                continue
            data = KeyValues(abi.name, 'displayname', abi.name)
            data.SetString('name', abi.name)
            self.abilitylist.AddItem( data, 0, False, True )

    def ApplySchemeSettings(self, schemeobj):
        super(AbilityPanel, self).ApplySchemeSettings(schemeobj)

        self.LoadAbilities()
        
    def ExecuteSelected(self):
        itemid = self.abilitylist.GetSelectedItem(0)
        if itemid == -1: 
            # TODO: Notify user
            return
        selectedability = self.abilitylist.GetItem(itemid).GetString('name')
            
        engine.ClientCommand("wars_abi %s" % (selectedability))   
            
    def OnCommand(self, command):
        if command == 'doability':
            self.ExecuteSelected() 
        else:
            super(AbilityPanel, self).OnCommand(command)

    def OnKeyCodeTyped(self, code):
        super(AbilityPanel, self).OnKeyCodeTyped(code)

        if code == ButtonCode_t.KEY_SPACE:
            self.ExecuteSelected() 
        
abilitypanel = AbilityPanel()   
        
@concommand('abilitypanel', 'Show up a panel to create abilities (cheats)', 0)
def show_abilitypanel(args):
    ShowTool(abilitypanel, not abilitypanel.IsVisible())
        
# ==============================================================
# Modify attribute of units
# ==============================================================
class AttributeValue(TextEntry):
    def ApplySchemeSettings(self, schemeobj):
        super(AttributeValue, self).ApplySchemeSettings(schemeobj)
        
        hfontdebugverysmall = schemeobj.GetFont( "DefaultVerySmall" )
        self.SetFont(hfontdebugverysmall)

class AttributeModifierPanel(TreeView):
    def __init__(self, parent, panelname, sendcommand):
        super(AttributeModifierPanel, self).__init__(parent, panelname)
        
        self.sendcommand = sendcommand
        
        # Set scheme
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        self.SetVisible(False)
        
        # PTR datatype only works with the name "Panel", which is automatically set if you use PostActionSignal
        self.RegMessageMethod( "TextNewLine", self.OnSendNewLine, 1, "panel", DataType_t.DATATYPE_PTR )
        
    def ApplySchemeSettings(self, schemeobj):
        super(AttributeModifierPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontdebugsmall = schemeobj.GetFont( "DefaultVerySmall" )
        self.SetFont(hfontdebugsmall)

    def Clear(self, indentifier):
        self.indentifier = indentifier
        self.RemoveAll()  
        self.rootIndex = self.AddItem( {'Text':'root', 'Data':None}, -1)
        
    def LoadAttributesFromObject(self, object, filterflags=0):
        for k, v in object.__dict__.iteritems():
            if not isinstance(v, BaseField):
                continue
            if IsAttributeFiltered(k, v, filterflags):
                continue
            self.SetAttribute(self.indentifier, k, str(v))
            
    def SetAttribute(self, indentifier, name, value):
        # Change existing attribute
        for node in self.nodeList:
            if node.data['Text'] == name:
                node.data['Data'].SetText(value)
                return
                
        # Insert new if not found
        a = AttributeValue(self, 'AttributeValue')
        a.SetText(value)
        a.SetWide(200)
        a.SendNewLine(True)
        a.AddActionSignalTarget( self )
        i = self.AddItem( {'Text':name, 'Data':a}, self.rootIndex) 
        a.SetTall(self.GetItem(i).GetTall())
        if not self.nodeList[self.rootIndex].expand:
            self.ExpandItem(self.rootIndex, True)
            
        self.InvalidateLayout()
 
    def OnSendNewLine(self, panel):
        for node in self.nodeList:
            if node.data['Data'] == panel:
                attributename = node.data['Text']
        engine.ServerCommand('%s %s %s "%s"' % (self.sendcommand, self.indentifier, attributename, panel.GetText()))
        self.RequestFocus() # Kill focus of the particular attribute field
        
    def PerformLayout(self):
        super(AttributeModifierPanel, self).PerformLayout()
        
        xpos = 0
        for node in self.nodeList:
            x, y = node.GetPos()
            xposnode = x + node.GetWide()
            if xposnode > xpos:
                xpos = xposnode

        for node in self.nodeList:
            if not node.data['Data']:   # Root node
                continue
            if not node.IsVisible():
                node.data['Data'].SetVisible(False)
                continue
            x, y = node.GetPos()
            node.data['Data'].SetPos(xpos + 20, y)
            node.data['Data'].SetVisible(True)
           
class AttributeModifierTool(ToolBaseFrame):
    def __init__(self):
        super(AttributeModifierTool, self).__init__(None, 'AttributeModifierTool')
        
        # Set scheme
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        self.SetVisible(False)
        
        self.SetTitle("Attribute Editor", False)
        self.passthroughkeys = False
        
        # Unit list
        self.unitlist = ToolListPanel(self, "UnitList")
        self.unitlist.SetScheme(schemeobj)
        self.unitlist.SetMultiselectEnabled(False)
        self.unitlist.AddColumnHeader(0, "name", "Units", 200, ToolListPanel.COLUMN_RESIZEWITHWINDOW)
        self.unitlist.AddActionSignalTarget(self)
        
        self.RegMessageMethod("ItemSelected", self.OnItemSelected)
        
        # Different tabs for unit, class and instance data
        self.modifytabs = PropertySheet(self, 'ModifyTabs')
        self.modifytabs.SetScheme( schemeobj )
        self.modifytabs.SetVisible(True)  
        
        # Unit attribute panel
        self.unitpanel = AttributeModifierPanel(self.modifytabs, 'UnitAttributePanel', 'unitinfo_setattr')
        self.unitpanel.MakeReadyForUse()
        self.modifytabs.AddPage(self.unitpanel, 'Unit')
        
        # Class attribute panel
        self.classpanel = AttributeModifierPanel(self.modifytabs, 'ClassAttributePanel', 'classinfo_setattr')
        self.classpanel.MakeReadyForUse()
        self.modifytabs.AddPage(self.classpanel, 'Class')
        
        # Instance attribute panel
        self.instancepanel = AttributeModifierPanel(self.modifytabs, 'InstanceAttributePanel', 'instance_setattr')
        self.instancepanel.MakeReadyForUse()
        self.modifytabs.AddPage(self.instancepanel, 'Instance')
        
        self.LoadControlSettings("Resource/UI/AttributeModifierPanel.res")
        
    def OnGamePackageChanged(self, package_name):
        self.LoadUnits()
        
    def ApplySchemeSettings(self, schemeobj):
        super(AttributeModifierTool, self).ApplySchemeSettings(schemeobj)
        
        hfontdebugverysmall = schemeobj.GetFont( "DefaultVerySmall" )
        
        self.LoadUnits()

    def LoadUnits(self):
        from core.units.info import dbunits, GetUnitInfo
        self.unitlist.RemoveAll()
        for unit in dbunits.values():
            data = KeyValues(unit.name, 'name', unit.name)
            self.unitlist.AddItem( data, 0, False, True ) 

    def OnItemSelected(self):
        # Get the selected unit
        itemid = self.unitlist.GetSelectedItem( 0 )
        if itemid == -1: 
            assert(0)   # Got a selected message, so something SHOULD be selected
        selectedunit = self.unitlist.GetItem(itemid).GetString('name')

        # Get the active page
        activepage = self.modifytabs.GetActivePage()

        # Get info unit
        info = GetUnitInfo(selectedunit)
        assert(info)
        
        # Print
        engine.ServerCommand('unitinfo_requestall %s %d' % (selectedunit, 0))
        self.unitpanel.name = selectedunit
        engine.ServerCommand('classinfo_requestall %s %d' % (selectedunit, 0))
        self.classpanel.name = selectedunit
        
attributemodifiertool = AttributeModifierTool()   
        
@concommand('attributemodifiertool', 'Show a panel to modify attributes of an unit class or instance', 0)
def show_attributemodifiertool(args):
    ShowTool(attributemodifiertool, not attributemodifiertool.IsVisible())

# ==============================================================
# Modify player instance data
# ==============================================================
class PlayerModifierTool(ToolBaseFrame):
    def __init__(self):
        super(PlayerModifierTool, self).__init__(None, 'PlayerModifierTool')
        
        # Set scheme
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme( schemeobj )
        self.SetVisible(False)  
        
        self.SetTitle("Player Editor", False)
        self.passthroughkeys = False
        
        self.RegMessageMethod( "TextChanged", self.OnTextChanged, 2, 
                "vpanel", DataType_t.DATATYPE_INT, "text", DataType_t.DATATYPE_CONSTCHARPTR )
        
        # The attribute modifier panel
        self.playerpanel = AttributeModifierPanel(self, 'PlayerAttributePanel', 'playerinfo_setattr')
        self.playerpanel.MakeReadyForUse()
        
        # Owner number
        self.playerbox = ComboBox(self, "PlayerBox", 11 , False)
        self.playerbox.SetScheme(schemeobj)
        self.playerbox.SetVisible( True )
        self.playerbox.SetEnabled( True )
        
        self.playerbox.AddItem( "-", None )
        self.playerbox.AddItem( "n", 0 )
        self.playerbox.AddItem( "e", 1 )
        self.playerbox.AddItem( "p1", 2 )
        self.playerbox.AddItem( "p2", 3 )
        self.playerbox.AddItem( "p3", 4 )
        self.playerbox.AddItem( "p4", 6 )
        self.playerbox.AddItem( "p5", 7 )
        self.playerbox.AddItem( "p6", 8 )
        self.playerbox.AddItem( "p7", 9 )
        self.playerbox.AddItem( "p8", 10 )
        
        self.LoadControlSettings("Resource/UI/PlayerModifyPanel.res")
        
    def OnTextChanged(self, vpanel, data):
        panel = ipanel().GetPanel(vpanel, self.GetModuleName())
        userdata = panel.GetActiveItemUserData()
        self.playerpanel.Clear(userdata)     
        self.playerpanel.LoadAttributesFromObject( playermgr.dbplayers[userdata] )
        self.playerpanel.LoadAttributesFromObject( playermgr.dbplayers[userdata].__class__ )
            
playermodifiertool = PlayerModifierTool()   
        
@concommand('playermodifiertool', 'Show a panel to modify attributes of a player', 0)
def show_playermodifiertool(args):
    ShowTool(playermodifiertool, not playermodifiertool.IsVisible())
