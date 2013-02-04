
if isserver:
    from entities import CBaseFilter, entity
    from fields import IntegerField, StringField
    
    @entity('filter_owner',
            iconsprite='editor/filter_name.vmt')
    class OwnerFilter(CBaseFilter):
        def PassesFilterImpl(self, caller, entity):
            if entity.GetOwnerNumber() != self.GetOwnerNumber():
                return False
            return True
            
    @entity('filter_unittype',
            iconsprite='editor/filter_name.vmt')
    class UnitTypeFilter(CBaseFilter):
        def PassesFilterImpl(self, caller, entity):
            if not entity.IsUnit():
                return False
            if entity.unitinfo.name != self.unittype:
                return False
            return True
            
        unittype = StringField(value='', keyname='unittype',
                               displayname='Unit Type', helpstring='Unit Type')