from srcbase import DMG_GENERIC
from vmath import vec3_origin, vec3_angle
from core.abilities import AbilityTargetGroup

if isserver:
    from core.units import BaseBehavior
    from entities import gEntList
    from unit_helper import GF_OWNERISTARGET
    
if isserver:
    class ActionSalvage(BaseBehavior.ActionAbility):
        def FindNearestBuilding(self, classname, checkownernumber=True):
            cur = gEntList.FindEntityByClassname(None, classname)
            if not cur:
                return None
            best = None
            while cur:
                try:
                    isvalid = cur.isconstructed
                except AttributeError:
                    isvalid = False
            
                if isvalid and (not checkownernumber or cur.GetOwnerNumber() == self.outer.GetOwnerNumber()):
                    dist = cur.GetAbsOrigin().DistTo(self.outer.GetAbsOrigin())
                    if not best:
                        best = cur
                        bestdist = dist
                    else:
                        if dist < bestdist:
                            best = cur
                            bestdist = dist
                cur = gEntList.FindEntityByClassname(cur, classname)
            return best
            
        def FindNearestHQ(self): return self.FindNearestBuilding("build_reb_hq")
        def FindNearestScrapMarker(self): return self.FindNearestBuilding("scrap_marker", checkownernumber=False)
            
        def Update(self):
            p = self.order.target
            if not p:
                return self.ChangeTo(self.behavior.ActionIdle, "No target")
                
            if p.GetClassname() != 'scrap_marker':
                p = self.FindNearestScrapMarker()
            
            if p:
                dist = (p.GetLocalOrigin() - self.outer.GetLocalOrigin()).Length2D()
                if not self.outer.carryingscrap and (dist > self.MINRANGE_MARKER+self.TOLERANCE+1.0):
                    return self.SuspendFor(self.behavior.ActionMoveTo, "Moving to scrap marker", p, tolerance=self.TOLERANCE, goalflags=GF_OWNERISTARGET)
                elif not self.outer.carryingscrap:
                    # Salvage time
                    scrap = p.GetScrap()
                    scrap.SetOwnerEntity(self.outer)
                    scrap.SetParent(self.outer, self.outer.LookupAttachment( "eyes" ) )
                    scrap.SetLocalOrigin(vec3_origin)
                    scrap.SetLocalAngles(vec3_angle)
                    self.outer.carryingscrap = scrap.GetHandle()
                    return self.Continue()
            
            if not self.outer.carryingscrap:
                return self.ChangeTo(self.behavior.ActionIdle, "Not carrying scrap and target is not scrap")
                
            nearestcolony = self.FindNearestHQ()
            if not nearestcolony:
                return self.ChangeTo(self.behavior.ActionIdle, "No hq to return to...")
            return self.SuspendFor(self.behavior.ActionMoveTo, "Moving to hq with a scrap on my back", nearestcolony, tolerance=self.TOLERANCE)
            
        def OnEnd(self):
            super(ActionSalvage, self).OnEnd()
            
        def OnResume(self):
            if self.outer.carryingscrap:
                nearestcolony = self.FindNearestHQ()
                if nearestcolony and self.outer.GetAbsOrigin().DistTo(nearestcolony.GetAbsOrigin()) < self.MINRANGE_HQ+self.TOLERANCE+1.0:
                    # Add resources and destroy scrap
                    self.outer.carryingscrap.SetParent(None)
                    self.outer.carryingscrap.AddResourcesAndRemove(self.outer.GetOwnerNumber())
                    #self.outer.carryingscrap.Remove()
                    self.outer.carryingscrap = None
                    
        MINRANGE_HQ = 196.0 # Minimum range required to deliver a grub to the colony
        MINRANGE_MARKER = 196.0 # Minimum range until we get a grub assigned. After that the worker moves to the exact spot.
        TOLERANCE = 32.0
        
class AbilitySalvage(AbilityTargetGroup):
    # Info
    name = "salvage"
    image_name = 'vgui/abilities/collectgrubs.vmt'
    rechargetime = 0
    displayname = "#RebSalvage_Name"
    description = "#RebSalvage_Description"
    image_name = 'vgui/rebels/abilities/salvage'
    hidden = True
    
    @classmethod
    def OverrideOrder(cls, unit, data, player):
        target = data.ent
        if isserver: # TODO: Also check on client to prevent normal order processing
            try: isconstructed = target.isconstructed
            except AttributeError: isconstructed = False
            
            if target and isconstructed and (target.ClassMatches('scrap_marker') or
               (target.ClassMatches('build_reb_hq') and unit.carryingscrap)):
                unit.DoAbility('salvage', [('leftpressed', data)])
                return True
        return False
        
    # Ability
    if isserver:
        def DoAbility(self):
            data = self.mousedata
            target = data.ent
            if not target or target.IsWorld():
                self.Cancel()
                return
            
            for unit in self.units:
                if (not target.ClassMatches('scrap_marker') and
                        not (target.ClassMatches('build_reb_hq') and unit.carryingscrap)):
                    continue
                unit.AbilityOrder(target=target, ability=self)
            self.Completed()
            
        behaviorgeneric_action = ActionSalvage
