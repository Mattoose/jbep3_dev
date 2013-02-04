from srcbase import KeyValues, Color, MAX_PLAYERS

from entities import C_HL2WarsPlayer, PlayerResource

from vgui import scheme, ipanel, DataType_t, AddTickSignal, RemoveTickSignal, IsGameUIVisible
from vgui.controls import (Panel, Frame, Label, RichText, TextEntry, Button, ListPanel)
from gamelobby_minimap import GamelobbyMinimap
from input import ButtonCode_t

from gamerules import GameRules
from gameinterface import PlayerInfo, engine
from ..gamelobby_shared import *

from core.gamerules import GetGamerulesInfo
from core.signals import gamepackageloaded, gamepackageunloaded

from gamelobby_settings import SettingsPanel
from gamelobby_playerentry import PlayerEntry

# Chat text entry
class ChatTextEntry(TextEntry):
    def ApplySchemeSettings(self, schemeobj):
        super(ChatTextEntry, self).ApplySchemeSettings(schemeobj)
        self.SetBorder( schemeobj.GetBorder("DepressedBorder") )
        
    def ClearEntry(self):
        self.SetText( "" )
        
    def OnKeyCodeTyped(self, code):
        if code == ButtonCode_t.KEY_ENTER or code == ButtonCode_t.KEY_PAD_ENTER:
            self.PostActionSignal ( KeyValues("NewLineMessage") )
        elif code == ButtonCode_t.KEY_TAB:
            # Ignore tab, otherwise vgui will screw up the focus.
            return
        else:
            super(ChatTextEntry, self).OnKeyCodeTyped(code)
        
class CustomFieldLabel(Label):
    def __init__(self, parent, panelname, text):
        super(CustomFieldLabel, self).__init__(parent, panelname, text)
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
    def ApplySchemeSettings(self, schemeobj):
        super(CustomFieldLabel, self).ApplySchemeSettings(schemeobj)
        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        self.SetFont(hfontmedium)
        self.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        self.SetFgColor(Color(216, 222, 211, 255))
        
# Party leader selection panel
class LeaderSelectionPanel(Frame):
    def __init__(self, parent, panelname):
        super(LeaderSelectionPanel, self).__init__(parent, panelname)
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme( schemeobj )
        self.SetVisible(False)

        self.SetMoveable(True)
        self.SetSizeable(False)
        #self.SetProportional(True)
        self.SetTitleBarVisible( False )
        
        # Player list
        self.playerlist = ListPanel(self, "PartyLeaderPlayerList")
        self.playerlist.SetScheme( schemeobj )
        self.playerlist.SetMultiselectEnabled( False )
        self.playerlist.AddColumnHeader( 0, "name", "Players", 200, ListPanel.COLUMN_RESIZEWITHWINDOW )
    
        self.selectbutton = Button( self, "SelectButton", 'Select' )
        self.selectbutton.SetScheme(schemeobj)
        self.selectbutton.SetCommand('Select')
        self.cancelbutton = Button( self, "CancelButton", 'Cancel' )
        self.cancelbutton.SetScheme(schemeobj)
        self.cancelbutton.SetCommand('Cancel')
        
    def ApplySchemeSettings(self, schemeobj):
        super(LeaderSelectionPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        hfontheadline = schemeobj.GetFont( "HeadlineLarge" )  

        self.SetBorder( schemeobj.GetBorder("ButtonBorder") )
        self.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        
        self.playerlist.SetFont(hfontsmall)
        self.playerlist.SetColumnHeaderHeight( 32 )

        self.selectbutton.SetFont(hfontmedium)
        self.cancelbutton.SetFont(hfontmedium)
        
    def PerformLayout(self):
        super(LeaderSelectionPanel, self).PerformLayout()
        
        self.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 150))        
        self.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 250))   
                     
        self.playerlist.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 5),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 10))
        self.playerlist.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 90),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 215)) 
        self.playerlist.vbar.SetWide(28)   # Temp
        
        # Buttons
        self.selectbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 50),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 230))        
        self.selectbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 45),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
        self.cancelbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 5),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 230))        
        self.cancelbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 45),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
            
    def RefreshPlayers(self):
        self.playerlist.RemoveAll()
        for i in range(1, gpGlobals.maxClients+1):
            info = PlayerInfo()
            if not engine.GetPlayerInfo(i, info):
                continue
            data = KeyValues(info.name, 'name', info.name)
            self.playerlist.AddItem( data, 0, False, True )
               
    def ShowPanel(self, show):
        if self.IsVisible() == show:
            return

        if show:
            self.Activate()
            self.SetMouseInputEnabled( True )
            self.DoModal()
            self.RefreshPlayers()
        else:
            self.SetVisible( False )
            self.SetMouseInputEnabled( False )
            self.CloseModal()
            
    def OnCommand(self, command):
        if command == 'Cancel':
            self.ShowPanel(False)
        elif command == 'Select':
            self.ShowPanel(False)
            itemid = self.playerlist.GetSelectedItem( 0 )
            if itemid != -1:
                playername = self.playerlist.GetItem(itemid).GetString('name')
                engine.ClientCommand('gl_selectleader %s' % (playername))

