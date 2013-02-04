from srcbase import HIDEHUD_STRATEGIC, Color, KeyValues
from vgui import CHudElement, GetClientMode, scheme, XRES, YRES, HudIcons, surface, AddTickSignal, GetAnimationController
from vgui.controls import Panel, Label, AnimationController
from utils import ScreenWidth, ScreenHeight
from core.hud import HudInfo
from core.factions import GetFactionInfo
from core.resources import resources
from entities import C_HL2WarsPlayer
from core.units import unitpopulationcount, GetMaxPopulation
from gameinterface import ConVarRef

# Hud default main parts
from core.hud import (BaseHudAbilities, HudUnitsContainer, BaseHudPortrait, AbilityButton,
                      AbilityHudInfo, BaseHudMinimap, BaseHudUnits, BaseHudGroups)
                      
cl_teamcolor_relationbased = ConVarRef('cl_teamcolor_relationbased')

class BackgroundPanel(Panel):
    def __init__(self, parent, panelname):
        super(BackgroundPanel, self).__init__(parent, panelname)
        
        self.SetPaintBackgroundEnabled(True)
        self.background = HudIcons().GetIcon(self.backgroundtexture)

    def PaintBackground(self):
        if self.background:
            w, h = self.GetSize()
            self.background.DrawSelf(0, 0, w, h, self.drawcolor)
            
    background = None
    backgroundtexture = None
    drawcolor = Color(255, 255, 255, 255)
    
class TopPanel(Panel):
    def __init__(self, parent, panelname):
        super(TopPanel, self).__init__(parent, panelname)

        #self.SetPaintBackgroundEnabled(True)
        
    def ApplySchemeSettings(self, schemeobj):
        super(TopPanel, self).ApplySchemeSettings(schemeobj)
        
        self.background = HudIcons().GetIcon(self.backgroundtexture)

    def Paint(self):
        if self.background:
            w, h = self.GetSize()
            self.background.DrawSelf(0, 0, w, h, self.drawcolor)
            
    def OnMouseReleased(self, code):
        # let parent deal with it
        self.CallParentFunction(KeyValues("MouseReleased", "code", code))
        
    def OnMousePressed(self, code):
        # let parent deal with it
        self.CallParentFunction(KeyValues("MousePressed", "code", code))
        
    def OnMouseDoublePressed(self, code):
        self.CallParentFunction(KeyValues("MouseDoublePressed", "code", code))
        
    background = None
    backgroundtexture = None
    drawcolor = Color(255, 255, 255, 255)
    
class HudMinimapSection(BackgroundPanel):
    def __init__(self, parent):
        super(HudMinimapSection, self).__init__(parent, 'HudMinimapSection')
        
        self.SetProportional(True)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(False)
        
        self.minimap = BaseHudMinimap(parent)
        
        self.teamcolorbutton = AbilityButton(parent, 'teamcolortoggle')
        self.teamcolorbutton.SetAllImages(HudIcons().GetIcon(self.teamcolorbuttontexture), Color(255, 255, 255, 255))
        self.teamcolorbutton.SetImage(self.teamcolorbutton.BUTTON_ENABLED_MOUSE_OVER, HudIcons().GetIcon(self.teamcolorbuttonhovertexture), Color(255, 255, 255, 255))
        self.teamcolorbutton.SetCommand('teamcolortoggle')
        self.teamcolorbutton.AddActionSignalTarget(self)
        self.teamcolorbutton.SetMouseInputEnabled(True)
        self.teamcolorbutton.SetVisible(True)
        self.teamcolorbutton.SetZPos(10)
        self.teamcolorbutton.SetEnabled(True)
        
    def SetVisible(self, visible):
        super(HudMinimapSection, self).SetVisible(visible)
        if self.minimap:
            self.minimap.SetVisible(visible)
        if self.teamcolorbutton:
            self.teamcolorbutton.SetVisible(visible)
            
    def UpdateOnDelete(self):
        if self.minimap:
            self.minimap.DeletePanel()
            self.minimap = None
        if self.teamcolorbutton:
            self.teamcolorbutton.DeletePanel()
            self.teamcolorbutton = None
        
    def PerformLayout(self):
        super(HudMinimapSection, self).PerformLayout()
        
        x, y = self.GetPos()
        self.minimap.SetPos(x+int(0.0693069307*self.GetWide()), y+int(0.0891304348*self.GetTall()))
        self.minimap.SetSize(int(0.782178218*self.GetWide()), int(0.852173913*self.GetTall()))

        wide, tall = self.GetSize()
        self.teamcolorbutton.SetPos(x+int(wide*0.85), y+int(tall*0.15))
        self.teamcolorbutton.SetSize(int(wide*0.1), int(tall*0.1))
        
    def OnCommand(self, command):
        if command == 'teamcolortoggle':
            cl_teamcolor_relationbased.SetValue(not cl_teamcolor_relationbased.GetBool())
            return True
        return super(HudMinimapSection, self).OnCommand(command)
        
    backgroundtexture = 'hud_rebels_minimap'
    teamcolorbuttontexture = 'hud_rebels_button_toggleteamcolor'
    teamcolorbuttonhovertexture = 'hud_rebels_button_toggleteamcolorhover'
    
