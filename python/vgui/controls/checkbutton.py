from srcbase import KeyValues, Colorfrom vgui.controls import TextImage, Labelfrom togglebutton import ToggleButtonclass CheckImage(TextImage):    """ Check box image """    def __init__(self, checkbutton):        super(CheckImage, self).__init__( "g" )        self._CheckButton = checkbutton                self._borderColor1 = Color()        self._borderColor2 = Color()        self._checkColor = Color()        self._bgColor = Color()            self.SetSize(20, 13)    def Paint(self):        self.DrawSetTextFont(self.GetFont())        # draw background        if self._CheckButton.IsEnabled() and self._CheckButton.checkbuttoncheckable:            self.DrawSetTextColor(self._bgColor)        else:            self.DrawSetTextColor(self._CheckButton.GetDisabledBgColor())        self.DrawPrintChar(0, 1, 'g')            # draw border box        self.DrawSetTextColor(self._borderColor1)        self.DrawPrintChar(0, 1, 'e')        self.DrawSetTextColor(self._borderColor2)        self.DrawPrintChar(0, 1, 'f')        # draw selected check        if self._CheckButton.IsSelected():            if not self._CheckButton.IsEnabled():                self.DrawSetTextColor( self._CheckButton.GetDisabledFgColor() )            else:                self.DrawSetTextColor(self._checkColor)            self.DrawPrintChar(0, 2, 'b')class CheckButton(ToggleButton):    def __init__(self, parent, panelName, text):        super(CheckButton, self).__init__( parent, panelName, text )        self.SetContentAlignment(Label.a_west)        self.checkbuttoncheckable = True        # create the image        self._checkBoxImage = CheckImage(self)        self.SetTextImageIndex(1)        self.SetImageAtIndex(0, self._checkBoxImage, self.CHECK_INSET)        self._selectedFgColor = Color( 196, 181, 80, 255 )        self._disabledFgColor = Color(130, 130, 130, 255)        self._disabledBgColor = Color(62, 70, 55, 255)    def __del__(self):        self._checkBoxImage.DeletePanel()    def ApplySchemeSettings(self, schemeobj):        super(CheckButton, self).ApplySchemeSettings(schemeobj)        self.SetDefaultColor( self.GetSchemeColor("CheckButton.TextColor", schemeobj), self.GetBgColor() )        self._checkBoxImage._bgColor = self.GetSchemeColor("CheckButton.BgColor", Color(62, 70, 55, 255), schemeobj)        self._checkBoxImage._borderColor1 = self.GetSchemeColor("CheckButton.Border1", Color(20, 20, 20, 255), schemeobj)        self._checkBoxImage._borderColor2 = self.GetSchemeColor("CheckButton.Border2", Color(90, 90, 90, 255), schemeobj)        self._checkBoxImage._checkColor = self.GetSchemeColor("CheckButton.Check", Color(20, 20, 20, 255), schemeobj)        self._selectedFgColor = self.GetSchemeColor("CheckButton.SelectedTextColor", self.GetSchemeColor("ControlText", schemeobj), schemeobj)        self._disabledFgColor = self.GetSchemeColor("CheckButton.DisabledFgColor", Color(130, 130, 130, 255), schemeobj)        self._disabledBgColor = self.GetSchemeColor("CheckButton.DisabledBgColor", Color(62, 70, 55, 255), schemeobj)        self.SetContentAlignment(Label.a_west)        self._checkBoxImage.SetFont( schemeobj.GetFont("Marlett", self.IsProportional()) )        self._checkBoxImage.ResizeImageToContent()        self.SetImageAtIndex(0, self._checkBoxImage, self.CHECK_INSET)        # don't draw a background        self.SetPaintBackgroundEnabled(False)    def GetBorder(self, depressed, armed, selected, keyfocus):        return None            def SetSelected(self, state):        """ Check the button """        if self.checkbuttoncheckable:            # send a message saying we've been checked            msg = KeyValues("CheckButtonChecked", "state", int(state))            self.PostActionSignal(msg)                        super(CheckButton, self).SetSelected(state)    def SetCheckButtonCheckable(self, state):        """ sets whether or not the state of the check can be changed """        self.checkbuttoncheckable = state        self.Repaint()    def GetButtonFgColor(self):        """ Gets a different foreground text color if we are selected """        if self.IsSelected():            return self._selectedFgColor        return super(CheckButton, self).GetButtonFgColor()            def GetDisabledFgColor(self):        return self._disabledFgColor            def GetDisabledBgColor(self):        return self._disabledBgColor    def OnCheckButtonChecked(self, panel):        pass            CHECK_INSET = 6