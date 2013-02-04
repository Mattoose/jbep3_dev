import srcmgr
from vgui import scheme
from vgui.controls import ImagePanel, BitmapButton, BitmapImage
from vgui.baseminimap import BaseMinimap
from ..gamelobby_shared import *
from gamerules import GameRules
import readmap

NUMBERPOSITIONS = MAXPLAYERS+1

class GamelobbyMinimap(BaseMinimap):
    """ Minimap for the in gamelobby """
    def __init__(self, parent, panelname, clickablepositions):
        super(GamelobbyMinimap, self).__init__(parent, panelname, registerlisteners=False, bsetmap=False)
        self.minimapimage = None
        self.mapentry = None
        self.followangle = False
        self.baserotation = 0.0
        self.imagepanel = ImagePanel(self, "BackGround")
        self.imagepanel.SetZPos(-1)

        # create position buttons
        self.positions = [None]*MAXPLAYERS
        for i in range(0, MAXPLAYERS):
            command = 'BPosition_'+str(i)

            self.positions[i] = BitmapButton(self, "button_position", "") 
            self.positions[i].SetVisible(False)
            if clickablepositions:
                self.positions[i].AddActionSignalTarget(parent)
                self.positions[i].SetCommand(command)
            self.positions[i].MakeReadyForUse()
            
        self.SetMap(srcmgr.levelname)

        # Create position buttons
        self.imagepositions = [None]*NUMBERPOSITIONS
        self.imagepositions[0] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_one.vmt")
        self.imagepositions[1] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_two.vmt")
        self.imagepositions[2] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_three.vmt")
        self.imagepositions[3] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_four.vmt")
        self.imagepositions[4] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_five.vmt")
        self.imagepositions[5] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_six.vmt")
        self.imagepositions[6] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_seven.vmt")
        self.imagepositions[7] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_eight.vmt")
        self.imagepositions[8] = BitmapImage( self.positions[0].GetVPanel(), "VGUI/buttons/position_blank.vmt")
        
    def ApplySchemeSettings(self, schemeobj):
        super(GamelobbyMinimap, self).ApplySchemeSettings(schemeobj)
        for i in range(0, MAXPLAYERS):
            self.positions[i].SetAllImages(self.imagepositions[8], Color(255, 255, 255, 255))
            self.positions[i].SetPaintBackgroundEnabled(False)
            self.positions[i].SetPaintBorderEnabled(False)
            self.positions[i].SetSize(scheme().GetProportionalScaledValueEx( self.GetScheme(), 16 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 16 ))
                
    def PerformLayout(self):
        super(GamelobbyMinimap, self).PerformLayout()
        
        w, h = self.GetSize()
        self.imagepanel.SetSize(w, h)
        
        # Correct the positions on the minimap
        if self.mapentry:
            for i in range(0, MAXPLAYERS):
                if not self.mapentry.positionavailable[i]:
                    self.positions[i].SetVisible(False)     
                    continue
                position = readmap.StringToVector( self.mapentry.positionorigin[i] )
                pos2D = self.MapToPanel( self.WorldToMap( position ) )

                self.positions[i].SetPos( int(pos2D.x-self.positions[i].GetWide()/2.0), int(pos2D.y-self.positions[i].GetTall()/2.0) )
                self.positions[i].SetVisible(True)
        else:
            for i in range(0, MAXPLAYERS):
                self.positions[i].SetVisible(False)   
                
    def SetMap(self, mapname, info=None):
        super(GamelobbyMinimap, self).SetMap(mapname)
        
        if self.minimap_material == None:
            self.minimapimage = None
            self.imagepanel.SetImage(None) 
        else:
            self.minimapimage = BitmapImage(self.GetVPanel(), self.minimap_material)
            self.imagepanel.SetImage(self.minimapimage)   
        
        # Get map entry from gamerules
        if info and info.hidestartspots:
            self.mapentry = None
        else:
            self.mapentry = GameRules().maplist.get(mapname, None)
        self.PerformLayout()   
        
    def UpdatedPositionImages(self, slotidx, oldposition, newposition):
        if oldposition != INVALID_POSITION:
            self.positions[oldposition].SetAllImages( self.imagepositions[8], Color(255, 255, 255, 255) )
        if newposition != INVALID_POSITION:
            self.positions[newposition].SetAllImages( self.imagepositions[slotidx], Color(255, 255, 255, 255) )
            