class HudPopulationSection(BackgroundPanel):
    def __init__(self, parent):
        super(HudPopulationSection, self).__init__(parent, 'HudPopulationSection')
        
        self.amountunits = Label(self,"UnitsAmount","")
        self.amountunits.MakeReadyForUse()
        self.amountunits.SetScheme(scheme().LoadSchemeFromFile("resource/ClientScheme.res", "ClientScheme"))
        self.amountunits.SetPaintBackgroundEnabled(False)
        self.amountunits.SetPaintBorderEnabled(False)
        self.amountunits.SetContentAlignment(Label.a_west)

        AddTickSignal(self.GetVPanel(), 250)
        
    def PerformLayout(self):
        super(HudPopulationSection, self).PerformLayout()
        
        margintop = scheme().GetProportionalScaledValueEx(self.GetScheme(), 10)
        marginleft = scheme().GetProportionalScaledValueEx(self.GetScheme(), 25)
        self.amountunits.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 50), 
            scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))
        self.amountunits.SetPos(marginleft, margintop)
                
    def OnTick(self):
        super(HudPopulationSection, self).OnTick()
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
        # update amount of units
        ownernumber = player.GetOwnerNumber()
        pop = unitpopulationcount[ownernumber]
        maxpop = GetMaxPopulation(ownernumber)
        self.amountunits.SetText('%s / %s' % (pop, maxpop))
        if pop > maxpop:
            self.amountunits.SetFgColor(Color(255, 0, 0, 255))
        else:
            self.amountunits.SetFgColor(Color(255, 255, 255, 255))
            
    backgroundtexture = 'hud_rebels_population'
    
class HudResourceSection(BackgroundPanel):
    def __init__(self, parent):
        super(HudResourceSection, self).__init__(parent, 'HudResourceSection')
        
        self.resources = []
        for i in range(0, 3):
            l = Label(self, "ResourcesAmount", "")
            l.MakeReadyForUse()
            l.SetScheme(scheme().LoadSchemeFromFile("resource/ClientScheme.res", "ClientScheme"))
            l.SetPaintBackgroundEnabled(False)
            l.SetPaintBorderEnabled(False)
            self.resources.append(l)
        
        AddTickSignal(self.GetVPanel(), 250)
            
    def ApplySchemeSettings(self, scheme_obj):
        super(HudResourceSection, self).ApplySchemeSettings(scheme_obj)

        for l in self.resources:
            l.SetBgColor(Color(0,0,0,0))
            l.SetFgColor(Color(225,225,225,255))
            l.SetContentAlignment(Label.a_west)
        
    def PerformLayout(self):
        super(HudResourceSection, self).PerformLayout()
        
        for i, l in enumerate(self.resources):
            margintop = scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
            marginleft = scheme().GetProportionalScaledValueEx(self.GetScheme(), 10)
            l.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 50), 
                scheme().GetProportionalScaledValueEx(self.GetScheme(), 20))
            l.SetPos(marginleft,
                margintop + scheme().GetProportionalScaledValueEx(self.GetScheme(), 20)*i)
        
    def OnTick(self):
        super(HudResourceSection, self).OnTick()
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return

        faction = player.GetFaction()
        info = GetFactionInfo(faction)
        if not info or not info.resources:
            return

        # update amount of resources
        for i, r in enumerate(info.resources):
            if i >= 3:
                break
            # TODO: ICONS
            amountresources = resources[player.GetOwnerNumber()][info.resources[i]]
            text = '%s %s' % (amountresources, r)
            if self.resources[i].GetText() != text:
                self.resources[i].SetText(text)
        
    backgroundtexture = 'hud_rebels_resource'
    
