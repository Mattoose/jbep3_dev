from srcbase import Color
from vgui import scheme, GetClientMode, surface, scheme, AddTickSignal, RemoveTickSignal
from vgui.controls import Panel, Label, TextEntry
from entities import C_HL2WarsPlayer
from core.abilities import GetAbilityInfo
from core.factions import GetFactionInfo
import hotkeymgr
from gameinterface import engine

class Description(TextEntry):
    def ApplySchemeSettings(self, schemobj):
        super(Description, self).ApplySchemeSettings(schemobj)

        self.SetFgColor(Color(200,200,200,255))
        self.SetBgColor(Color(200,200,200,0))

        self.SetFont( schemobj.GetFont( "DebugFixedSmall" ) )

        self.SetBorder(None)
        
class InfoLabel(Label):
    def __init__(self, parent, panelname, text, fontcolor=None):
        super(InfoLabel, self).__init__(parent, panelname, text)
        
        self.SetScheme(scheme().LoadSchemeFromFile("resource/HL2Wars.res", "HL2Wars")) 
        self.SetPaintBackgroundEnabled(False)
        self.SetPaintBorderEnabled(False)
        self.SetContentAlignment(Label.a_west)
        self.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 50),
            scheme().GetProportionalScaledValueEx(self.GetScheme(), 15 ))
        self.fontcolor = fontcolor
        
    def ApplySchemeSettings(self, schemobj):
        super(InfoLabel, self).ApplySchemeSettings(schemobj)
        
        hfontsmall = schemobj.GetFont("DefaultVerySmall")
        
        self.SetFont(hfontsmall)
        self.SetBgColor(Color(0,0,0,0))
        if self.fontcolor:
            self.SetFgColor(self.fontcolor)
        else:
            self.SetFgColor(Color(200,200,200,255))
            
class InfoObject(object):
    def __init__(self, parent, name, headertext, fontcolor=None):
        self.header = InfoLabel(parent, "%sHeader" % (name), headertext, fontcolor=fontcolor)
        self.info = InfoLabel(parent, "InfoTime", "", fontcolor=fontcolor)
        
    def UpdateLayout(self, xindent, cury, xwidth, ysize):
        if self.header.IsVisible():
            self.header.SetPos(xindent, cury)
            wide = self.header.GetWide()
            self.info.SetPos(xindent + wide, cury)
            cury += ysize
        return cury
        
    def SetText(self, text):
        self.info.SetText(text)
        
    def SetVisible(self, vis):
        self.header.SetVisible(vis)
        self.info.SetVisible(vis)
        self.vis = vis
        
    def IsVisible(self):
        return self.vis
        
    def SetColor(self, color):
        self.header.SetFgColor(color)
        self.info.SetFgColor(color)
        self.header.fontcolor = color
        self.info.fontcolor = color

    vis = False
        
class InfoList(object):
    def __init__(self, parent, name, headertext):
        self.header = InfoList(parent, "%sHeader" % (name), headertext)
        self.items = []
        self.itemlabels = []
        
    def UpdateLayout(self, xindent, cury, xwidth, ysize):
        if self.header.IsVisible() and self.itemlabels:
            self.header.SetPos(xindent, cury)
            cury += ysize
            for il in self.itemlabels:
                il.SetPos(xindent+xindent, cury)
                il.SetWide(xwidth-xindent)
                cury += ysize
        return cury
        
    def UpdateItems(self, items):
        self.items = items
        for il in self.itemlabels:
            il.DeletePanel()
        self.itemlabels = []
        if not items:
            return
        for i in self.items:
            il = InfoLabel(self, 'Item', '%s' % (i)) 
            il.SetVisible(True)
            self.itemlabels.append(il)
                
