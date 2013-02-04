if isserver:
    from entities import CPointEntity, entity
    from fields import input, OutputField, BooleanField, FloatField, IntegerField, StringField, FlagsField, fieldtypes, input
    from core.signals import buildingstarted, buildingfinished
    
    @entity('event_building_listener',
            base=['Targetname', 'Parentname', 'Angles', 'EnableDisable'],
            iconsprite='editor/logic_script.vmt')
    class EventBuildingListener(CPointEntity):
        def Spawn(self):
            super(EventBuildingListener, self).Spawn()
            
            buildingstarted.connect(self.OnBuildingStarted)
            buildingfinished.connect(self.OnBuildingFinished)
            
        def UpdateOnRemove(self):
            super(EventBuildingListener, self).UpdateOnRemove()
            
            buildingstarted.disconnect(self.OnBuildingStarted)
            buildingfinished.disconnect(self.OnBuildingFinished)
            
        def OnBuildingStarted(self, building, *args, **kwargs):
            self.onbuildingstarted.Set('', building, self)
            
        def OnBuildingFinished(self, building, *args, **kwargs):
            self.onbuildingfinished.Set('', building, self)
            
        onbuildingstarted = OutputField(keyname='OnBuildingStarted', fieldtype=fieldtypes.FIELD_STRING)
        onbuildingfinished = OutputField(keyname='OnBuildingFinished', fieldtype=fieldtypes.FIELD_STRING)