from vgui.controls import Panel
from vgui import surface, WarsVGUIScreen
from utils import MainViewUp, MainViewRight, MainViewForward
from vmath import QAngle, VectorAngles
from te import ClientSideEffect

class UnitBar(Panel):
    def __init__(self, barcolor, fillcolor, outlinecolor):
        super(UnitBar, self).__init__()
    
        self.barcolor = barcolor
        self.fillcolor = fillcolor
        self.outlinecolor = outlinecolor
        
    def Paint(self):
        barfilled = int(self.weight * self.GetTall())
    
        # draw bar part
        surface().DrawSetColor( self.barcolor )
        surface().DrawFilledRect(
            0, 
            0, 
            self.GetWide(), 
            barfilled
        )

        # Draw filler part
        surface().DrawSetColor( self.fillcolor )
        surface().DrawFilledRect(
            0, 
            barfilled, 
            self.GetWide(), 
            self.GetTall()
        )

        # draw the outline of the healthbar
        surface().DrawSetColor( self.outlinecolor )
        surface().DrawOutlinedRect(
            0, 
            0, 
            self.GetWide(), 
            self.GetTall() 
        )
        
    weight = 1.0
    
class UnitBarRenderer(ClientSideEffect):
    def __init__(self, screen):
        super(UnitBarRenderer, self).__init__('UnitBarRenderer')
        self.screen = screen
    def Draw(self, frametime):
        if not self.IsActive():
            return
        self.screen.Draw()
        
class BaseScreen(WarsVGUIScreen):
    def __init__(self):
        super(BaseScreen, self).__init__()

        self.renderer = UnitBarRenderer(self)
        
    def Shutdown(self):
        self.renderer.Destroy()
        self.renderer.screen = None
        self.renderer = None
        self.SetPanel(None)
        
class UnitBarScreen(BaseScreen):
    def __init__(self, unit, barcolor, fillcolor, outlinecolor, offsety=0.0, worldsizey=3.0, worldbloatx=0.0, panel=None):
        super(UnitBarScreen, self).__init__()

        if not panel: panel = UnitBar(barcolor, fillcolor, outlinecolor)
        self.SetPanel(panel)
        self.unit = unit.GetHandle()
        self.offsety = offsety
        self.worldsizey = worldsizey
        self.worldbloatx = worldbloatx
        
        mins = self.unit.WorldAlignMins()
        maxs = self.unit.WorldAlignMaxs()
    
        wide = maxs.x - mins.x + 8.0 + self.worldbloatx
        self.SetWorldSize(self.worldsizey, wide)

        #scaleup = 640/wide
        #self.GetPanel().SetBounds(0, 0, int(3*scaleup), int((maxs.x - mins.x + 8.0)*scaleup))
        self.GetPanel().SetBounds(0, 0, 640, 1024)

    def Draw(self):
        maxs = self.unit.WorldAlignMaxs()
        
        origin = self.unit.GetAbsOrigin() + MainViewRight()*(self.GetHeight()/2)
        origin.z += maxs.z
        origin += MainViewUp()*(8.0 + self.offsety)
        self.SetOrigin( origin )
        
        angles = QAngle()
        dir = MainViewUp()
        VectorAngles(dir, angles)
        self.SetAngles(angles)
    
        super(UnitBarScreen, self).Draw()
        
                