class BaseHudInfo(Panel):
    def __init__(self, 
            showhotkey=True, 
            showrechargetime=True, 
            showcosts=True, 
            showenergy=True,
            showtechreq=True,
            showbuildtime=True,
            showpopulation=True):
        super(BaseHudInfo, self).__init__(None, "BaseHudInfo")
        self.SetParent( GetClientMode().GetViewport() )

        self.SetProportional(True)
        self.SetPaintBackgroundEnabled(True)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(False)     
        self.SetScheme(scheme().LoadSchemeFromFile("resource/HL2Wars.res", "HL2Wars"))  
        self.SetVisible(False)
        self.SetZPos(100)

        # Settings
        self.showhotkey = showhotkey
        self.showrechargetime = showrechargetime
        self.showcosts = showcosts
        self.showenergy = showenergy
        self.showtechreq = showtechreq
        self.showbuildtime = showbuildtime
        self.showpopulation = showpopulation
        
        # Create elements
        self.title = Label(self, "Title", "Put your title here!")
        self.title.SetPaintBackgroundEnabled(False)
        self.title.SetPaintBorderEnabled(False)
        self.title.SetContentAlignment(Label.a_west)
        self.title.SetVisible(True)
        
        self.hotkey = Label(self, "Hotkey", "")
        self.hotkey.SetPaintBackgroundEnabled(False)
        self.hotkey.SetPaintBorderEnabled(False )
        self.hotkey.SetContentAlignment(Label.a_west)
        self.hotkey.SetVisible(False)
            
        # load icons
        #self.costicon = surface().CreateNewTextureID() 
        #surface().DrawSetTextureFile( self.costicon, "vgui/icons/icon_cost" , True, False) 
        #self.timeicon = surface().CreateNewTextureID() 
        #surface().DrawSetTextureFile( self.timeicon, "vgui/icons/icon_reChargetime" , True, False) 
        
        self.description = Description(self, "Description")
        self.description.SetPaintBackgroundEnabled( True )
        self.description.SetPaintBorderEnabled( True )
        self.description.SetVisible( True )
        self.description.SetVerticalScrollbar( False )
        self.description.SetMultiline( True )
        self.description.SetEditable( False )
        self.description.SetEnabled( True )
        
        self.description.SetText("")
        
    def ApplySchemeSettings(self, schemobj):
        super(BaseHudInfo, self).ApplySchemeSettings(schemobj)
        
        self.SetBgColor(self.GetSchemeColor("ObjElement.BgColor", self.GetBgColor(), schemobj))
        self.SetBorder(schemobj.GetBorder("BaseBorder"))

        hfontnormal = schemobj.GetFont( "Default" )
        hfontsmall = schemobj.GetFont( "DefaultVerySmall" )
        hfontsmallest = schemobj.GetFont( "DebugFixedSmall" )
    
        self.title.SetFont(hfontnormal)
        self.title.SetBgColor(Color(0,0,0,0))	
        self.title.SetFgColor( Color(185,181,68,255) )
        
        self.hotkey.SetFont(hfontnormal)
        self.hotkey.SetBgColor(Color(0,0,0,0))	
        self.hotkey.SetFgColor( Color(220,220,0,255) )
        
        self.description.SetFont(hfontsmallest)  

    def PerformLayout(self):
        super(BaseHudInfo, self).PerformLayout()
        
        # To position ourself above the mainhud we need to know the height of the main hud.
        if not self.mainhud_tall:
            self.mainhud_tall = scheme().GetProportionalScaledValueEx(self.GetScheme(), 135)
         
        screenwidth, screenheight = surface().GetScreenSize()
        self.iswidescreen = engine.GetScreenAspectRatio(screenwidth, screenheight) > 1.5
        width = scheme().GetProportionalScaledValueEx( self.GetScheme(), 180 if self.iswidescreen else 150 )
        self.SetWide(width)
        tall = scheme().GetProportionalScaledValueEx( self.GetScheme(), 5 )
        xpos = screenwidth - width
        
        xindent = scheme().GetProportionalScaledValueEx( self.GetScheme(), 10 ) # Indent for headers/labels
        xwidth = width - xindent*2
        ysize = scheme().GetProportionalScaledValueEx( self.GetScheme(), 10 )

        # Position the remaining elements (only if they are visible)
        self.title.SetPos(xindent, tall)
        self.title.SizeToContents()
        self.title.SetTall(ysize)
        title_wide = self.title.GetWide()
        self.hotkey.SetPos(xindent + title_wide + scheme().GetProportionalScaledValueEx( self.GetScheme(), 3 ), tall)
        self.hotkey.SetSize(scheme().GetProportionalScaledValueEx( self.GetScheme(), 25 ), ysize)
        tall += ysize
        
        tall = self.PerformLayoutElements(xindent, tall, xwidth, ysize)

        if self.description.IsVisible():
            # Keep some space between description and other info labels
            tall += scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
        
            self.description.SetPos( xindent, tall)
            self.description.SetWide(xwidth)
            self.description.SetToFullHeight()
            tall += self.description.GetTall()
        
        # Keep some space between bottom and last element
        tall += scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
        
        # Finally set our size and position
        ypos = screenheight - self.mainhud_tall - tall
        self.defaultx = xpos
        self.defaulty = ypos
        if self.defaultpos:
            self.curx = xpos
            self.cury = ypos
        if self.posup:
            self.SetPos(self.curx, self.cury - tall)
        else:
            self.SetPos(self.curx, self.cury)
        self.SetTall(tall)
        
    def MoveTo(self, x, y, up=False):
        self.posup = up
        self.curx = x
        self.cury = y
        self.defaultpos = False
            
    def MoveToDefault(self):
        self.defaultpos = True
        self.posup = False
           
    '''
    def Paint(self):
        super(BaseHudInfo, self).Paint()
    
        # draw icons
        # surface().DrawSetColor( 255, 255, 255, 255 )
        # surface().DrawSetTexture( self.costicon )
        # surface().DrawTexturedRect( 
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 12 ),
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 15 ), 
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 21 ),
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 24 ) 
        # )	

        # surface().DrawSetColor( 255, 255, 255, 255 )
        # surface().DrawSetTexture( self.timeicon )
        # surface().DrawTexturedRect( 
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 12 ),
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 23 ), 
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ),
            # scheme().GetProportionalScaledValueEx( self.GetScheme(), 31 ) 
        # )
    '''

    def OnTick(self):
        if not self.IsVisible():
            return
            
        super(BaseHudInfo, self).OnTick()

        if self.showtimeout and self.showtimeout < gpGlobals.curtime:
            self.ShowAbility(None)
        elif self.showability:
            self.UpdateElements()
            self.Repaint()    
                
    # Changing the ability shown
    showability = None
    def ShowAbility(self, showability, slot=-1, unittype=None):
        if not showability:
            self.showability = None
            self.SetVisible(False)
            RemoveTickSignal(self.GetVPanel())
            return
            
        # Get Player
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            self.showability = None
            self.SetVisible(False)
            RemoveTickSignal(self.GetVPanel())
            return

        self.showtimeout = None
        if showability == self.showability:
            self.PerformLayout()
            return  
            
        self.showability = showability
        self.unittype = player.GetSelectedUnitType() if not unittype else unittype
        
        AddTickSignal(self.GetVPanel(), 100)

        # Now change the information of the shown ability
        info = showability
        
        self.title.SetText(info.displayname)
        self.description.SetText("")
        self.description.InsertString(info.description)
        
        if self.showhotkey and slot != -1:
            self.hotkeychar = hotkeymgr.hotkeysystem.GetHotkeyForAbility(info, slot)
            if self.hotkeychar:
                self.hotkey.SetText('[%s]' % (self.hotkeychar.upper()) )
                self.hotkey.SetVisible(True)
            else:
                self.hotkey.SetVisible(False)
        else:
            self.hotkey.SetVisible(False)
            
        self.OnShowElements()
            
        self.SetVisible(True)
        
        self.PerformLayout()
        
        # Do an extra tick to color them correctly
        self.OnTick()
        
    def GetColorBasedOnRequirements(self, requirements, name):
        return self.requiredcolor if name in requirements else self.normalcolor
        
    def PerformLayoutElements(self, xindent, cury, xwidth, ysize):
        return cury
        
    def UpdateElements(self):
        pass
            
    def OnShowElements(self):
        pass
        
    def HideAbility(self):
        self.showtimeout = gpGlobals.curtime + self.TIMEOUT

    # Default settings
    TIMEOUT = 0.05
    bgcolor = Color(255, 255, 255, 255)
    mainhud_tall = None
    iswidescreen = False
    
    normalcolor = Color(200,200,200,255)
    requiredcolor = Color(200,0,0,255)
    
    curx = 0
    cury = 0
    defaultpos = True
    posup = False
    showtimeout = -1
    hotkeychar = None
        
