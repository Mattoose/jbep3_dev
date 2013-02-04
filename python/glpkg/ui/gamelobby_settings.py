from srcbase import KeyValues, Color
from input import ButtonCode_t
from gamerules import GameRules
from gameinterface import engine

from vgui import scheme, ipanel, AddTickSignal, RemoveTickSignal, DataType_t
from vgui.controls import Panel, Frame, Button, Label, RichText, ListPanel, ComboBox
from gamelobby_minimap import GamelobbyMinimap
from core.gamerules.info import dbgamerules
from core.gamerules import GetGamerulesInfo

class ChoiceHeader(Label):
    def __init__(self, parent, panelname, text):
        super(ChoiceHeader, self).__init__(parent, panelname, text)
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
    def ApplySchemeSettings(self, schemeobj):
        super(ChoiceHeader, self).ApplySchemeSettings(schemeobj)
        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        self.SetFont(hfontmedium)
        self.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        self.SetFgColor(Color(216, 222, 211, 255))
        
class ChoiceComboBox(ComboBox):
    def __init__(self, parent, panelname, numLines, allowEdit):
        super(ChoiceComboBox, self).__init__(parent, panelname, numLines, allowEdit)
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
    def ApplySchemeSettings(self, schemeobj):
        super(ChoiceComboBox, self).ApplySchemeSettings(schemeobj)
        
        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        self.GetMenu().MakeReadyForUse()
        self.SetBorder(None)
        self.SetFgColor( schemeobj.GetColor("White", Color(255, 255, 255 ) ) )
        self.SetBgColor( Color(0, 0, 0, 0) )
        self.SetFont(hfontmedium)   
        
