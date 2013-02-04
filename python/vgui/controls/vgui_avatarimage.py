from isteam import CSteamID, steamapicontext, EUniverse, EAccountType, EAvatarSize
from gameinterface import engine, PlayerInfo
from utils import ScreenWidth, ScreenHeight
from vgui.controls import AvatarImage
from imagepanel import ImagePanel
    
class AvatarImagePanel(ImagePanel):
    def SetPlayer(self, player):
        """ Set the player that this Avatar should display for """
        if self.player:
            self.SetPlayerIndex(player.entindex())
                    
    def SetPlayerIndex(self, index):
        """ Set the player (by index) that this Avatar should display for """
        if self.image:
            self.image.ClearAvatarSteamID()

        if index and steamapicontext.SteamUtils():
            pi = PlayerInfo()
            if engine.GetPlayerInfo(index, pi):
                if pi.friendsID:
                    steamIDForPlayer = CSteamID(pi.friendsID, 1, steamapicontext.SteamUtils().GetConnectedUniverse(), EAccountType.k_EAccountTypeIndividual)
                    self.SetAvatarBySteamID(steamIDForPlayer)
                    
    def PaintBackground(self):
        if self.image:
            self.image.SetColor(self.drawcolor)
            self.image.Paint()

    def SetAvatarBySteamID(self, friendsID):
        if not self.image:
            image = AvatarImage()
            self.SetImage(image)

        # Indent the image. These are deliberately non-resolution-scaling.
        indent = 2
        self.image.SetPos(indent, indent)
        wide = self.GetWide() - (indent*2)

        self.image.SetAvatarSize(EAvatarSize.k_EAvatarSize64x64 if wide > 32 else EAvatarSize.k_EAvatarSize32x32)
        self.image.SetAvatarSteamID(friendsID)

        self.image.SetSize(wide, self.GetTall()-(indent*2))
        