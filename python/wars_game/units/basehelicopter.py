from srcbase import *
from vmath import *
from core.units import UnitInfo, UnitBaseCombat as BaseClass
from sound import CSoundEnvelopeController

class BaseHelicopter(BaseClass):
    def __init__(self):
        super(BaseHelicopter, self).__init__()
    
        if isserver:
            self.SetShadowCastDistance(2048.0) # Use a much higher shadow cast distance

    def Event_Killed(self, info):
        super(BaseHelicopter, self).Event_Killed(info)
        
        self.StopLoopingSounds()
        
    def UnitThink(self):
        super(BaseHelicopter, self).UnitThink()
        
        iPitch = 50
        self.UpdateRotorSoundPitch(iPitch)

    def InitializeRotorSound(self):
        controller = CSoundEnvelopeController.GetController()

        if self.rotorsound:
            # Get the rotor sound started up.
            controller.Play( self.rotorsound, 0.0, 100 )
            self.UpdateRotorWashVolume()

        if self.rotorblast:
            # Start the blast sound and then immediately drop it to 0 (starting it at 0 wouldn't start it)
            controller.Play( self.rotorblast, 1.0, 100 )
            controller.SoundChangeVolume(self.rotorblast, 0, 0.0)

        #self.soundstate = SND_CHANGE_PITCH # hack for going through level transitions
 
    def UpdateRotorSoundPitch(self, iPitch):
        if self.rotorsound:
            controller = CSoundEnvelopeController.GetController()
            controller.SoundChangePitch( self.rotorsound, iPitch, 0.1 )
            self.UpdateRotorWashVolume()

    def UpdateRotorWashVolume(self):
        ''' Updates the rotor wash volume '''
        if not self.rotorsound:
            return

        controller = CSoundEnvelopeController.GetController()
        flVolDelta = self.GetRotorVolume() - controller.SoundGetVolume( self.rotorsound )
        if flVolDelta:
            # We can change from 0 to 1 in 3 seconds. 
            # Figure out how many seconds flVolDelta will take.
            flRampTime = abs( flVolDelta ) * 3.0
            controller.SoundChangeVolume( self.rotorsound, self.GetRotorVolume(), flRampTime )

    def GetRotorVolume(self):
        ''' For scripted times where it *has* to shoot '''
        return 0.0 if self.supresssound else 1.0

    def StopRotorWash(self):
        if self.rotorwash:
            UTIL_Remove( self.rotorwash )
            self.rotorwash = None

    def StopLoopingSounds(self):
        # Kill the rotor sounds
        controller = CSoundEnvelopeController.GetController()
        controller.SoundDestroy( self.rotorsound )
        controller.SoundDestroy( self.rotorblast )
        self.rotorsound = None
        self.rotorblast = None

        super(BaseHelicopter, self).StopLoopingSounds()
    
    rotorsound = None
    rotorblast = None
    rotorwash = None
    supresssound = False
    jumpheight = 0.0
    