class AbilityHudInfo(BaseHudInfo):
    def __init__(self):
        super(AbilityHudInfo, self).__init__(showhotkey=True)
        
        # setting up headers for some Label's
        self.costheader = InfoLabel(self, "InfoCostHeader", "Cost")
        self.costs = []
        
        self.time = InfoObject(self, 'InfoTime', 'Recharge')
        self.buildtime = InfoObject(self, "InfoBuildTime", "Time")
        self.population = InfoObject(self, "InfoPopulation", "Population")
        self.energy = InfoObject(self, "InfoEnergy", "Energy")
        
        self.techheader = InfoLabel(self, "InfoTech", "Requirements: ")
        self.techrequirements = []
        
    def PerformLayoutElements(self, xindent, cury, xwidth, ysize):
        if self.costheader.IsVisible():
            self.costheader.SetPos(xindent, cury)
            costwide = self.costheader.GetWide()
            cury += ysize
            for tr in self.costs:
                tr.SetPos(xindent+xindent, cury)
                tr.SetWide(xwidth-xindent)
                cury += ysize
                
        if self.time.IsVisible(): cury = self.time.UpdateLayout(xindent, cury, xwidth, ysize)
        if self.buildtime.IsVisible(): cury = self.buildtime.UpdateLayout(xindent, cury, xwidth, ysize)
        if self.population.IsVisible(): cury = self.population.UpdateLayout(xindent, cury, xwidth, ysize)
        if self.energy.IsVisible(): cury = self.energy.UpdateLayout(xindent, cury, xwidth, ysize)

        if self.techheader.IsVisible():
            self.techheader.SetPos(xindent, cury)
            self.techheader.SetWide(xwidth)
            cury += ysize
            for tr in self.techrequirements:
                tr.SetPos(xindent+xindent, cury)
                tr.SetWide(xwidth-xindent)
                cury += ysize
                
        return cury
        
    def OnShowElements(self):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return
            
        factioninfo = GetFactionInfo(player.GetFaction())
            
        requirements = self.showability.GetRequirementsUnits(player)
        
        info = self.showability
        
        for c in self.costs:
            c.DeletePanel()
        self.costs = []
        if len(info.costs) != 0:
            costs = None
            
            # Prefer to show the costs that match the specified resources of the player faction
            if factioninfo:
                for clist in info.costs:
                    hassall = True
                    for c in clist:
                        if c[0] not in factioninfo.resources:
                            hassall = False
                            break
                        if hassall: costs = clist
                    if costs:
                        break
                            
            # Default to first cost set
            if not costs:
                costs = info.costs[0]

            self.costheader.SetVisible(True)
            for c in costs:
                l = InfoLabel(self, 'Cost', '%s %s' % (c[1], c[0][0]),
                              fontcolor=self.GetColorBasedOnRequirements(requirements, 'resources')) 
                l.SetVisible(True)
                self.costs.append(l)
        else:
            self.costheader.SetVisible(False)
       
        if info.rechargetime != 0:
            self.time.SetText(str(info.rechargetime))
            self.time.SetVisible(True)
        else:
            self.time.SetVisible(False)
            
        if hasattr(info, 'buildtime') and info.buildtime != 0:
            self.buildtime.SetText(str(info.buildtime))
            self.buildtime.SetVisible(True)
        else:
            self.buildtime.SetVisible(False)
            
        if hasattr(info, 'population') and info.population != 0:
            self.population.SetText(str(info.population))
            self.population.SetVisible(True)
        else:
            self.population.SetVisible(False)
            
        if info.energy != 0:
            self.energy.SetText(str(info.energy))
            self.energy.SetVisible(True)
        else:
            self.energy.SetVisible(False)
            
        for tr in self.techrequirements:
            tr.DeletePanel()
        self.techrequirements = []
        if len(info.techrequirements) != 0:
            self.techheader.SetVisible(True)
            for tr in info.techrequirements:
                techinfo = GetAbilityInfo(tr)
                if not techinfo:
                    continue
                l = InfoLabel(self, 'TechRequirement', '- %s' % (techinfo.displayname), 
                              fontcolor=self.GetColorBasedOnRequirements(requirements, 'available')) 
                l.SetVisible(True)
                self.techrequirements.append(l)
        else:
            self.techheader.SetVisible(False)
            
    def UpdateElements(self):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player:
            return

        if not self.unittype:
            return
            
        # Get requirements
        requirements = self.showability.GetRequirementsUnits(player)

        color = self.GetColorBasedOnRequirements(requirements, 'recharging')
        self.time.SetColor(color)
        
        color = self.GetColorBasedOnRequirements(requirements, 'resources')
        self.costheader.SetFgColor(color)
        for c in self.costs:
            c.SetFgColor(color)
            
        if hasattr(self.showability, 'population'):
            color = self.GetColorBasedOnRequirements(requirements, 'population')
            self.population.SetColor(color)
            
        color = self.GetColorBasedOnRequirements(requirements, 'energy')
        self.energy.SetColor(color)
            
        color = self.GetColorBasedOnRequirements(requirements, 'available')
        self.techheader.SetFgColor(color)
        for tr in self.techrequirements:
            tr.SetFgColor(color)
        
