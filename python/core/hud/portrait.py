from srcbase import Color
from vgui import surface, AddTickSignal, HudIcons, vgui_input
from vgui.controls import Panel, VideoGeneralPanel
from entities import C_HL2WarsPlayer
from core.dispatch import receiver
from core.signals import selectionchanged
 
class BaseHudPortrait(Panel):
    def __init__(self, parent):    
        super(BaseHudPortrait, self).__init__(parent, "BaseHudPortrait")
        
        self.EnableSBuffer(True)
        self.SetPaintBackgroundEnabled(True)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)
        self.SetVisible(True)
        
        self.portrait = VideoGeneralPanel(self, "Portrait")
        self.portrait.SetLooped(True)
        
        self.SetZPos(-10)
        self.portrait.SetZPos(-10)
        
        # Crop the video, since we can only use 320x200 and some other resolutions
        # This means the video is about 195 too wide, so we cut off 97,5 pixels from each side
        self.portrait.SetCropVideo(0.3046875, 0.3046875, 0.0, 0.0)
        
        self.OnSelectionChanged = receiver(selectionchanged)(self.OnSelectionChanged)
        
    def UpdateOnDelete(self):
        selectionchanged.disconnect(self.OnSelectionChanged)
        self.portrait.StopVideo()
        
    def ApplySchemeSettings(self, schemeobj):
        super(BaseHudPortrait, self).ApplySchemeSettings(schemeobj)

        self.portrait.SetBgColor(Color(200,100,0,100))
        
        # load background texture
        self.backgroundtextureid = HudIcons().GetIcon(self.backgroundtexture)
        
    def PerformLayout(self):
        super(BaseHudPortrait, self).PerformLayout()
        
        self.portrait.SetSize(self.GetWide(), self.GetTall())
        
    def OnSelectionChanged(self, player, **kwargs):
        if not player.CountUnits():
            if self.curunitname:
                self.portrait.StopVideo()
                self.curunitname = None
                self.unit = None
            return
            
        unit = player.GetUnit(0)
        info = unit.unitinfo
        self.unit = unit
        if info.name == self.curunitname:
            return
            
        if self.curunitname:
            self.portrait.StopVideo()
            
        self.curunitname = info.name
        
        if not info.portrait:
            self.portrait.StopVideo()
            return
        
        self.portrait.SetVideo(info.portrait)

        self.FlushSBuffer() # Trigger Paint() in Python

    def PaintBackground(self):
        """ Draw that thing behind the portrait """
        #if self.backgroundtextureid < 0:
        #    return
        #surface().DrawSetColor(255,255,255, 255)
        #surface().DrawSetTexture(self.backgroundtextureid)
        #surface().DrawTexturedRect(0, 0, self.GetWide(), self.GetTall())
        w, h = self.GetSize()
        self.backgroundtextureid.DrawSelf(0, 0, w, h, Color(255,255,255,255))
        
    def OnMousePressed(self, code):
        # lock mouse input to going to this button
        vgui_input().SetMouseCapture(self.GetVPanel())
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
            
        if self.unit:
            player.CamFollowEntity(self.unit)
        
    def OnMouseReleased(self, code):
        # ensure mouse capture gets released
        vgui_input().SetMouseCapture(0)
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
            
        player.CamFollowEntity(None)
            
    curunitname = None
    backgroundtexture = 'hud_classic_portrait'
    unit = None
    