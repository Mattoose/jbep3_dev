from srcbase import COLLISION_GROUP_NPC, MASK_NPCSOLID, MAX_TRACE_LENGTH
from vmath import QAngle, anglemod, AngleVectors, Vector, vec3_angle, vec3_origin
from math import atan, pi, sqrt, pow

if isserver:
    from gameinterface import concommand, FCVAR_CHEAT, CSingleUserRecipientFilter
    
from _utils import *

# Tracer Flags
TRACER_FLAG_WHIZ = 0x0001
TRACER_FLAG_USEATTACHMENT = 0x0002

TRACER_DONT_USE_ATTACHMENT = -1

# To be used with UTIL_ClientPrintAll
HUD_PRINTNOTIFY = 1
HUD_PRINTCONSOLE = 2
HUD_PRINTTALK = 3
HUD_PRINTCENTER = 4

# UTIL_BloodSpray flags
FX_BLOODSPRAY_DROPS = 0x01
FX_BLOODSPRAY_GORE = 0x02
FX_BLOODSPRAY_CLOUD = 0x04
FX_BLOODSPRAY_ALL = 0xFF

if isserver:
    def ClientPrint(player, msg_dest, msg_name, param1, param2, param3, param4):
        if not player:
            return

        user = CSingleUserRecipientFilter(player)
        user.MakeReliable()

        UTIL_ClientPrintFilter(user, msg_dest, msg_name, param1, param2, param3, param4)
else:
    def ClientPrint(player, msg_dest, msg_name, param1, param2, param3, param4): pass
    
def UTIL_GetPlayers():
    players = []
    for i in range(1, gpGlobals.maxClients+1):
        player = UTIL_PlayerByIndex(i)
        if player is None or not player.IsConnected():
            continue   
        players.append(player)
    return players

def UTIL_CalculateDirection(point1, point2):
    diff_x = point1.x - point2.x
    diff_y = point1.y - point2.y
    if diff_x == 0:
        return vec3_angle
    yaw = atan( diff_y / diff_x ) * ( 180 / pi )

    # fix up yaw if needed
    if diff_x > 0 and diff_y > 0:
        yaw += 180.0
    elif diff_x > 0:
        yaw += 180.0
    
    return QAngle(0.0, yaw, 0.0)
    
# Clamp Yaw
def ClampYaw( yawSpeedPerSec, current, target, time ):
    if current != target:
        speed = yawSpeedPerSec * time
        move = target - current

        if target > current:
            if move >= 180:
                move = move - 360
        else:
            if move <= -180:
                move = move + 360

        if move > 0: # turning to the npc's left
            if move > speed:
                move = speed
        else: # turning to the npc's right
            if move < -speed:
                move = -speed
        
        return anglemod(current + move)

    return target
    
class PositionInRadiusInfo(object):
    """ Stores info when scanning for positions in a radius. """
    def __init__(self, startposition, mins, maxs, radius, fan=None, stepsize=None, ignore=None, 
                 zoffset=0.0, beneathlimit = 256.0, mask=MASK_NPCSOLID):
        super(PositionInRadiusInfo, self).__init__()

        self.startposition = Vector(startposition)
        self.position = Vector(startposition)
        self.mins = mins
        self.maxs = maxs
        self._radius = radius
        if fan is None:
            self.fan = QAngle(0, 0, 0)
        else:
            self.fan = fan
        self.ignore = ignore
        self.zoffset = zoffset
        self.beneathlimit = beneathlimit
        self.success = False
        self.mask = mask

        if not stepsize:
            self.ComputeRadiusStepSize() 
        else:
            self.stepsize = int(stepsize)
            self.usecustomstepsize = True
            
    def ComputeRadiusStepSize(self):
        if not self.radius:
            self.stepsize = 0
            return
        perimeter = 2 * pi * self.radius
        sizeunit = int(sqrt(pow(self.maxs.x - self.mins.x, 2)+ pow(self.maxs.y - self.mins.y, 2))*1.25)
        self.stepsize = max(8, int(360 / (perimeter / sizeunit)))    
        
    def getradius(self):
        return self._radius
    def setradius(self, radius):
        self._radius = radius
        if not self.usecustomstepsize:
            self.ComputeRadiusStepSize()
    radius = property(getradius, setradius, "Radius")
    
    usecustomstepsize = False
    
def UTIL_FindPositionInRadius(info):
    """ Scans all positions on the perimeter of the circle 
        The field success is put to True if a position is found. 
        The field position contains the result. 
        Pass in the info object again to find the next position (for optimization) """
    info.success = False
    starty = int(info.fan.y)
    vecDir = Vector()
    tr = trace_t()
    for info.fan.y in range(starty, 360, info.stepsize):
        AngleVectors(info.fan, vecDir)

        vecTest = info.startposition + vecDir * info.radius

        # Maybe no nav mesh? Fallback to trace line
        UTIL_TraceLine(vecTest, vecTest - Vector(0, 0, MAX_TRACE_LENGTH), info.mask, info.ignore, COLLISION_GROUP_NPC, tr)
        if tr.fraction == 1.0:
            continue
        endpos = tr.endpos
        
        endpos.z += -info.mins.z + info.zoffset
        UTIL_TraceHull( endpos,
                        endpos + Vector(0, 0, 10),
                        info.mins,
                        info.maxs,
                        info.mask,
                        info.ignore,
                        COLLISION_GROUP_NPC,
                        tr )

        if tr.fraction == 1.0:
            info.position = Vector(tr.endpos)
            info.success = True
            info.fan.y += info.stepsize
            return info     
    return info

