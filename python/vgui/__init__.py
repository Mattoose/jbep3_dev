import srcmgr
srcmgr.VerifyIsClient()

__all__ = ['controls']

from _vgui import *
from utils import ScreenWidth, ScreenHeight

#gHUD = GetHud()

def XRES(x): return int( x  * ( ScreenWidth() / 640.0 ) )
def YRES(y): return int( y  * ( ScreenHeight() / 480.0 ) )

# ASW has a new class for hud icons. 
# In 2007 it's still in the Hud object.
try:
    HudIcons
except NameError:
    def HudIcons(): return gHUD
