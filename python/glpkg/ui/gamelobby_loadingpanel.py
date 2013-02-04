""" A panel that shows the list of players participating in a game launched from the gamelobby """
from srcbase import KeyValues, Color
from vgui import scheme
from vgui.controls import Panel, Label, SectionedListPanel

class GLLoadingPanel(Panel):
    def __init__(self):
        super(GLLoadingPanel, self).__init__(None, "GLLoadingPanel")
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
        self.SetPaintBackgroundEnabled(False)
        
        self.countdowntime = None
        self.loadtimeout = None
        
        # Header
        self.header = Label(self, "GLLoadingPanelHeader", "")
        self.header.SetText("")
        self.header.SetContentAlignment(Label.a_northwest)        
        
        # Player list
        self.sectionid = 0
        self.playerlist = SectionedListPanel(self, "PlayerList")
        self.playerlist.SetVerticalScrollbar(False)

        hfontsmall = scheme().GetIScheme(schemeobj).GetFont("FriendsSmall")
        
        self.playerlist.AddSection(self.sectionid, "", None)
        self.playerlist.SetSectionAlwaysVisible(self.sectionid)
        self.playerlist.AddColumnToSection(self.sectionid, "name", "PlayerName", 0, scheme().GetProportionalScaledValueEx( self.GetScheme(),100), hfontsmall )
        self.playerlist.AddColumnToSection(self.sectionid, "status", "PlayerStatus", 0, scheme().GetProportionalScaledValueEx( self.GetScheme(),100), hfontsmall ) 
        
    def GetCountDownTime(self):
        return max(0, int(self.countdowntime - gpGlobals.curtime))
        
    def Paint(self):
        if self.countdowntime:
            self.header.SetText("Commencing game in %d seconds..." % self.GetCountDownTime())
    
        super(GLLoadingPanel, self).Paint()
        
    def ApplySchemeSettings(self, schemeobj):
        super(GLLoadingPanel, self).ApplySchemeSettings(schemeobj)
        
        self.hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        self.hfontmedium = schemeobj.GetFont( "FriendsMedium" )
        self.hfontheadLine = schemeobj.GetFont( "HeadlineLarge" )   

        self.header.SetFont(self.hfontheadLine)
        
        self.playerlist.SetFontSection(self.sectionid, self.hfontmedium)
        
        for item in self.playerlist.items:
            item.SetFont(self.hfontheadLine)
        
    def PerformLayout(self): 
        super(GLLoadingPanel, self).PerformLayout()
        
        self.header.SetWide(self.GetWide())
        
        self.playerlist.SetPos(0, int(self.GetTall()*.1))
        self.playerlist.SetSize( self.GetWide(), int(self.GetTall()*.9) ) 
        
        for item in self.playerlist.items:
            item.SetFont(self.hfontheadLine)
            
glloadingdialog = GLLoadingPanel()
