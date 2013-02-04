""" Runover gamemode related entities """

if isserver:
    from entities import CPointEntity, entity
    from fields import input, OutputField, BooleanField, FloatField, IntegerField, StringField, FlagsField, fieldtypes, input
    from gamerules import gamerules
    
    @entity('overrun_wave_spawnpoint',
            base=['Targetname', 'Parentname', 'Angles', 'EnableDisable'],
            iconsprite='editor/info_target.vmt')
    class OverrunWaveSpawnPoint(CPointEntity):
        @input(inputname='Enable')
        def InputEnable(self, inputdata):
            self.disabled = False
            
        @input(inputname='Disable')
        def InputDisable(self, inputdata):
            self.disabled = True
            
        disabled = BooleanField(value=False, keyname='StartDisabled')
        priority = IntegerField(value=0, keyname='Priority')
    
    @entity('overrun_manager',
            base=['Targetname', 'Parentname', 'Angles', 'EnableDisable'],
            iconsprite='editor/logic_auto.vmt')
    class OverrunManager(CPointEntity):
        def Spawn(self):
            super(OverrunManager, self).Spawn()
            
            if self.GetSpawnFlags() & self.SF_CUSTOM_CONDITIONS:
                self.usecustomconditions = True
            
        def OnNewWave(self, wave):
            self.onnewwave.Set(wave, self, self)
            
        @input(inputname='Victory')
        def InputVictory():
            gamerules.EndOverrun()
            
        @input(inputname='Failed')
        def InputFailed():
            pass
            
        onnewwave = OutputField(keyname='OnNewWave', fieldtype=fieldtypes.FIELD_INTEGER)
        
        usecustomconditions = False
        wavetype = StringField(value='', keyname='wavetype')
        
        spawnflags = FlagsField(keyname='spawnflags', flags=
            [('SF_CUSTOM_CONDITIONS', ( 1 << 0 ), False)], 
            cppimplemented=True)
        
    @entity('overrun_distribution')
    class OverrunDistribution(CPointEntity):
        def __init__(self):
            super(OverrunDistribution, self).__init__()
            
            self.entries = []
            
        @input(inputname='AddEntry')
        def InputAddEntry():
            pass
        
    @entity('overrun_distribution_entry')
    class OverrunDistributionEntry(CPointEntity):
        unittype = StringField(value='', keyname='unittype')
        weight = FloatField(value=0.0, keyname='weight')
        