class SettingsPanel(Frame):
    def __init__(self, parent, panelname):
        super(SettingsPanel, self).__init__(parent, panelname)
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme( schemeobj )
        self.SetVisible(False)

        self.SetMoveable(True)
        self.SetSizeable(False)
        self.SetProportional(True)
        self.SetTitleBarVisible( False )
        
        self.header = Label(self, "Header", "Settings")
        self.header.SetScheme( schemeobj )
        
        # Settings background
        self.background = Panel(self, "SettingsArea")
        self.background.SetScheme( schemeobj )
        self.background.SetZPos(-1)
        
        # Map list
        self.maplist = ListPanel(self, "SettingsMapList")
        self.maplist.SetScheme( schemeobj )
        self.maplist.SetMultiselectEnabled( False )
        self.maplist.AddColumnHeader( 0, "name", "Maps", 200, ListPanel.COLUMN_RESIZEWITHWINDOW )
        
        # info
        self.mapname = RichText(self, "MapName")
        self.mapname.SetScheme(schemeobj)     
        self.mapname.SetVerticalScrollbar(False)        
            
        self.gamerulesheader = RichText(self, "GameRulesHeader")
        self.gamerulesheader.SetScheme(schemeobj)
        self.gamerulesheader.SetVerticalScrollbar(False)
        self.gamerules = ComboBox(self, "GameRules", 10, False )
        self.gamerules.SetScheme(schemeobj)
        self.gamerules.SetVisible( True )
        self.gamerules.AddActionSignalTarget( self )
        self.gamerules.SetEnabled( True )    
        self.LoadGamerules()
            
        # Cancel/select button
        self.cancelbutton = Button( self, "CancelButton", 'Cancel' )
        self.cancelbutton.SetScheme(schemeobj)
        self.cancelbutton.SetCommand('Cancel')

        self.selectbutton = Button( self, "SelectButton", 'Select' )
        self.selectbutton.SetScheme(schemeobj)
        self.selectbutton.SetCommand('Select')
        
        # Minimap 
        self.minimap = GamelobbyMinimap( self, "MiniMap", False )
        self.minimap.SetScheme(schemeobj)
        self.minimap.SetVisible( True )
        
        self.RegMessageMethod( "ItemSelected", self.OnItemSelected )
        self.RegMessageMethod( "TextChanged", self.OnTextChanged, 2, 
                "vpanel", DataType_t.DATATYPE_INT, "text", DataType_t.DATATYPE_CONSTCHARPTR )
        
        self.lastselectedmap = None
        self.customfields = {}
        
    def ApplySchemeSettings(self, schemeobj):
        super(SettingsPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        hfontheadLine = schemeobj.GetFont( "HeadlineLarge" )  
        
        self.SetBorder( schemeobj.GetBorder("ButtonBorder") )
        self.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        
        self.header.SetFont(hfontheadLine)
        self.header.SizeToContents()
        
        self.background.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.background.SetBgColor( schemeobj.GetColor("LightClayBG", Color(255, 255, 255 ) ) )
        self.background.SetBorder(schemeobj.GetBorder("DepressedBorder") )
        
        self.minimap.SetBorder(schemeobj.GetBorder("DepressedBorder") )
        
        # Gamerules selection
        self.gamerulesheader.SetFont(hfontmedium)
        self.gamerulesheader.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        self.gamerulesheader.SetFgColor(Color(216, 222, 211, 255))
        self.gamerules.GetMenu().MakeReadyForUse()
        self.gamerules.SetBorder(None)
        self.gamerules.SetFgColor( schemeobj.GetColor("White", Color(255, 255, 255 ) ) )
        self.gamerules.SetBgColor( Color(0, 0, 0, 0) )
        self.gamerules.SetFont(hfontmedium)        
        
        self.cancelbutton.SetFont(hfontmedium)
        self.selectbutton.SetFont(hfontmedium)
        
        self.maplist.SetFont(hfontsmall)
        self.maplist.SetColumnHeaderHeight( 32 )
        
        self.mapname.SetFont(hfontmedium)
        self.mapname.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        
    def PerformLayout(self):
        super(SettingsPanel, self).PerformLayout()
         
        self.MoveToCenterOfScreen()
        self.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 450),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 320))   
  
        # Header
        self.header.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 10),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 7))        
        self.header.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 150),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))   
  
        # Background
        self.background.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 4),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 4))        
        self.background.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 442),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 288))       
      
        # Minimap
        self.minimap.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 347),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 25))        
        self.minimap.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 95),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 95))          
      
        # Maplist
        self.maplist.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 10),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 25))        
        self.maplist.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 85),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 243))   
        self.maplist.vbar.SetWide(28)   # Temp
                
        # Buttons
        self.cancelbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 290),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 298))        
        self.cancelbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 75),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))   
        self.selectbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 371),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 298))        
        self.selectbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 75),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))                        
        
        # Default text
        self.SettingsChanged()

        # Info labels
        self.gamerulesheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 38))        
        self.gamerulesheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 45),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14)) 
        self.gamerules.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 145),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 35))        
        self.gamerules.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14)) 
        self.mapname.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 25))        
        self.mapname.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))      

        # Custom fields
        ystart = 52
        yincr = 14
        for cf in self.customfieldelements.itervalues():
            cf.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), ystart))   
            ystart += yincr
            
    def LoadGamerules(self):
        self.gamerules.RemoveAll()
        for k, f in dbgamerules.iteritems():
            # Skip the gamelobby rules
            if f.name == 'gamelobbyrules':
                continue
            self.gamerules.AddItem(f.displayname, f.name)  

    def LoadMapList(self):
        self.maplist.RemoveAll()
        info = GetGamerulesInfo(self.GetSelectedGamerules())
        for mapentry in GameRules().maplist.values():
            if info and not info.mapfilter.match(mapentry.mapname):
                continue
            data = KeyValues(mapentry.mapname, 'name', mapentry.mapname)
            self.maplist.AddItem(data, 0, False, True)
        self.CheckSelectedMap()
        
    def ShowPanel(self, show):
        if self.IsVisible() == show:
            return

        if show:
            self.Activate()
            self.SetMouseInputEnabled( True )
            self.DoModal()
            AddTickSignal( self.GetVPanel(), 100 )
            self.LoadDefaultSettings()
        else:
            self.SetVisible( False )
            self.SetMouseInputEnabled( False )
            self.CloseModal()
            RemoveTickSignal( self.GetVPanel() )
            
    def GetSelectedGamerules(self):
        itemid = self.gamerules.GetActiveItem()
        return self.gamerules.GetItemUserData(itemid) if itemid != -1 else 'sandbox'  

    def OnCommand(self, command):
        if command == 'Cancel':
            self.ShowPanel(False)
        elif command == 'Select':
            self.ShowPanel(False)
            
            # Send the fixed settings
            itemid = self.maplist.GetSelectedItem( 0 )
            if itemid != -1:
                mapname = self.maplist.GetItem(itemid).GetString('name')
            else:
                mapname = 'wmp_forest'
                
            gamerules = self.GetSelectedGamerules()
            
            engine.ClientCommand('gl_settings %s %s' % (mapname, gamerules))
            
            # Send the settings specific for the selected gamerules
            for name, cf in self.customfields.iteritems():
                panel = self.customfieldelements[name]
                if cf[0] == 'choices':
                    itemid = panel.choices.GetActiveItem()
                    if itemid != -1:
                        cfvalue = panel.choices.GetItemUserData(itemid)
                    else:
                        cfvalue = cf[1]
                    engine.ClientCommand('gl_custom %s %s' % (name, cfvalue))
                else:
                    assert(0)
        else:
            super(SettingsPanel, self).OnCommand(command)
            
    def OnTextChanged(self, vpanel, data):
        panel = ipanel().GetPanel(vpanel, self.GetModuleName())

        # Which combobox changed?
        userdata = panel.GetActiveItemUserData()
        if panel == self.gamerules:
            self.AddCustomFields()
            self.LoadMapList()

    def OnItemSelected(self):
        self.SettingsChanged()  
        
    def CheckSelectedMap(self):
        """ Called after the maplist changed to ensure we have a map selected"""
        # First try the map we had selected
        if self.lastselectedmap:
            for id in range(0, self.maplist.GetItemCount()):
                mapname = self.maplist.GetItem(id).GetString('name')
                if mapname == self.lastselectedmap:
                    self.maplist.SetSingleSelectedItem(id)
                    return
    
        # Otherwise try the gamerules selected map (server side controlled)
        if GameRules().selectedmap:
            id = self.maplist.GetItem(GameRules().selectedmap)
            if id != -1:
                self.maplist.SetSingleSelectedItem(id)
                return
        
        # Otherwise default to the first map in the list
        if self.maplist.GetItemCount() > 0:
            self.maplist.SetSingleSelectedItem(0)
        
    def LoadDefaultSettings(self):
        self.CheckSelectedMap()
            
        for id, item in enumerate(self.gamerules.dropdown.menuitems):
            if item.GetUserData() == GameRules().selectedgamerule:
                self.gamerules.ActivateItem(id)
                break    
    
    def SettingsChanged(self):
        itemid = self.maplist.GetSelectedItem( 0 )
        if itemid == -1: 
            selectedmap = 'None'
        else:
            selectedmap = self.maplist.GetItem(itemid).GetString('name')
            
        self.lastselectedmap = selectedmap
            
        self.minimap.SetMap( selectedmap )
            
        self.mapname.SetText("")
        self.mapname.InsertColorChange( Color(216, 222, 211, 255) )
        self.mapname.InsertString("Map: " + selectedmap)      

        self.gamerulesheader.SetText("")
        self.gamerulesheader.InsertColorChange( Color(216, 222, 211, 255) )
        self.gamerulesheader.InsertString("Gamerules: ")   

    def ParseCustomField(self, type, name, default_value, values):
        hscheme = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        schemeobj = scheme().GetIScheme(hscheme)
        if type == 'choices':
            container = Panel(self, name+'_container')
            container.type = type
            container.SetBgColor( Color(0,0,0,0) )
            container.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 150), scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))
            container.SetVisible(True)
            header = ChoiceHeader(container, name, name)
            header.SetPos(5, 0)
            header.SizeToContents()
            header.ApplySchemeSettings(schemeobj)
            header.Repaint()
            container.header = header
            choices = ChoiceComboBox(container, name+'_choices', len(values), False)
            choices.SetPos(header.GetWide(), 0)
            choices.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 100), scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))
            choices.AddActionSignalTarget( self )
            container.choices = choices
            for v in values:
                id = choices.AddItem(v, v)
                if v == default_value:
                    choices.ActivateItem(id)
            return container
        return None
        
    def AddCustomFields(self):
        self.customfieldelements = {}
        itemid = self.gamerules.GetActiveItem()
        if itemid == -1:
            return
        gamerules_name = self.gamerules.GetItemUserData(itemid)
        info = GetGamerulesInfo(gamerules_name)
        if not info:
            return
     
        try:
            GetCustomFields = info.cls.GetCustomFields
        except:
            GetCustomFields = None
        self.customfields = GetCustomFields() if GetCustomFields else {}
        
        for name, v in self.customfields.iteritems():
            self.customfieldelements[name] = self.ParseCustomField(v[0], name, v[1], v[2:len(v)])
        self.InvalidateLayout(True, True)    
            