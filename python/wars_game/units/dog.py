from srcbase import *
from entities import entity
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass
from unit_helper import UnitAnimConfig, LegAnimType_t

if isserver:
    from utils import UTIL_Remove
    from entities import CBeam, CSprite
    
@entity('unit_dog', networked=True)
class UnitDog(BaseClass):   
    def __init__(self):
        super(UnitDog, self).__init__()
        
        self.glowsprites = [None]*self.EFFECT_COUNT
        self.beams = [None]*self.EFFECT_COUNT

    if isserver:
        def Precache(self):
            super(UnitDog, self).Precache()
        
            self.PrecacheScriptSound( "Weapon_PhysCannon.Launch" )

            self.PrecacheModel( "sprites/orangelight1.vmt" )
            self.PrecacheModel( "sprites/physcannon_bluelight2.vmt" )
            self.PrecacheModel( "sprites/glow04_noz.vmt" )

        def Spawn(self):
            super(UnitDog, self).Spawn()
            
            self.SetBloodColor(BLOOD_COLOR_MECH)
        
    def ClearBeams(self):
        self.ClearSprites()
        
        # Turn off sprites
        for i in range(0, self.EFFECT_COUNT):
            if self.beams[i] != None:
                UTIL_Remove( self.beams[i] )
                self.beams[i] = None

    def ClearSprites(self):
        # Turn off sprites
        for i in range(0, self.EFFECT_COUNT):
            if self.glowsprites[i] != None:
                UTIL_Remove( self.glowsprites[i] )
                self.glowsprites[i] = None

    def CreateSprites(self):
        #Create the glow sprites
        for i in range(0, self.EFFECT_COUNT):
            if self.glowsprites[i]:
                continue

            attachNames = [
                "physgun",
                "thumb",
                "pinky",
                "index",
            ]

            self.glowsprites[i] = CSprite.SpriteCreate( "sprites/glow04_noz.vmt", self.GetAbsOrigin(), False )

            self.glowsprites[i].SetAttachment( self, self.LookupAttachment( attachNames[i] ) )
            self.glowsprites[i].SetTransparency( kRenderGlow, 255, 128, 0, 64, kRenderFxNoDissipation )
            self.glowsprites[i].SetBrightness( 255, 0.2 )
            self.glowsprites[i].SetScale( 0.55, 0.2 )

    def CreateBeams(self):
        if self.usebeameffects == False:
            self.ClearBeams()
            return

        self.CreateSprites()

        for i in range(0, self.EFFECT_COUNT):
            if self.beams[i]:
                continue

            attachNames = [
                "physgun",
                "thumb",
                "pinky",
                "index",
            ]

            self.beams[i] = CBeam.BeamCreate( "sprites/physcannon_bluelight2.vmt", 5.0 )

            self.beams[i].EntsInit( self.physicsent, self )
            self.beams[i].SetEndAttachment( self.LookupAttachment( attachNames[i] ) )
            self.beams[i].SetBrightness( 255 )
            self.beams[i].SetColor( 255, 255, 255 )
            self.beams[i].SetNoise( 5.5 )
            self.beams[i].SetRenderMode( kRenderTransAdd )
            
    # Animation state
    animconfig = UnitAnimConfig(
        maxbodyyawdegrees=90.0,
        leganimtype=LegAnimType_t.LEGANIM_8WAY,
        useaimsequences=False,
    )
    class AnimStateClass(BaseClass.AnimStateClass):
        def OnNewModel(self):
            super(UnitDog.AnimStateClass, self).OnNewModel()
            
            studiohdr = self.outer.GetModelPtr()
            
            self.bodyyaw = self.outer.LookupPoseParameter("body_yaw")
            self.bodypitch = self.outer.LookupPoseParameter("aim_pitch")
            
            aimyaw = self.outer.LookupPoseParameter(studiohdr, "aim_yaw")
            if aimyaw < 0:
                return
            self.outer.SetPoseParameter(studiohdr, aimyaw, 0.0)
            
            headpitch = self.outer.LookupPoseParameter(studiohdr, "head_pitch")
            if headpitch < 0:
                return
            headyaw = self.outer.LookupPoseParameter(studiohdr, "head_yaw")
            if headyaw < 0:
                return
            headroll = self.outer.LookupPoseParameter(studiohdr, "head_roll")
            if headroll < 0:
                return
                
            self.outer.SetPoseParameter(studiohdr, headpitch, 0.0)
            self.outer.SetPoseParameter(studiohdr, headyaw, 0.0)
            self.outer.SetPoseParameter(studiohdr, headroll, 0.0)
            
            spineyaw = self.outer.LookupPoseParameter(studiohdr, "spine_yaw")
            if spineyaw < 0:
                return
                
            self.outer.SetPoseParameter(studiohdr, spineyaw, 0.0)
            
            necktrans = self.outer.LookupPoseParameter(studiohdr, "neck_trans")
            if necktrans < 0:
                return
                
            self.outer.SetPoseParameter(studiohdr, necktrans, 0.0)

    maxspeed = 350
    yawspeed = 15.0
    jumpheight = 150.0
    
    usebeameffects = False
    physicsent = None
    
    EFFECT_COUNT = 4
    
class DogInfo(UnitInfo):
    name        = 'unit_dog'
    cls_name    = 'unit_dog'
    displayname = '#Dog_Name'
    description = '#Dog_Description'
    image_name = 'vgui/units/unit_shotgun.vmt'
    health = 1000
    attributes = ['heavy']
    modelname = 'models/dog.mdl'
    hulltype = 'HULL_WIDE_HUMAN'
    abilities = {
        8 : 'attackmove',
        9 : 'holdposition',
    }