class HudAbilitiesSection(BackgroundPanel):
    def __init__(self, parent, infobox):
        super(HudAbilitiesSection, self).__init__(parent, 'HudAbilitiesSection')
        
        self.SetProportional(True)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)
        
        self.abilitypanel = BaseHudAbilities(self, infobox)
        self.abilitypanel.marginbottom = 2
        self.abilitypanel.margintop = 3
        
    def UpdateOnDelete(self):
        self.abilitypanel.DeletePanel()
        
    def PerformLayout(self):
        super(HudAbilitiesSection, self).PerformLayout()
        
        x, y = self.GetPos()
        margin = scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
        self.abilitypanel.SetPos(margin, margin)
        self.abilitypanel.SetSize(self.GetWide()-margin*2, self.GetTall()-margin*2)

    backgroundtexture = 'hud_rebels_abilities'
    
class HudUnits(BaseHudUnits):
    scale_values = {
        20 : (10, 2),
        60 : (15, 3),
        80 : (20, 4)
    }
    unitbuttonhpbounds = (0.043, 0.96, 0.87, 0.96) # xmin, xmax, ymin, ymax
    
class HudUnitsSection(BackgroundPanel):
    def __init__(self, parent, infopanel):
        super(HudUnitsSection, self).__init__(parent, 'HudUnitsSection')
        
        self.SetProportional(True)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)
        
        self.unitpanel = HudUnitsContainer(self, infopanel)
        self.unitpanel.defaultunitpanelclass = HudUnits
        
    def UpdateOnDelete(self):
        self.unitpanel.DeletePanel()
        
    def PerformLayout(self):
        super(HudUnitsSection, self).PerformLayout()
        
        x, y = self.GetPos()
        margin = scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
        self.unitpanel.SetPos(margin, margin)
        self.unitpanel.SetSize(self.GetWide()-margin*2, self.GetTall()-margin*2)

    backgroundtexture = 'hud_rebels_units'

class HudGroups(BaseHudGroups):
    def OnCursorEnteredButton(self, button):
        super(HudGroups, self).OnCursorEnteredButton(button)
        x, y = button.controlpanel.LocalToScreen(0, 0)
        GetAnimationController().RunAnimationCommand(button, "ypos", y+int(-1*button.GetTall()*0.3), 0.0, 0.25, AnimationController.INTERPOLATOR_LINEAR)
    def OnCursorExitedButton(self, button):
        super(HudGroups, self).OnCursorExitedButton(button)
        x, y = button.controlpanel.LocalToScreen(0, 0)
        GetAnimationController().RunAnimationCommand(button, "ypos", y, 0.0, 0.25, AnimationController.INTERPOLATOR_LINEAR)
    
class HudPortraitSection(BaseHudPortrait):
    def __init__(self, parent):
        super(HudPortraitSection, self).__init__(parent)
        self.topframe = TopPanel(self, 'TopFrame')
        self.topframe.backgroundtexture = 'hud_rebels_portrait'
        
    def PerformLayout(self):
        super(HudPortraitSection, self).PerformLayout()

        x, y = self.GetPos()
        self.topframe.SetPos(0, 0)
        self.topframe.SetSize(self.GetWide(), self.GetTall())
        
    backgroundtexture = 'hud_rebels_portrait_bg'
    