# The main window
class Gamelobby(Frame):
    def __init__(self):
        super(Gamelobby, self).__init__(None, "Gamelobby")
        
        self.RegMessageMethod( "NewLineMessage", self.OnNewLine )
        
        # Need to keep a variable to know if the panel should be showed
        # In OnTick the visibility is changed when the game ui is on.
        # However this can still mean that we should show the gamelobby.
        self.showpanel = False
        
        self.SetTitle( 'Gamelobby', True )
        self.SetSizeable(False)
        
        # Other useful options
        self.SetMoveable(False)
        self.SetSizeable(False)
        self.SetProportional(True)
        self.SetTitleBarVisible( False )
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme( schemeobj )
        self.SetVisible(False)
        self.SetEnabled(True)
        
        # Add labels to the player box
        self.header = Label(self, "GamelobbyHeader", "")
        self.header.SetText("GameLobby")
        self.header.SetContentAlignment(Label.a_northwest)
        self.playerheader = Label(self, "PlayerHeader", "")
        self.playerheader.SetText("Player")
        self.playerheader.SetContentAlignment(Label.a_northwest)
        self.colorheader = Label(self, "ColorHeader", "")
        self.colorheader.SetText("Color")
        self.colorheader.SetContentAlignment(Label.a_northwest)
        self.factionheader = Label(self, "FactionHeader", "")
        self.factionheader.SetText("Faction")
        self.factionheader.SetContentAlignment(Label.a_northwest)
        self.teamheader = Label(self, "TeamHeader", "")
        self.teamheader.SetText("Team")
        self.teamheader.SetContentAlignment(Label.a_northwest)
        self.readyheader = Label(self, "ReadyHeader", "")
        self.readyheader.SetText("Ready")
        self.readyheader.SetContentAlignment(Label.a_northwest)
        self.spectatorheader = Label(self, "SpectatorsHeader", "")  
        self.spectatorheader.SetText("Spectators")   
        self.spectatorheader.SetContentAlignment(Label.a_northwest)
        self.gamemasterheader = Label(self, "GamemasterHeader", "")  
        self.gamemasterheader.SetText("Gamemaster")   
        self.gamemasterheader.SetContentAlignment(Label.a_northwest)
        
        # Add launch and spectate buttons
        self.launch = Button(self, "LaunchButton", "Launch")
        self.launch.SetScheme(schemeobj)
        self.launch.SetCommand('LaunchGame')
        
        self.leave = Button(self, "LeaveButton", "Leave")
        self.leave.SetScheme(schemeobj)
        self.leave.SetCommand('Leave')

        self.spectate = Button(self, "SpectateButton", "Spectate")
        self.spectate.SetScheme(schemeobj)
        self.spectate.SetCommand('SpectateGame')

        # Spectator list
        self.gamemaster = RichText(self, "GameMasterName")
        self.gamemaster.SetScheme(schemeobj)
        self.spectatorlist = RichText(self, "SpectatorList")
        self.spectatorlist.SetScheme(schemeobj)

        # Setup settings box
        self.settingsbox = Panel( self, "SettingsArea" )
        self.settingsbox.SetScheme(schemeobj)
        self.settingsbox.SetZPos(-1)        
        
        self.minimap = GamelobbyMinimap(self, 'MiniMap', True)
        self.minimap.SetScheme(schemeobj)
        self.minimap.SetVisible(True) 

        self.mapname = RichText(self, 'MapName')
        self.mapname.SetScheme(schemeobj)
        self.mapname.SetVerticalScrollbar(False)
        self.gamerules = RichText(self, 'MapName')
        self.gamerules.SetScheme(schemeobj)
        self.gamerules.SetVerticalScrollbar(False)
  
        self.partyleaderbutton = Button(self, "PartyLeader", "Select leader")
        self.partyleaderbutton.SetScheme(schemeobj)  
        self.partyleaderbutton.SetCommand('LeaderSelection')
        self.settingsbutton = Button(self, "ChangeSettingsButton", "Settings")
        self.settingsbutton.SetScheme(schemeobj)
        self.settingsbutton.SetCommand('ChangeSettings')
        
        self.leaderselection = LeaderSelectionPanel(self, 'LeaderSelectionPanel')
        self.settingspanel = SettingsPanel(self, 'SetttingsPanel')
        
        # Description area
        self.descriptionpanel = Panel(self, 'DescriptionPanel')
        self.descriptionpanel.SetScheme(schemeobj)
        self.descriptionpanel.SetZPos(-1)
        
        self.description = RichText(self.descriptionpanel, "Description")
        self.description.SetScheme(schemeobj)
        self.description.SetVerticalScrollbar(False)
        
        # Setup the chat things
        self.chatboxpanel = Panel(self, "ChatBoxPanel")
        self.chatboxpanel.SetScheme(schemeobj)
        self.chatboxpanel.SetZPos(-1)
        
        self.chatbox = ChatTextEntry(self, "ChatBoxEntry")
        self.chatbox.SetScheme(schemeobj)
        self.chatbox.AddActionSignalTarget(self)
        self.chatbox.SendNewLine(True) # with the txtEntry Type you need to set it to pass the return key as a message
        self.chatbox.SetCatchEnterKey(True)
       	self.chatbox.SetMultiline(False)
        self.chatbox.SetEditable(True)

        self.chathistory = RichText(self, "ChatHistory")
        self.chathistory.SetScheme(schemeobj)
        
        self.sendbutton = Button(self, "SendButton", "Send")
        self.sendbutton.SetScheme(schemeobj)
        self.sendbutton.SetCommand('SendChat')
        
        # Setup the player area
        self.playerbox = Panel(self, "PlayerArea")
        self.playerbox.SetScheme(schemeobj)
        self.playerbox.SetZPos(-1)
        
        self.RefreshCustomFields()
        
        # Create player entries
        self.playerentries = []
        for i in range(0, MAXPLAYERS):
            self.playerentries.append( PlayerEntry(self, 'player_entry_%d' % (i), i) )

    def ApplySchemeSettings(self, schemeobj):
        super(Gamelobby, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont('FriendsSmall')
        hfontmedium = schemeobj.GetFont('FriendsMedium')
        hfontheadline = schemeobj.GetFont('HeadlineLarge')
        
        #self.SetBgColor( schemeobj.GetColor("Black", Color(255, 255, 255, 0 ) ) )
        self.SetBgColor( Color(255, 255, 255, 0 ) )
        
        self.playerbox.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.playerbox.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.descriptionpanel.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.descriptionpanel.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.chatboxpanel.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.chatboxpanel.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.settingsbox.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.settingsbox.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.partyleaderbutton.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.partyleaderbutton.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.settingsbutton.SetBorder(schemeobj.GetBorder("ButtonBorder") )
        self.settingsbutton.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        
        # Headers
        self.header.SetFont(hfontheadline)
        self.header.SizeToContents()
        self.playerheader.SetFont(hfontsmall)
        self.playerheader.SizeToContents()
        self.colorheader.SetFont(hfontsmall)
        self.colorheader.SizeToContents()
        self.factionheader.SetFont(hfontsmall)
        self.factionheader.SizeToContents()
        self.teamheader.SetFont(hfontsmall)
        self.teamheader.SizeToContents()
        self.readyheader.SetFont(hfontsmall)
        self.readyheader.SizeToContents()
        self.spectatorheader.SetFont(hfontsmall)
        self.spectatorheader.SizeToContents()     
        self.gamemasterheader.SetFont(hfontsmall)
        self.gamemasterheader.SizeToContents()   

        self.launch.SetFont(hfontmedium)
        self.leave.SetFont(hfontmedium)
        self.spectate.SetFont(hfontmedium)

        self.spectatorlist.SetFont(hfontmedium)
        self.spectatorlist.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 255, 0 ) ) )
        self.spectatorlist.SetVerticalScrollbar(False)        
        self.gamemaster.SetFont(hfontmedium)
        self.gamemaster.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 255, 0 ) ) )
        self.gamemaster.SetVerticalScrollbar(False)   
        
        self.HEADERCOLOR = schemeobj.GetColor("Blank", Color(255, 255, 255, 0 ) )
        
        self.chatbox.SetFont(hfontmedium)
        self.chathistory.SetFont(hfontmedium)
        self.sendbutton.SetFont(hfontmedium)
    
        # Settings box
        self.minimap.SetBorder(schemeobj.GetBorder("DepressedBorder") )
        self.mapname.SetFont(hfontheadline)
        self.mapname.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        self.gamerules.SetFont(hfontmedium)
        self.gamerules.SetBgColor( schemeobj.GetColor("Blank", Color(255, 255, 0 ) ) )
        self.gamerules.SetFgColor(Color(216, 222, 211, 255))
        
        self.partyleaderbutton.SetFont(hfontmedium)
        self.settingsbutton.SetFont(hfontmedium)
        
        # Description area
        self.description.SetBgColor( schemeobj.GetColor("ClayBG", Color(255, 255, 255 ) ) )
        self.description.SetFont(hfontmedium)
        
    def PerformLayout(self):
        super(Gamelobby, self).PerformLayout()
       
        # Main size
        wide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 640)
        tall = scheme().GetProportionalScaledValueEx(self.GetScheme(), 480) 
        self.SetSize(wide, tall)  
        self.MoveToCenterOfScreen()        

        # Player area
        self.playerbox.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 10),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 10))        
        self.playerbox.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 290),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 460))   

        for i in range(0, MAXPLAYERS):
            self.playerentries[i].SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 40+i*40 ) )      
            self.playerentries[i].SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 270 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 40 ) )
     
        # Headers     
        # This doesn't looks very nice
        self.header.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 15))        
        self.header.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 24))    
        self.playerheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 70),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))        
        self.playerheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
        self.colorheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 150),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))        
        self.colorheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
        self.factionheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 180),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))        
        self.factionheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))    
        self.teamheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 235),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))        
        self.teamheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14)) 
        self.readyheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 260),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))        
        self.readyheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))      
        self.spectatorheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 400))        
        self.spectatorheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))                
        self.gamemasterheader.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 370))        
        self.gamemasterheader.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
                     
        # Some buttons
        self.launch.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 230),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 440))        
        self.launch.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 65),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))   
        self.leave.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 150),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 440))        
        self.leave.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 65),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))          
        self.spectate.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 440))        
        self.spectate.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 65),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))     
        self.spectatorlist.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 410))        
        self.spectatorlist.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 250),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))                       
        self.gamemaster.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 20),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 380))        
        self.gamemaster.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 250),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))
     
        # Settings area
        self.settingsbox.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 310),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 10))        
        self.settingsbox.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 130))       

        self.minimap.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 40))        
        self.minimap.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 95),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 95))                            
       
        self.mapname.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 15))        
        self.mapname.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))       
                     
        self.gamerules.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 425),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 40))        
        self.gamerules.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 10))       

        self.partyleaderbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 425),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 121))        
        self.partyleaderbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 75),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))              
        self.settingsbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 425),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 103))        
        self.settingsbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 75),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
                     
        # Description area
        self.descriptionpanel.SetPos(scheme().GetProportionalScaledValueEx(self.GetScheme(), 310),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 150))        
        self.descriptionpanel.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 90))
                     
        self.description.SetPos(scheme().GetProportionalScaledValueEx(self.GetScheme(), 10),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 10))        
        self.description.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 300),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 70))
        
                     
        # Elements chat
        self.chatboxpanel.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 310),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 250))        
        self.chatboxpanel.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 220))              
        self.chathistory.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 260))        
        self.chathistory.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 300),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 180))
        self.chatbox.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 320),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 446))        
        self.chatbox.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 250),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))  
        self.sendbutton.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 575),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 446))        
        self.sendbutton.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 45),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 14))
                     
        # Custom fields
        ystart = 54
        yincr = 14
        for cf in self.customfields.itervalues():
            cf.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 428),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), ystart))   
            ystart += yincr                        
        
    def ShowPanel(self, show):
        if self.showpanel == show:
            return
        self.showpanel = show
        
        if show:
            self.Activate()
            self.SetMouseInputEnabled( True )
            
            # Add ticks
            # Update 1/10 per second
            AddTickSignal( self.GetVPanel(), 100 )
            for pe in self.playerentries:
                AddTickSignal( pe.GetVPanel(), 100 )  
            gamepackageloaded.connect(self.OnGamePackageChanged)
            gamepackageunloaded.connect(self.OnGamePackageChanged)
        else:
            self.SetVisible( False )
            self.SetMouseInputEnabled( False )
            
            RemoveTickSignal( self.GetVPanel() )
            for pe in self.playerentries:
                RemoveTickSignal( pe.GetVPanel() )
            gamepackageloaded.disconnect(self.OnGamePackageChanged)
            gamepackageunloaded.disconnect(self.OnGamePackageChanged)
    def OnNewLine(self):
        if self.chatbox.HasFocus():
            self.Send()
            
    def Send(self):
        text = self.chatbox.GetText()
        
        engine.ServerCommand( 'say ' + text )
        
        self.chatbox.ClearEntry()
        
    def PrintChat(self, playerindex, filter, msg):
        if playerindex == 0:
            msg = 'Console : %s' % (msg)
        # Temp parse left of string <- :
        # Color it
        say = msg.partition(':')
        self.chathistory.InsertColorChange( Color(153, 204, 255, 255) )
        self.chathistory.InsertString( say[0] )
        self.chathistory.InsertColorChange( Color(255, 255,255,255) )
        self.chathistory.InsertString( say[1] + say[2] + '\n' )    
        
    # Do not use the Frame OnThink
    # It invalidates the layout and gives us behavior we don't want
    def OnThink(self):
        pass
        
    def OnTick(self):
        if IsGameUIVisible() and self.IsVisible():
            self.SetVisible(False)
        elif not IsGameUIVisible() and not self.IsVisible():
            self.SetVisible(True)
    
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
        slotlocal = GameRules().FindSlotPlayerByIndex(player.entindex())
        isspectator = player.GetTeamNumber() == TEAM_SPECTATOR
        isgamemaster = player.entindex() == GameRules().gamemasterindex
        
        # Update state buttons
        self.sendbutton.SetEnabled( self.chatbox.GetTextLength() != 0 )
        self.launch.SetEnabled( isgamemaster )
        self.partyleaderbutton.SetEnabled( isgamemaster )
        self.settingsbutton.SetEnabled( isgamemaster )
        
        # Update name gamemaster
        if GameRules().gamemasterindex != None:
            info = PlayerInfo()
            if engine.GetPlayerInfo(GameRules().gamemasterindex, info):   
                self.gamemaster.SetText( "" )   
                self.gamemaster.InsertColorChange( Color(0, 180, 247, 200) ) 
                self.gamemaster.InsertString( info.name )   
        else:
            self.gamemaster.SetText( "" )   
            self.gamemaster.InsertColorChange( Color(255, 0, 0, 200) ) 
            self.gamemaster.InsertString( 'Nobody... first slot taker becomes gamemaster!' )
        
        # Rebuild spectator list
        self.spectatorlist.SetText("")
        self.spectatorlist.InsertColorChange( Color(255, 255, 0, 200) )
        sep = False
        for i in range(1, gpGlobals.maxClients+1):
            #print 'i: ' + str(i) + ' team: ' + str(PlayerResource().GetTeam(i))
            if not (PlayerResource().GetTeam(i) == TEAM_SPECTATOR):
                continue

            info = PlayerInfo()
            if not engine.GetPlayerInfo(i, info):
                continue

            if sep:
                self.spectatorlist.InsertColorChange( self.HEADERCOLOR )
                self.spectatorlist.InsertString(", ")
            self.spectatorlist.InsertColorChange( Color(255, 255, 0, 200) )
            self.spectatorlist.InsertString(info.name)
            sep = True
        
    def OnCommand(self, command):
        if command == 'SpectateGame':
            engine.ClientCommand('gl_spectate')
        elif command == 'LaunchGame':
            engine.ClientCommand('gl_launch')
        elif command == 'Leave':
            self.ShowPanel(False)
            engine.ClientCommand( 'disconnect' )
        elif command == 'SendChat':
            self.Send()
        elif command == 'ChangeSettings':
            self.settingspanel.ShowPanel(True)
        elif command == 'LeaderSelection':
            self.leaderselection.ShowPanel(True)
        elif command.startswith('BPosition_'):
            player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
            slotlocal = GameRules().FindSlotPlayerByIndex(player.entindex())
            if slotlocal != -1:
                engine.ClientCommand('gl_position ' + command[-1] + ' ' + str(slotlocal))
        else:
            super(Gamelobby, self).OnCommand(command)
            
    def OnGamePackageChanged(self, sender, packagename, **kwargs):
        # For each player entry reload the factions
        for s in self.playerentries:
            s.LoadFactions()
        # For the settings panel, reload the gamerules
        self.settingspanel.LoadGamerules()
        self.SettingsChanged()
        
    def InvalidateSlots(self):
        #info = GetGamerulesInfo( GameRules().selectedgamerule ) if GameRules() else None
        #if info:
        #    self.teamheader.SetVisible(info.useteams)
        for slot in self.playerentries:
            slot.InvalidateSlot()
        
    def PositionChanged(self, slotidx, oldposition, newposition):
        self.minimap.UpdatedPositionImages(slotidx, oldposition, newposition)
            
    def SettingsChanged(self):
        info = GetGamerulesInfo(GameRules().selectedgamerule)
        if not info:
            gamerulesname = GameRules().selectedgamerule
            description = 'Error retrieving gamerules description'
        else:
            gamerulesname = info.displayname
            description = info.description
    
        mapname = str(GameRules().selectedmap)
    
        self.mapname.SetText('')
        self.mapname.InsertString('Map: %s' % (mapname)) 
        self.gamerules.SetText('')
        self.gamerules.InsertString('Gamerules: %s' % (gamerulesname))
        self.minimap.SetMap(mapname, info)
        
        self.description.SetText('')
        self.description.InsertColorChange(Color(255, 255, 255, 255))
        self.description.InsertString('%s' % (gamerulesname))
        self.description.InsertColorChange(Color(220, 220, 220, 255))
        self.description.InsertIndentChange(5)
        self.description.InsertString('\n')
        self.description.InsertString(description)
        
        self.RefreshCustomFields()
        self.InvalidateSlots()
        
    def UpdateCustomField(self, name, value):
        if name in self.customfields:
            self.customfields[name].SetText('%s: %s' % (name, value))
        
    def ParseCustomField(self, type, name, default_value, values):
        hscheme = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        schemeobj = scheme().GetIScheme(hscheme)
        header = CustomFieldLabel(self, name, name)
        header.name = name
        header.SetPos(5, 0)
        header.SetText('%s: %s' % (name, default_value) )
        header.SizeToContents()
        header.ApplySchemeSettings(schemeobj)
        header.Repaint()
        return header
        
    def RefreshCustomFields(self):
        self.customfields = {}
        info = GetGamerulesInfo(GameRules().selectedgamerule)
        if not info:
            return
        try:
            cflist = info.cls.GetCustomFields()
        except:
            return
        for name, v in cflist.iteritems():
            self.customfields[name] = self.ParseCustomField(v[0], name, v[1], v[2:len(v)])
        self.InvalidateLayout()
        
