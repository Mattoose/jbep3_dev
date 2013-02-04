"""
Controls the music
"""
import os
import random

from srcbase import RelToAbs, RegisterTickMethod, UnregisterTickMethod
from vgui.controls import Frame
from sound import soundengine
from gameinterface import ConCommand
from core.signals import prelevelinit, postlevelshutdown

class MusicManager(object):
    def __init__(self):
        super(MusicManager, self).__init__()
        
        self.playlist = self.defaultplaylist
        
        prelevelinit.connect(self.LevelInitPreEntity)
        postlevelshutdown.connect(self.LevelShutdownPostEntity)
        
    def LoadPlayList(self, musicplaylist=None):
        if not musicplaylist:
            musicplaylist = self.defaultplaylist
            
        if musicplaylist != self.playlist:
            self.playlist = musicplaylist
            self.cursongidx = None
            self.NextSong()
    
    def LevelInitPreEntity(self, **kwargs):
        self.musicactive = True
        RegisterTickMethod(self.OnTick, 0.1)
        self.NextSong()

    def LevelShutdownPostEntity(self, **kwargs):
        self.musicactive = False
        UnregisterTickMethod(self.OnTick)
        
    def OnTick(self):
        self.UpdateMusic()
        
    __active = True
    @property
    def active(self):
        return self.__active
    @active.setter
    def active(self, active):
        if not active:
            self.StopMusic()
        self.__active = active
        
    def StopMusic(self):
        if self.guidcursong and soundengine.IsSoundStillPlaying(self.guidcursong):
            soundengine.StopSoundByGuid(self.guidcursong)
        
    def NextSong(self):
        self.StopMusic()
        if self.cursongidx == None:
            self.cursongidx = random.randint(0, len(self.playlist)-1)
        else:
            self.cursongidx = (self.cursongidx+1)%len(self.playlist)
        if not self.active:
            return
        soundengine.EmitAmbientSound(self.playlist[self.cursongidx], self.volume)
        self.guidcursong = soundengine.GetGuidForLastSoundEmitted()
        
    def UpdateMusic(self):
        if not self.active:
            return
        if not self.guidcursong:
            soundengine.EmitAmbientSound(self.playlist[self.cursongidx], self.volume)
            self.guidcursong = soundengine.GetGuidForLastSoundEmitted()
        elif not soundengine.IsSoundStillPlaying(self.guidcursong):
            self.NextSong() 
        
    # Default vars
    lastupdate = 0
    musicactive = False
    guidcursong = None
    volume = 0.16
    
    # Playlist
    cursongidx = None
    cursongname = None
    defaultplaylist = [
        'music/A New Revolution.mp3',
        'music/Glowstick.mp3',
        'music/Endangered Specimen.mp3',
        'music/Atmospheric Disturbances.mp3',
        'music/Now is the Hour.mp3',
        'music/Uprising.mp3',
    ]
    
musicmanager = MusicManager()

# Commands
def cc_music_toggle( args ):
    musicmanager.active = not musicmanager.active
music_toggle = ConCommand( "music_toggle", cc_music_toggle, "Toggle music.", 0 ) 

def cc_music_nextsong( args ):
    musicmanager.NextSong()
music_nextsong = ConCommand( "music_nextsong", cc_music_nextsong, "Next music song.", 0 )    

# GUI for controlling the music. Still empty
class MusicPlayer(Frame):
    def __init__(self):
        super(MusicPlayer, self).__init__(None, "MusicPlayer")
        
        self.SetTitle( 'Music player', True )
        
        self.SetMoveable( True )
        self.SetSizeable( True )
        self.SetMenuButtonVisible( False )
        self.SetMinimizeButtonVisible( False )
        self.SetMaximizeButtonVisible( False )
        self.SetCloseButtonVisible( True )
        
        self.SetSize( 400, 450 )  
        self.SetMinimumSize( 350, 400 )

    def ApplySchemeSettings(self, scheme_obj):
        super(MusicPlayer, self).ApplySchemeSettings(scheme_obj)
       
    def PerformLayout(self):
        super(MusicPlayer, self).PerformLayout()
       
    def OnTick(self):
        super(MusicPlayer, self).OnTick()

musicplayer = MusicPlayer()   
        
def show_musicplayer(args):
    if musicplayer.IsVisible():
        musicplayer.SetVisible(False)
        musicplayer.SetEnabled(False)  
    else:
        musicplayer.SetVisible(True)
        musicplayer.SetEnabled(True)  
        musicplayer.MoveToFront()
show_musicplayer_command = ConCommand("musicplayer", show_musicplayer, "Show up the ingame music player.", 0)
   