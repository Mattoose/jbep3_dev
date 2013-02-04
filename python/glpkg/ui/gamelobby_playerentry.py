from srcbase import Color, KeyValues
from vgui import DataType_t, scheme, ipanel
from vgui.controls import Panel, AvatarImagePanel, CheckButton, MenuItem, Button, ComboBox
from isteam import CSteamID, steamapicontext, EAccountType, EAvatarSize
from gameinterface import PlayerInfo, engine
from gamerules import GameRules
from entities import C_HL2WarsPlayer, PlayerResource

from core.factions import dbfactions
from core.gamerules import GetGamerulesInfo

from ..gamelobby_shared import *

class ColorMenuItem(MenuItem):
    def GetButtonBgColor(self):
        if not self.IsEnabled():
            color = Button.GetButtonBgColor(self)
            return Color(int(color.r()*0.3+70), int(color.g()*0.3+70), int(color.b()*0.3+70), 255 )
        return Button.GetButtonBgColor(self)
        
    def ApplySchemeSettings(self, schemeobj):
        """ Apply the resource scheme to the menu. """
        pass
        # chain back first
        # Button.ApplySchemeSettings(schemeobj) 

# A player entry
class PlayerEntry(Panel):
    def __init__(self, parent, panelname, idxslot):
        super(PlayerEntry, self).__init__(parent, panelname)
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme( schemeobj )
        
        self.idxslot = idxslot
        self.curtype = -1
        self.useteams = True
        
        self.wasgamemaster = False
        self.oldsupportcpu = False
        
        self.RegMessageMethod( "TextChanged", self.OnTextChanged, 2, 
                "vpanel", DataType_t.DATATYPE_INT, "text", DataType_t.DATATYPE_CONSTCHARPTR )
        self.RegMessageMethod( "CheckButtonChecked", self.OnCheckButtonChecked )
                
        # Create avatar panel
        self.avatarpanel = AvatarImagePanel(self, "PlayerAvatar")
        self.avatarpanel.SetScheme(schemeobj)
        self.avatarpanel.SetVisible( True )
        self.curavatar = -1
        
        # set up the label for the name of the owner
        self.slotname = ComboBox(self, "slot", 4 , False)
        self.slotname.SetScheme(schemeobj)
        self.slotname.SetVisible( True )
        self.slotname.AddActionSignalTarget( self )
        self.slotname.SetEnabled( False )
        
        self.slotname.AddItem( "Open", GLTYPE_OPEN )
        self.slotname.AddItem( "Close", GLTYPE_CLOSED )
        self.slotname.AddItem( "Take slot", GLTYPE_HUMAN )
        self.slotname.AddItem( "Add CPU", GLTYPE_CPU )
        
        # Color selection for the player
        self.color = ComboBox(self, "Color", 10 , False)
        self.color.SetScheme(schemeobj)
        self.color.SetVisible( True )
        self.color.AddActionSignalTarget( self )
        self.color.SetEnabled( True )
        
        # Faction/side selection for the player
        self.faction = ComboBox(self, "faction", 3 , False)
        self.faction.SetScheme(schemeobj)	
        self.faction.SetVisible( True )
        self.faction.AddActionSignalTarget( self )
        self.faction.SetEnabled( True )
        self.LoadFactions()
        
        # Team selector
        self.team = ComboBox(self, "team", 10 , False)
        self.team.SetScheme(schemeobj)	
        self.team.SetVisible( True )
        self.team.AddActionSignalTarget( self )
        self.team.SetEnabled( True )
        
        self.team.AddItem( "-", TEAM_UNASSIGNED )
        self.team.AddItem( "1", TEAM_ONE )
        self.team.AddItem( "2", TEAM_TWO )
        self.team.AddItem( "3", TEAM_THREE )
        self.team.AddItem( "4", TEAM_FOUR )
        
        # ready button
        self.ready = CheckButton( self, "Ready", "" )
        self.ready.SetEnabled( False )
        self.ready.AddActionSignalTarget( self )
        
        for color_name, color in GL_COLORS.iteritems():
            # Contains the number of the color
            data = KeyValues( "UserData", "selected_color", color_name )
            
            # Create the item that represents the color
            coloritem = ColorMenuItem(self.color.GetMenu(), color_name, "")
            coloritem.SetDefaultColor( color, color )
            coloritem.SetArmedColor( color, color )
            coloritem.SetDepressedColor( color, color )
            coloritem.SetCommand(KeyValues("SetText", "text", color_name))
            coloritem.AddActionSignalTarget(self.color)
            coloritem.SetUserData(color_name)
            self.color.GetMenu().AddMenuItemIntern(coloritem)  
            
        self.color.GetMenu().MakeReadyForUse()   
        
    def ApplySchemeSettings(self, schemeobj):
        super(PlayerEntry, self).ApplySchemeSettings(schemeobj)
        
        self.SetBorder( schemeobj.GetBorder("ButtonBorder") )
        self.SetBgColor( schemeobj.GetColor("DarkClayBG", Color(255, 255, 255 ) ) )

        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        
        # Avatar of the player in this slot
        #self.avatarpanel.SetBorder( schemeobj.GetBorder("AvatarBorder") )

        # Name of the player in self slot
        self.slotname.GetMenu().MakeReadyForUse()
        self.slotname.SetBorder(None)
        self.slotname.SetFgColor( schemeobj.GetColor("White", Color(255, 255, 255 ) ) )
        self.slotname.SetBgColor( Color(0, 0, 0, 0) )
        self.slotname.SetFont(hfontmedium)
        
        # Color
        self.color.SetBorder(schemeobj.GetBorder("DepressedBorder"))
        self.color.SetBgColor( Color(0, 0, 0, 255) )
        self.color.SetFgColor( Color(255, 255, 255, 0) )	# hide text
        self.color.GetMenu().SetBgColor( Color(20, 120, 200, 0) )
        
        # Faction/side selection for the player
        self.faction.GetMenu().MakeReadyForUse()
        self.faction.SetBorder(None)
        self.faction.SetFgColor( schemeobj.GetColor("White", Color(255, 255, 255 ) ) )
        self.faction.SetBgColor( Color(0, 0, 0, 0) )
        self.faction.SetFont(hfontmedium)

        # Team selection for the player
        self.team.GetMenu().MakeReadyForUse()
        self.team.SetBorder(None)
        self.team.SetFgColor( schemeobj.GetColor("White", Color(255, 255, 255 ) ) )
        self.team.SetBgColor( Color(0, 0, 0, 0) )
        self.team.SetFont(hfontmedium)

    def PerformLayout(self):
        super(PlayerEntry, self).PerformLayout()
        
        self.avatarpanel.SetSize(64+23, 64)
        pos = (scheme().GetProportionalScaledValueEx( self.GetScheme(), 40 ) /2) - 34
        self.avatarpanel.SetPos( pos-8, pos )
        
        self.slotname.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 75 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 18 ) )
        self.slotname.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 50 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 5 ) )    
                
        self.color.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ) )
        self.color.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 130 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 10 ) )    
                
        self.faction.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 50 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 21 ) )
        self.faction.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 160 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 5 ) )
                
        self.team.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 21 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 21 ) )
        self.team.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 215 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 5 ) )
                
        # Set size/pos ready button
        self.ready.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 40 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 40 ) )
        self.ready.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 240 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 0 ) )
                
    def OnTick(self):
        super(PlayerEntry, self).OnTick()
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
        
        isgamemaster = GameRules().gamemasterindex == player.entindex()
        
        info = GetGamerulesInfo(GameRules().selectedgamerule) if GameRules() else None
        if info:
            supportcpu = info.supportcpu
            supportfactions = info.supportfactions
        else:
            supportcpu = True
            supportfactions = True
            
        # Type changed
        newtype = GameRules().slots[self.idxslot].type
        if self.curtype != newtype or isgamemaster != self.wasgamemaster or supportcpu != self.oldsupportcpu:
            if newtype == GLTYPE_OPEN:
                # Update items slot names
                self.slotname.SetItemEnabled("Open", False)
                self.slotname.SetItemEnabled("Close", isgamemaster)
                self.slotname.SetItemEnabled("Take slot", True)
                self.slotname.SetItemEnabled("Add CPU", isgamemaster and supportcpu)
                self.ClearEntry()
                self.slotname.SetText("Open")  
                self.SetVisible(True)
            elif newtype == GLTYPE_CLOSED:
                self.slotname.SetItemEnabled("Open", isgamemaster)
                self.slotname.SetItemEnabled("Close", False)
                self.slotname.SetItemEnabled("Take slot", isgamemaster)
                self.slotname.SetItemEnabled("Add CPU", isgamemaster and supportcpu)
                self.ClearEntry()
                self.slotname.SetText("Closed")  
                self.SetVisible(True)
            elif newtype == GLTYPE_NOTAVAILABLE:
                self.ClearEntry()
                self.SetVisible(False)
            elif newtype == GLTYPE_HUMAN:
                self.slotname.SetItemEnabled("Open", False)
                self.slotname.SetItemEnabled("Close", False)
                self.slotname.SetItemEnabled("Take slot", False)
                self.slotname.SetItemEnabled("Add CPU", False)    
                self.SetVisible(True)
            elif newtype == GLTYPE_CPU:
                self.slotname.SetItemEnabled("Open", isgamemaster)
                self.slotname.SetItemEnabled("Close", isgamemaster)
                self.slotname.SetItemEnabled("Take slot", isgamemaster)
                self.slotname.SetItemEnabled("Add CPU", False)
                self.slotname.SetText("CPU")
                self.SetVisible(True)
                
        if newtype == GLTYPE_HUMAN:
            self.UpdatePlayerInfo(GameRules().slots[self.idxslot].index, supportfactions)
        elif newtype == GLTYPE_CPU:
            self.UpdateCPUInfo(supportfactions)
            
        self.curtype = newtype
        self.wasgamemaster = isgamemaster
        self.oldsupportcpu = supportcpu
        
    def ClearEntry(self):
        self.curavatar = -1
        self.avatarpanel.SetVisible(False)
        self.slotname.SetText("")
        self.slotname.SetEnabled( True )  
        self.color.SetBgColor(Color(0, 0, 0, 0))
        self.color.SetEnabled( False )
        self.color.SetVisible( False )  
        self.faction.SetText("")
        self.faction.SetEnabled(False)
        self.faction.SetVisible(False)
        self.team.SetText("")
        self.team.SetEnabled( False )
        self.team.SetVisible(False)  
        self.ready.SetVisible(False)      
        
    def UpdatePlayerInfo(self, index, supportfactions):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        islocalplayer = (index == player.entindex())
        localplayerisgamemaster = GameRules().gamemasterindex == player.entindex()
        
        # Get player info
        info = PlayerInfo()
        if not engine.GetPlayerInfo(index, info):
            return
            
        # Update avatar
        if info.friendsID and steamapicontext.SteamFriends() and steamapicontext.SteamUtils():
            steamIDForPlayer = CSteamID( info.friendsID, 1, steamapicontext.SteamUtils().GetConnectedUniverse(), EAccountType.k_EAccountTypeIndividual )

            # See if the avatar's changed
            iAvatar = steamapicontext.SteamFriends().GetFriendAvatar(steamIDForPlayer, EAvatarSize.k_EAvatarSize32x32)
            if self.curavatar != iAvatar:
                self.curavatar = iAvatar
                self.avatarpanel.SetVisible(True)
                self.avatarpanel.SetPlayerIndex(index)
        else:
            self.avatarpanel.SetVisible(False)
        
        # Fill in
        self.slotname.SetText(info.name)
        
        # Update colors
        try:
            color = GL_COLORS[GameRules().slots[self.idxslot].color]
        except KeyError:
            color = Color(0, 0, 0, 0)
        self.color.SetBgColor( color )
        self.color.SetDisabledBgColor( color )
        self.color.SetEnabled( islocalplayer )
        self.color.SetVisible(True)
        
        for color_name, color in GL_COLORS.iteritems():
            self.color.SetItemEnabled( color_name, GameRules().IsColorFree(color_name) )
        
        # Update faction/side
        try:
            factionname = dbfactions[GameRules().slots[self.idxslot].faction].displayname
        except:
            factionname = GameRules().slots[self.idxslot].faction
        self.faction.RemoveActionSignalTarget(self)
        self.faction.SetText(factionname)
        self.faction.AddActionSignalTarget(self)
        self.faction.SetEnabled(islocalplayer and supportfactions)
        self.faction.SetVisible(True)

        # Update team
        self.team.RemoveActionSignalTarget(self)
        self.team.SetText( GL_TEAMSTEXT[GameRules().slots[self.idxslot].team] )
        self.team.AddActionSignalTarget(self)
        self.team.SetEnabled( islocalplayer and self.useteams )
        self.team.SetVisible(True)
        
        # Update ready button
        if islocalplayer and localplayerisgamemaster:
            if self.ready.IsSelected() != True:
                self.ready.RemoveActionSignalTarget(self)
                self.ready.SetSelected( True )
                self.ready.AddActionSignalTarget(self)                
        else:
            if self.ready.IsSelected() != GameRules().slots[self.idxslot].ready:
                self.ready.RemoveActionSignalTarget(self)
                self.ready.SetSelected( GameRules().slots[self.idxslot].ready )
                self.ready.AddActionSignalTarget(self)
        self.ready.SetEnabled( islocalplayer and not localplayerisgamemaster )
        self.ready.SetVisible(True)
        
    def UpdateCPUInfo(self, supportfactions):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        isgamemaster = GameRules().gamemasterindex == player.entindex()    
    
        # Fill in
        self.slotname.SetText("CPU")
        
        # Update colors
        try:
            color = GL_COLORS[GameRules().slots[self.idxslot].color]
        except KeyError:
            color = Color(0, 0, 0, 0)
        self.color.SetBgColor( color )
        self.color.SetDisabledBgColor( color )
        self.color.SetEnabled(isgamemaster)
        self.color.SetVisible(True)
        
        for color_name, color in GL_COLORS.iteritems():
            self.color.SetItemEnabled( color_name, GameRules().IsColorFree(color_name) )
        
        # Update faction/side
        try:
            factionname = dbfactions[GameRules().slots[self.idxslot].faction].displayname
        except:
            factionname = GameRules().slots[self.idxslot].faction
        self.faction.RemoveActionSignalTarget(self)
        self.faction.SetText(factionname)
        self.faction.AddActionSignalTarget(self)
        self.faction.SetEnabled(isgamemaster and supportfactions)
        self.faction.SetVisible(True)

        # Update team
        self.team.RemoveActionSignalTarget(self)
        self.team.SetText( GL_TEAMSTEXT[GameRules().slots[self.idxslot].team] )
        self.team.AddActionSignalTarget(self)
        self.team.SetEnabled( isgamemaster and self.useteams )
        self.team.SetVisible(True)
        
        # Update ready button
        if self.ready.IsSelected() != GameRules().slots[self.idxslot].ready:
            self.ready.RemoveActionSignalTarget(self)
            self.ready.SetSelected( True )
            self.ready.AddActionSignalTarget(self)
        self.ready.SetEnabled( False )
        self.ready.SetVisible(True)    
        
    def OnTextChanged(self, vpanel, data):
        panel = ipanel().GetPanel(vpanel, self.GetModuleName())

        # Now which combobox changed?
        userdata = panel.GetActiveItemUserData()
        if panel == self.slotname:
            engine.ClientCommand('gl_type %s %s' % (userdata, self.idxslot))
        elif panel == self.color:
            engine.ClientCommand('gl_color %s %s' % (userdata, self.idxslot))
        elif panel == self.faction:
            engine.ClientCommand('gl_faction %s %s' % (userdata, self.idxslot))
        elif panel == self.team:
            engine.ClientCommand('gl_team  %s %s' % (userdata, self.idxslot))   
            
    def OnCheckButtonChecked(self):
        engine.ClientCommand('gl_ready %s %s' % (int(not GameRules().slots[self.idxslot].ready), self.idxslot))
        
    def LoadFactions(self):
        info = GetGamerulesInfo(GameRules().selectedgamerule) if GameRules() else None
        self.faction.RemoveAll()
        count = 0
        for k, f in dbfactions.iteritems():
            if info and not info.factionfilter.match(f.name):
                continue
            self.faction.AddItem( f.displayname, f.name )
            count += 1
            
    def InvalidateSlot(self):
        """ Called when the gamerules or gamepackages changed.
            Check if showed options are still valid """
        self.LoadFactions()
        info = GetGamerulesInfo( GameRules().selectedgamerule ) if GameRules() else None
        if info:
            self.useteams = info.useteams
            