class FindPositionInfo(object):
    def __init__(self, startposition, mins, maxs, startradius=0, maxradius=None, radiusgrow=None, radiusstep=None, ignore=None, 
                 zoffset=0.0, beneathlimit=256.0, mask=MASK_NPCSOLID):
        super(FindPositionInfo, self).__init__()
        
        self.position = Vector(startposition)
        self._mins = mins
        self._maxs = maxs
        self.radius = startradius
        self._ignore = ignore
        self.zoffset = zoffset
        self.beneathlimit = beneathlimit
        self.success = False
        self.mask = mask
        self.radiusstep = radiusstep
        
        if not radiusgrow:
            self.radiusgrow = (maxs - mins).Length2D() #int(abs(maxs.x - mins.x))
        else:
            self.radiusgrow = radiusgrow
            
        if not maxradius:
            self.maxradius = self.radiusgrow*100.0
        else:
            self.maxradius = maxradius
            
        self.inradiusinfo = PositionInRadiusInfo(self.position, mins, maxs, 0, stepsize=radiusstep,
                ignore=ignore, zoffset=zoffset, beneathlimit=beneathlimit, mask=mask)

    def getmins(self):
        return self._mins
    def setmins(self, mins):
        self._mins = mins
        if self.inradiusinfo: self.inradiusinfo.mins = mins
    mins = property(getmins, setmins, "Mins")
    
    def getmaxs(self):
        return self._maxs
    def setmaxs(self, maxs):
        self._maxs = maxs
        if self.inradiusinfo: self.inradiusinfo.maxs = maxs
    maxs = property(getmaxs, setmaxs, "Maxs")
    
    def getignore(self):
        return self._ignore
    def setignore(self, ignore):
        self._ignore = ignore
        if self.inradiusinfo: self.inradiusinfo.ignore = ignore
    ignore = property(getignore, setignore, "Ignore entity")
    
def UTIL_FindPosition(info):
    info.success = False
    tr = trace_t()
    if info.radius == 0:
      
        # Maybe no nav mesh? Fallback to trace line
        UTIL_TraceLine(info.position, info.position - Vector(0, 0, MAX_TRACE_LENGTH), info.mask, info.ignore, COLLISION_GROUP_NPC, tr)
        endpos = tr.endpos if tr.fraction == 1.0 else vec3_origin
        
        info.radius += info.radiusgrow

        if endpos != vec3_origin:
            endpos.z += -info.mins.z + info.zoffset
            UTIL_TraceHull( endpos,
                            endpos + Vector(0, 0, 10),
                            info.mins,
                            info.maxs,
                            info.mask,
                            info.ignore,
                            COLLISION_GROUP_NPC,
                            tr )

            if tr.fraction == 1.0:
                info.position = Vector(tr.endpos)
                info.success = True
                return info

    while info.radius <= info.maxradius:
        info.inradiusinfo.radius = info.radius
        UTIL_FindPositionInRadius(info.inradiusinfo)
        if info.inradiusinfo.success:
            info.position = Vector(info.inradiusinfo.position)
            info.success = True        
            return info
        info.inradiusinfo.fan.Init(0,0,0)
        info.radius += info.radiusgrow
    return info
    
if isserver:
    @concommand('test_findposition', '', FCVAR_CHEAT)
    def TestFindPosition(args):
        import ndebugoverlay
        player = UTIL_GetCommandClient()
        data = player.GetMouseData()
        
        radius = float(args[1])
        info = FindPositionInfo(data.groundendpos, -Vector(16, 16, 16), Vector(16, 16, 16), maxradius=radius)
        for i in range(0, 10000):
            UTIL_FindPosition(info)
            if not info.success:
                break
            ndebugoverlay.Cross3D(info.position, 32.0, 255, 0, 0, False, 10.0)

#def UTIL_ListPlayersForOwnerNumber(ownernumber):
#    """ Helper method. List players for an owner number """
#    players = []
#    for i in range(1, gpGlobals.maxClients+1):
#        player = UTIL_PlayerByIndex(i)
#        if player == None:
#            continue
#        if player.GetOwnerNumber() == ownernumber:
#            players.append(player)
#    return players
#    
#def UTIL_ListForOwnerNumberWithDisp(ownernumber, d=Disposition_t.D_LI):
#    import playermgr 
#    players = []
#    for i in range(1, gpGlobals.maxClients+1):
#        player = UTIL_PlayerByIndex(i)
#        if player == None:
#            continue
#        if playermgr.relationships[(ownernumber, player.GetOwnerNumber())] == d:
#            players.append(player)
#    return players
#    
#def UTIL_ListForOwnerNumberExclDisp(ownernumber, d=Disposition_t.D_LI):
#    import playermgr 
#    players = []
#    for i in range(1, gpGlobals.maxClients+1):
#        player = UTIL_PlayerByIndex(i)
#        if player == None:
#            continue
#        if playermgr.relationships[(ownernumber, player.GetOwnerNumber())] != d:
#            players.append(player)
#    return players