class HudRebels(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudRebels")
        Panel.__init__(self, None, "HudRebels")
        
        viewport = GetClientMode().GetViewport()
        
        self.SetParent(viewport)
        self.SetHiddenBits(HIDEHUD_STRATEGIC)

        # Create panels
        self.infobox = AbilityHudInfo()
        #self.infobox = Panel(viewport, 'minimap')
        self.minimapsection = HudMinimapSection(viewport)
        #self.minimapsection = Panel(viewport, 'minimapsection')
        self.population = HudPopulationSection(viewport)
        self.resource = HudResourceSection(viewport)
        #self.population = Panel(viewport, 'population')
        #self.resource = Panel(viewport, 'resource')
        self.abilities = HudAbilitiesSection(viewport, self.infobox)
        #self.abilities = Panel(viewport, 'abilities')
        self.units = HudUnitsSection(viewport, self.infobox)
        #self.units = Panel(viewport, 'units')
        self.portrait = HudPortraitSection(viewport)
        #self.portrait = Panel(viewport, 'portrait')
        self.groups = HudGroups(viewport)
        
        # Create a list for easy access
        # TODO: Consider removed attributes above?
        self.subpanels = {
            'infobox' : self.infobox, 
            'minimapsection' : self.minimapsection, 
            'population' : self.population, 
            'resource' : self.resource,
            'abilities' : self.abilities,
            'units' : self.units,
            'portrait' : self.portrait,
            'groups' : self.groups,
        }
        
    def UpdateOnDelete(self):
        # Delete panels that are not our children
        # otherwise they are still around when the new hud is created
        for name, panel in self.subpanels.iteritems():
            if panel:
                panel.DeletePanel()
        self.subpanels = {}
            
    def ApplySchemeSettings(self, scheme_obj):
        super(HudRebels, self).ApplySchemeSettings(scheme_obj)

        self.SetBgColor(Color(0,0,0,0))
        
    def PerformLayout(self):
        super(HudRebels, self).PerformLayout()
        
        self.SetSize(0,0)
        
        # save the screen size and get the aspect ratio
        self.screenwidth, self.screenheight = surface().GetScreenSize()
        self.aspect = self.screenwidth / float(self.screenheight)
        
        # Minimap + Population + resource panel
        # These panels are based on the left side of the screen.
        minimapwide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 158)
        self.minimapsection.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 0),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-144+1))
        self.minimapsection.SetSize( minimapwide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 144))
        
        self.population.SetPos( minimapwide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-41-1))
        self.population.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 133),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 41))
                     
        self.resource.SetPos( minimapwide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-41-73-2))
        self.resource.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 85),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 73))
                     
        # Abilities + units + portrait. 
        # These panels are based from the right side of the screen
        abilitieswide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 152)
        self.abilities.SetPos(self.screenwidth-abilitieswide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-135+1))
        self.abilities.SetSize(abilitieswide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 135))
                     
        if self.aspect > 1.7:
            # 16:9
            unitswide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 341)
            self.units.SetPos(self.screenwidth-unitswide-abilitieswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1))
            self.units.SetSize( unitswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 90))
        elif self.aspect >= 1.5:
            # 16:10
            unitswide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 255)
            self.units.SetPos(self.screenwidth-unitswide-abilitieswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1))
            self.units.SetSize( unitswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 90))
        else:
            # 4:3 suckers
            unitswide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 130)
            self.units.SetPos(self.screenwidth-unitswide-abilitieswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1))
            self.units.SetSize( unitswide,
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 90))
                     
        # Groups auto fixes the wide (to scale with the button ratio and number of buttons)
        groupsy = scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1)-int(self.groups.GetTall()*0.6)
        self.groups.SetTall(scheme().GetProportionalScaledValueEx(self.GetScheme(), 30))
        self.groups.SetPos(self.screenwidth-unitswide-abilitieswide, groupsy)
        self.groups.basey = groupsy
        self.groups.hovery = scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1)-int(self.groups.GetTall()*0.9)
                     
        portraitwide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 69)
        self.portrait.SetPos(self.screenwidth-portraitwide-unitswide-abilitieswide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 480-90+1))
        self.portrait.SetSize( portraitwide,
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 90))
                     
        # Info box
        self.infobox.mainhud_tall = scheme().GetProportionalScaledValueEx(self.GetScheme(), 135)
        self.infobox.iswidescreen = (self.aspect >= 1.45)
        self.infobox.PerformLayout()
        
    def SetVisible(self, visible):
        super(HudRebels, self).SetVisible(visible)
        for name, panel in self.subpanels.iteritems():
            if panel:
                panel.SetVisible(visible)
                
    subpanels = {}
                
class RebelsHudInfo(HudInfo):
    name = 'rebels_hud'
    cls = HudRebels