class UnitHudInfo(BaseHudInfo):
    def __init__(self):
        super(UnitHudInfo, self).__init__(showhotkey=False)
        
        self.health = InfoObject(self, "InfoHealth", "Health", fontcolor=self.healthcolor)
        self.energy = InfoObject(self, "InfoEnergy", "Energy", fontcolor=self.energycolor)
        
    def PerformLayoutElements(self, xindent, cury, xwidth, ysize):
        if self.health.IsVisible(): cury = self.health.UpdateLayout(xindent, cury, xwidth, ysize)
        if self.energy.IsVisible(): cury = self.energy.UpdateLayout(xindent, cury, xwidth, ysize)
        return cury
        
    def OnShowElements(self):
        self.health.SetVisible(self.unit.maxhealth > 0)
        self.energy.SetVisible(self.unit.maxenergy > 0)
        
    def UpdateElements(self):
        if not self.unit:
            return
            
        self.health.SetText('%d / %d' % (self.unit.health, self.unit.maxhealth))
        self.health.SetColor(self.healthcolor)
        self.energy.SetText('%d / %d' % (self.unit.energy, self.unit.maxenergy))
        self.energy.SetColor(self.energycolor)
        
    unit = None
    healthcolor = Color(0, 255, 0, 255)
    energycolor = Color(0, 200, 255, 255)
    
class QueueUnitHudInfo(BaseHudInfo):
    def __init__(self):
        super(QueueUnitHudInfo, self).__init__(showhotkey=False)
        
        self.buildtime = InfoObject(self, "InfoBuildTime", "BuildTime")
        
    def PerformLayoutElements(self, xindent, cury, xwidth, ysize):
        if self.buildtime.IsVisible(): cury = self.buildtime.UpdateLayout(xindent, cury, xwidth, ysize)
        return cury
        
    def OnShowElements(self):
        self.buildtime.SetVisible(self.unit != None)
        
    def UpdateElements(self):
        if not self.unit:
            return
            
        timepassed = self.unit.buildtime - max(0, self.unit.nextcompletiontime - gpGlobals.curtime)
        self.buildtime.SetText('%d / %d' % (timepassed, self.unit.buildtime))
        
class AttributeUnitHudInfo(BaseHudInfo):
    def __init__(self):
        super(AttributeUnitHudInfo, self).__init__(showhotkey=False)
        
    def OnShowElements(self):
        attributedesc = ''
        info = self.showability
        for attr in info.attributes:
            attributedesc += attr.description
    
        self.title.SetText('Attributes')
        self.description.SetText("")
        self.description.InsertString(attributedesc)
        