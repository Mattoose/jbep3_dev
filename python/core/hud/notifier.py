""" The notifier hud element displays notifications to the player.

TODO:
- Colorize notifcations
- Add icons
"""
from srcbase import Color
from vgui import GetClientMode, CHudElement, CHudElementHelper, scheme, GetAnimationController, AddTickSignal, localize, images
from vgui.controls import Panel, RichText, AnimationController
from core.abilities import GetAbilityInfo

class NotifierLine(Panel):
    def __init__(self, parent, text, icon=images.GetImage('vgui/units/unit_unknown.vmt')):
        super(NotifierLine, self).__init__(parent, 'NotifierLine')
        
        self.text = RichText(self, 'NotifierText')
        
        self.text.SetVerticalScrollbar(False)
        self.text.SetKeyBoardInputEnabled(False)
        self.text.SetMouseInputEnabled(False)
        self.text.SetPaintBackgroundEnabled(False)
        
        self.icon = icon
        
        self.SetVisible(False)
        self.SetPaintBackgroundEnabled(False)
        
        self.text.InsertString(text)
        
        self.SetZPos(-50)
        
        self.expiretime = gpGlobals.curtime + 5.0
        self.fadingout = False
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
    def ApplySchemeSettings(self, schemeobj):
        super(NotifierLine, self).ApplySchemeSettings(schemeobj)
        hfontmedium = schemeobj.GetFont( "HeadlineLarge" )
        self.text.SetFont(hfontmedium)
        
    def PerformLayout(self):
        super(NotifierLine, self).PerformLayout()
        
        self.SetSize(self.GetParent().GetWide(),
                scheme().GetProportionalScaledValueEx(self.GetScheme(), 12))
        self.iconsize = scheme().GetProportionalScaledValueEx(self.GetScheme(), 12)
        self.text.SetPos(self.iconsize+2, 0)
        self.text.SetSize(self.GetWide()-self.iconsize, self.GetTall())
        
    def Paint(self):
        self.icon.DoPaint(0, 0, self.iconsize, self.iconsize, 0, self.GetAlpha()/255.0)
        
class HudNotifier(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudNotifier")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudNotifier")

        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(False)
        self.SetPaintEnabled(False)
        self.SetPaintBackgroundEnabled(False)
        
        self.messages = []
        self.queuedmessages = []
        self.movingmessagesup = False
        
        self.SetZPos(-50)
        
        AddTickSignal(self.GetVPanel(), 350)
        
    def LevelInit(self):
        # Reset
        self.messages = []
        self.queuedmessages = []
        self.movingmessagesup = False
        
    def InsertMessage(self, newmsg):
        self.queuedmessages.append(newmsg)
        self.UpdateMessages()
        
    def MoveMessagesUp(self):
        for msg in self.messages:
            msg.targety -= self.msgtall
            GetAnimationController().RunAnimationCommand(msg, "ypos", msg.targety, 0.0, self.msgmovetime, AnimationController.INTERPOLATOR_LINEAR)
            
    def CheckSpaceNewMessage(self):
        if not self.messages:
            return True
        x, y = self.messages[-1].GetPos()
        targety = self.GetTall()-self.msgtall*2+1
        if y <= targety:
            return True
        return False
        
    def UpdateMessages(self):
        # Check expire time and remove expired messages
        for i in reversed(range(0,len(self.messages))):
            msg = self.messages[i]
            if msg.fadingout:
                # Alpha hit zero -> remove
                if msg.GetAlpha() <= 0:
                    msg.DeletePanel()
                    del self.messages[i]
            else:
                # Fade out if expired or if out of the panel
                x, y = msg.GetPos()
                if msg.expiretime < gpGlobals.curtime or y < 0:
                    GetAnimationController().RunAnimationCommand(msg, "alpha", 0.0, 0.0, self.msgfadein, AnimationController.INTERPOLATOR_LINEAR)
                    msg.fadingout = True
                    
        # Check if we can insert the current top queued message
        if self.queuedmessages:
            if self.CheckSpaceNewMessage():
                msg = self.queuedmessages.pop(0)
                self.messages.append(msg)
                msg.SetVisible(True)
                msg.targety = self.GetTall()-self.msgtall
                msg.SetPos(0, msg.targety)
                msg.SetAlpha(0)
                GetAnimationController().RunAnimationCommand(msg, "alpha", 255.0, 0.0, self.msgfadeout, AnimationController.INTERPOLATOR_LINEAR)
                self.movingmessagesup = False
            elif not self.movingmessagesup:
                self.MoveMessagesUp()
                self.movingmessagesup = True
                    
    def OnTick(self):
        super(HudNotifier, self).OnTick()
        self.UpdateMessages()
        
    def PerformLayout(self):
        super(HudNotifier, self).PerformLayout()
        
        dy = scheme().GetProportionalScaledValueEx(self.GetScheme(), 12)
        tall = dy*self.msgmaxshow
        
        self.SetSize(scheme().GetProportionalScaledValueEx( self.GetScheme(), 350 ), tall)
        self.SetPos(scheme().GetProportionalScaledValueEx( self.GetScheme(), 25),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 100 ))    
                
        # Perform layout of the messages
        y = tall-dy
        for i in range(0, min(self.msgmaxshow, len(self.messages))):
            msg = self.messages[i]
            msg.SetPos(0, y)
            msg.targety = y
            y -= dy
            
        self.msgtall = dy
            
    msgmaxshow = 5
    msgfadein = 2.0
    msgfadeout = 1.0
    msgmovetime = 0.5
        
hudnotifier = CHudElementHelper(HudNotifier())

'''
from gameinterface import concommand
@concommand('notifier_insertmsg')
def cc_insertmsg(args):
    hudnotifier.Get().InsertMessage(NotifierLine(hudnotifier.Get(), 'TestMessage. TimeStamp: %f' % (gpGlobals.curtime)))
'''
