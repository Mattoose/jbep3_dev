from srcbase import MASK_NPCSOLID
from vmath import Vector, QAngle
from core.gamerules import GamerulesInfo, WarsBaseGameRules
from playermgr import dbplayers, OWNER_LAST, OWNER_ENEMY, relationships
from gamemgr import dblist, BaseInfo, BaseInfoMetaclass
from gamemgr import dbgamepackages
import random
import bisect
import traceback
from collections import defaultdict
from math import floor, ceil
from glpkg.gamelobby_shared import INVALID_POSITION
from gamerules import GameRules, gamerules
from core.buildings.base import constructedlistpertype, buildinglist
from core.resources import SetResource, GiveResources, RESOURCE_KILLS
from fow import FogOfWarMgr
from navmesh import RandomNavAreaPosition, RandomNavAreaPositionWithin
import ndebugoverlay

from profiler import StartProfiler, EndProfiler
from vprof import vprofcurrentprofilee

if isserver:
    from entities import gEntList, MouseTraceData, CreateEntityByName, DispatchSpawn, D_LI, variant_t, g_EventQueue
    from core.units import unitlist, PrecacheUnit, CreateUnit, CreateUnitNoSpawn
    from utils import UTIL_HudMessageAll, hudtextparms, UTIL_FindPosition, FindPositionInfo, UTIL_DropToFloor
    from gameinterface import concommand, FCVAR_CHEAT, ConVar, AutoCompletion
    from core.usermessages import SendUserMessage, CReliableBroadcastRecipientFilter, CSingleUserRecipientFilter
    
if isserver:
    overrun_max_active_enemies = ConVar('overrun_max_active_enemies', '120')
    
# Wave type dictionary
dbwavetypeid = 'overrun_wavetype'
dbwavetypes = dblist[dbwavetypeid]

# Helpers for health mods
def HMod(unit): return 'healthmod_%s' % (unit)
def HModEasy(unit): return 'easy_healthmod_%s' % (unit)
def HModNormal(unit): return 'normal_healthmod_%s' % (unit)
def HModHard(unit): return 'hard_healthmod_%s' % (unit)

def HModGrow(unit): return 'healthgrowmod_%s' % (unit)
def HModGrowEasy(unit): return 'easy_healthgrowmod_%s' % (unit)
def HModGrowNormal(unit): return 'normal_healthgrowmod_%s' % (unit)
def HModGrowHard(unit): return 'hard_healthgrowmod_%s' % (unit)


# Small helper function for selecting units to some probability distribution
# http://rosettacode.org/wiki/Probabilistic_choice#Python
def probchoice(items, probs):
    '''\
    Splits the interval 0.0-1.0 in proportion to probs
    then finds where each random.random() choice lies
    '''

    prob_accumulator = 0
    accumulator = []
    for p in probs:
        prob_accumulator += p
        accumulator.append(prob_accumulator)
 
    while True:
        r = random.random()
        yield items[bisect.bisect(accumulator, r)]

class Overrun(WarsBaseGameRules):
    if isserver:
        def InitGamerules(self):
            super(Overrun, self).InitGamerules()
            
            random.seed()

            self.enemiesalive = []
            self.healthmodifiers = defaultdict( lambda : 1.0 )
            self.healthgrowmodifiers = defaultdict( lambda : 1.0 ) # Modifies the above health modifiers each wave
            self.nextwave = gpGlobals.curtime + self.waveinterval

            self.manager = gEntList.FindEntityByClassname(None, 'overrun_manager')

            # Setup default info, possible overridden by gamelobby
            if self.manager:
                if self.manager.wavetype:
                    self.wavetype = self.manager.wavetype
            
            self.RebuildSpawnPointsList()
            
        def Precache(self):
            super(Overrun, self).Precache()
            
            unittypes = set()
            for wave in dbwavetypes[self.wavetype].distribution.itervalues():
                if 'distribution' not in wave:
                    continue
                unittypes |= set(wave['distribution'][0])
            for unittype in unittypes:
                PrecacheUnit(unittype)
            
        def ClientActive(self, client):
            super(Overrun, self).ClientActive(client)
            
            filter = CSingleUserRecipientFilter(client)
            filter.MakeReliable()
            SendUserMessage( filter, 'overrun.waveupdate', [self.wave, self.__nextwave] )
            
        def EndOverrun(self):
            self.EndGame([], self.gamelobby_players)
                
        def Think(self):
            super(Overrun, self).Think()
            if self.gameover:
                return
            
            if self.CheckDefeat():
                self.EndOverrun()
                return
                
            # Don't run until a valid wave type is set
            if not self.waveinfo:
                return

            vprofcurrentprofilee.EnterScope("Overrun", 0, "Overrun", False)
            StartProfiler('Overrun')
            
            if self.waveinprogress:
                self.enemiesalive = filter(None, self.enemiesalive)
                unitsleft = ((self.spawnsleft+len(self.enemiesalive))/float(self.spawnsize))
                if unitsleft < 0.2:
                    self.nextwave = gpGlobals.curtime + max(0,self.waveinterval + random.uniform(-self.waveintervalnoise, self.waveintervalnoise))
                    self.waveinprogress = False

                    # Give income
                    players = self.GetRealPlayers()
                    owners = set(map(lambda p: p.GetOwnerNumber(), players))
                    DevMsg(1, "Wave %d ended. Active owners: %s\n" % (self.wave, str(owners)))
                    for ownernumber in owners:
                        DevMsg(1, "Giving player %d resources (%d)\n" % (ownernumber, self.waveincome))
                        GiveResources(ownernumber, [(RESOURCE_KILLS, self.waveincome)], firecollected=True)
            elif self.nextwave < gpGlobals.curtime:
                self.SpawnWave()

            # Update spawner
            if self.nextspawninterval < gpGlobals.curtime:
                self.UpdateSpawner()
                
                self.nextspawninterval = gpGlobals.curtime + self.spawninterval
                
            # Let wave info do it's thing
            self.waveinfo.Update(self)
                
            EndProfiler('Overrun')
            vprofcurrentprofilee.ExitScope()
                
        def CheckGameOver(self):
            if self.gameover:   # someone else quit the game already
                # check to see if we should change levels now
                if self.intermissionendtime < gpGlobals.curtime:
                    self.ChangeToGamelobby()  # intermission is over
                return True
            return False
        
        def CheckDefeat(self):
            if self.manager and self.manager.usecustomconditions:
                return False
                    
            count = 0
            for i in constructedlistpertype.itervalues():
                count += len(i['build_comb_hq']) + len(i['build_comb_hq_overrun']) + len(i['build_reb_hq']) + len(i['build_reb_hq_overrun'])
            return count == 0

        __nextwave = 0
        def __GetNextWave(self):
            return self.__nextwave
        def __SetNextWave(self, cap):
            self.__nextwave = cap
            filter = CReliableBroadcastRecipientFilter()
            SendUserMessage( filter, 'overrun.waveupdate', 
                [self.wave, self.__nextwave] ) 
        nextwave = property(__GetNextWave, __SetNextWave, None, "Level time at which the next wave is spawned")
        
        __wavetype = ''
        def __GetWaveType(self):
            return self.__wavetype
        def __SetWaveType(self, wavetype):
            try:
                self.waveinfo = dbwavetypes[wavetype]()
            except KeyError:
                PrintWarning('Failed  to set wavetype to %s\n' % (wavetype))
                return
            self.__wavetype = wavetype
        wavetype = property(__GetWaveType, __SetWaveType, None, "Wave type")

        def GetFromWaveInfo(self, waveinfo, name, default):
            diffkey = '%s_%s' % (self.difficulty, name)
            try: return waveinfo[diffkey]
            except KeyError: pass
                
            try: return waveinfo[name]
            except KeyError: pass
                
            return default
            
        def UpdateHealthModifiers(self, waveinfo):
            # Update health + grow modifiers
            for key in waveinfo.iterkeys():
                diffkey = '%s_healthmod_' % (self.difficulty)
                diffkeygrow = '%s_healthgrowmod_' % (self.difficulty)
                if key.startswith(diffkeygrow):
                    unit = key.lstrip(diffkeygrow)
                    self.healthgrowmodifiers[unit] = waveinfo[key]
                elif key.startswith('healthgrowmod_'):
                    unit = key.lstrip('healthgrowmod_')
                    self.healthgrowmodifiers[unit] = waveinfo[key]
                elif key.startswith(diffkey):
                    unit = key.lstrip(diffkey)
                    self.healthmodifiers[unit] = waveinfo[key]
                elif key.startswith('healthmod_'):
                    unit = key.lstrip('healthmod_')
                    self.healthmodifiers[unit] = waveinfo[key]
                    
        def GrowHealthModifiers(self):
            # Grow healthmodifiers
            for unit, growmod in self.healthgrowmodifiers.iteritems():
                self.healthmodifiers[unit] *= growmod
                DevMsg(1, "UpdateHealthModifiers: Grown health mod %s to %f\n" % (unit, self.healthmodifiers[unit]))
                        
        def UpdateWaveInfo(self):
            if self.wave in self.waveinfo.distribution:  
                waveinfo = self.waveinfo.distribution[self.wave]
                self.curwavedistribution = self.GetFromWaveInfo(waveinfo, 'distribution', self.curwavedistribution)
                newspawnsize = self.GetFromWaveInfo(waveinfo, 'spawnsize', None)
                if newspawnsize != None:
                    self.spawnsize = newspawnsize * max(1, self.activeplayers)
                self.spawngrowrate = self.GetFromWaveInfo(waveinfo, 'growrate', self.spawngrowrate)
                self.waveincome = self.GetFromWaveInfo(waveinfo, 'waveincome', self.waveincome)
                self.waveincomegrow = self.GetFromWaveInfo(waveinfo, 'waveincomegrow', self.waveincomegrow)
                self.waveinterval = self.GetFromWaveInfo(waveinfo, 'waveinterval', self.waveinterval)
                self.waveintervalnoise = self.GetFromWaveInfo(waveinfo, 'waveintervalnoise', self.waveintervalnoise)
                self.waveintervaldecreaserate = self.GetFromWaveInfo(waveinfo, 'waveintervaldecreaserate', self.waveintervaldecreaserate)
                
                self.UpdateHealthModifiers(waveinfo)
                
            self.GrowHealthModifiers()
                
        def WavePointInFOW(self, point, owernumber):
            ''' Check if this spawn point is hidden in the FOW. '''
            origin = point.GetAbsOrigin()
            if (FogOfWarMgr().PointInFOW(origin, owernumber) and
                FogOfWarMgr().PointInFOW(origin + Vector(320.0, 0, 0), owernumber) and
                FogOfWarMgr().PointInFOW(origin - Vector(320.0, 0, 0), owernumber) and
                FogOfWarMgr().PointInFOW(origin + Vector(0.0, 320.0, 0), owernumber) and
                FogOfWarMgr().PointInFOW(origin - Vector(0.0, 320.0, 0), owernumber) ):
                return True
            return False

        def RebuildSpawnPointsList(self):
            ''' Build list of wave spawn points.'''
            
            # Get all wavepoints per priority
            wavepointsmap = {}
            wavespawnpoint = gEntList.FindEntityByClassname(None, 'overrun_wave_spawnpoint')
            while wavespawnpoint:
                if not wavespawnpoint.disabled:
                    try:
                        wavepointsmap[wavespawnpoint.priority].append(wavespawnpoint)
                    except KeyError:
                        wavepointsmap[wavespawnpoint.priority] = [wavespawnpoint]
                wavespawnpoint = gEntList.FindEntityByClassname(wavespawnpoint, 'overrun_wave_spawnpoint')
                
            # Create a list of the lists of wavepoints, sorted on priority
            self.wavespawnpoints = []
            keys = sorted(wavepointsmap.keys(), reverse=True)
            for key in keys:
                self.wavespawnpoints.append(wavepointsmap[key])
            
            if not self.wavespawnpoints:
                PrintWarning("overrun gamemode: No overrun_wave_spawnpoint entities found (wave %s)!" % (self.wave))
                
        def BuildSpawnPointListFrame(self):
            ''' Build spawn point list for this frame. '''
            players = self.GetRealPlayers()
            if not players:
                return False
            owernumber = players[0].GetOwnerNumber()
            
            for pointlist in self.wavespawnpoints:
                valid = True
                for point in pointlist:
                    if not self.WavePointInFOW(point, owernumber):
                        valid = False
                        break
                     
                if valid:
                    break
            
            if self.curwavepointpriority != pointlist[0].priority:
                DevMsg(1, "BuildSpawnPointListFrame: Wave point priority changed from %d to %d\n" % (self.curwavepointpriority, pointlist[0].priority))
                self.curwavepointpriority = pointlist[0].priority
                
            #for point in pointlist:
            #    ndebugoverlay.Box(point.GetAbsOrigin(), -Vector(8, 8, 8), Vector(8, 8, 8), 255, 0, 0, 255, 15.0)
                        
            # Randomize points
            points = list(pointlist)
            random.shuffle(points)
                     
            return points
                
        def SpawnWave(self):
            self.wave += 1
            
            if self.manager:
                self.manager.OnNewWave(self.wave)
            
            self.RebuildSpawnPointsList()
            
            oldspawnsize = self.spawnsize
            oldwaveinterval = self.waveinterval
            self.UpdateWaveInfo()
                
            # Update spawnsize (except for wave 1)
            if self.wave != 1:
                if oldspawnsize == self.spawnsize:
                    self.spawnsize = min(100000, int(ceil(self.spawnsize*self.spawngrowrate)))
                if oldwaveinterval == self.waveinterval:
                    self.waveinterval = max(0, self.waveinterval-self.waveintervaldecreaserate)
                self.waveincome = int(ceil(self.waveincome * self.waveincomegrow))

            # Send wave message to all players
            params = hudtextparms()
            params.x = -1
            params.y = -1
            params.effect = 0
            params.r1 = params.g1 = params.b1 = 255
            params.a1 = 255
            params.r2 = params.g2 = params.b2 = 255
            params.a2 = 255
            params.fadeinTime = 1.0
            params.fadeoutTime = 0.5
            params.holdTime = 5.0
            params.fxTime = 3.0
            params.channel = 0
            UTIL_HudMessageAll(params, "WAVE %d INCOMING!" % (self.wave))
            
            # Should have a curwavedistribution set
            if not self.curwavedistribution:
                return
            
            # Spawn wave
            if self.wavespawnpoints:
                # Set the amount that needs to be spawned
                self.spawnsleft = self.spawnsize
                
                # Units are selected according to the wave distribution.
                self.curwavedistributor = probchoice(self.curwavedistribution[0], self.curwavedistribution[1])
                
            try:
                # Tell wave info we created a new wave
                self.waveinfo.OnNewWave(self.wave)
            except:
                traceback.print_exc()
            
            self.waveinprogress = True
            
    def UpdateSpawner(self):
        if not self.spawnsleft:
            return
            
        tobespawned = min(self.spawnsleft, self.maxspawnperinterval)
    
        # Check if we should spawn. If there are more than overrun_max_active_enemies
        # minus tobespawned antlions present we wait.
        self.enemiesalive = filter(None, self.enemiesalive)
        alive = len(self.enemiesalive)
        
        if alive + tobespawned > overrun_max_active_enemies.GetInt():
            return
        
        # Get spawn points
        spawnpoints = self.BuildSpawnPointListFrame()
        
        # Select random spawn point from list
        # Then use the wave distribution to spawn some units
        idx = random.randint(0,len(spawnpoints)-1)
        point = spawnpoints[idx]
        info = FindPositionInfo(point.GetAbsOrigin()+Vector(0,0,32.0), -Vector(40, 40, 0), Vector(40, 40, 100))

        for i in range(0, tobespawned):
            UTIL_FindPosition(info)
            if not info.success:
                break
                
            # Create and spawn unit
            unittype = self.curwavedistributor.next()
            unit = CreateUnitNoSpawn(unittype, owner_number=OWNER_ENEMY)
            unit.BehaviorGenericClass = unit.BehaviorOverrunClass
            unit.SetAbsOrigin(info.position)
            DispatchSpawn(unit)
            unit.Activate() 
            
            # Apply modifiers
            unit.health = int(unit.health * self.healthmodifiers[unittype])
            unit.maxhealth = int(unit.maxhealth * self.healthmodifiers[unittype])
            
            # Finalize
            UTIL_DropToFloor(unit, MASK_NPCSOLID)
            self.enemiesalive.append(unit.GetHandle())
            
        self.spawnsleft -= tobespawned
        
    def SetupGame(self, gamelobby_players, gamelobby_customfields):
        """ Called by the gamelobby code (see glpkg.gamelobbyrules) """
        super(Overrun, self).SetupGame(gamelobby_players, gamelobby_customfields)
        

        for i, glp in enumerate(gamelobby_players):
            if glp[0].position == INVALID_POSITION:
                continue
            ownernumber = OWNER_LAST+glp[0].position
            SetResource(ownernumber, RESOURCE_KILLS, 15)
            
        self.UpdateWaveInfo()
        self.nextwave = gpGlobals.curtime + self.waveinterval + random.uniform(-self.waveintervalnoise, self.waveintervalnoise)

    def SetupRelationships(self, gamelobby_players):
        """ Everybody likes everybody """
        for ownernumber1 in range(OWNER_LAST, OWNER_LAST+12):
            for ownernumber2 in range(OWNER_LAST, OWNER_LAST+12):
                relationships[(ownernumber1, ownernumber2)] = D_LI
            
    def ApplyGamelobbyDataToPlayer(self, gamelobby_players, player):
        rv = super(Overrun, self).ApplyGamelobbyDataToPlayer(gamelobby_players, player)
        
        # Make sure all players are on the same team
        player.ChangeTeam(2)
        
        return rv
        
    @classmethod    
    def GetCustomFields(cls):
        """ Return a list of fields that should appear in the settings in the gamelobby """
        
        # Build wave type list
        wavetypes = []
        for key, info in dbwavetypes.iteritems():
            if info.ShouldAddWaveType():
                wavetypes.append(key)
        wavetypes.sort()
        
        fields = {
            'difficulty' : ['choices', 'normal', 'easy', 'normal', 'hard'],
            'wavetype' : ['choices', wavetypes[0] if wavetypes else ''] + wavetypes,
        }
        fields.update(super(Overrun, cls).GetCustomFields())
        return fields
        
    def ParseCustomFields(self, fields):
        super(Overrun, self).ParseCustomFields(fields)
        
        for name, values in fields.iteritems():
            if name == 'difficulty':
                self.difficulty = values[1]
            elif name == 'wavetype':
                self.wavetype = values[1]
            
    wave = 0
    
    manager = None
    maxspawnperinterval = 5
    spawninterval = 0.2
    nextspawninterval = 0.0
    waveinprogress = False
    spawnsleft = 0
    
    curwavepointpriority = 0
    
    spawnsize = 0 # Set this in wavedistributions!
    spawngrowrate = 1.15
    
    waveincome = 0 # Set this in wavedistributions!
    waveincomegrow = 1.15
    
    waveinterval = 0.0 # Set this in wavedistributions!
    waveintervalnoise = 5.0
    waveintervaldecreaserate = 1.0
    
    difficulty = 'normal'
    curwavedistribution = None
    #wavetype = 'antlions'
    waveinfo = None
 
    gametimeout_glplayers = True
    
class BaseWaveType(BaseInfo):
    donotregister = False
    id = dbwavetypeid
    
    priority = 0
    spawncloseaspossible = False # Spawn units close as possible, based on wave point priority
    
    #: Dictionary containing your wave distribution.
    #: The first number indicates at which wave the new info gets applied (you must specify 1).
    #: For each waveinfo a new dictionary is created.
    #: 'distribution' contains two lists.
    #: The first list contains the type of units in the wave.
    #: The second list the way those units are distributed.
    #: Furthermore the growrate and spawnsize can be changed.
    distribution = None
    
    @classmethod
    def ShouldAddWaveType(cls):
        ''' Whether to add this wave type to the list of available wave types in the gamelobby. '''
        return True
        
    def OnNewWave(self, wave):
        pass
        
    def Update(self, gamerules):
        ''' Allows custom code for this wave type, called each overrun think freq. '''
        pass
        
class AntlionWaveType(BaseWaveType):
    name = 'antlions'
    
    distribution = {
        0 : {
                # Prepare time
                'easy_waveinterval' : 20,
                'normal_waveinterval' : 15,
                'hard_waveinterval' : 10,
                
                'waveintervaldecreaserate' : -3,
                
                HModHard('unit_antlion') : 1.2,
                HModHard('unit_antlionworker') : 1.2,
            },
        1 : { 
                'spawnsize' : 8,
                
                'waveincome' : 5,
                'waveincomegrow' : 1.15,
        
                'distribution' : (['unit_antlion'], 
                                 [1.0]),
            },
        3 : {
                'distribution' : (['unit_antlion', 'unit_antlionworker'], 
                                  [0.80, 0.20]),
            },
        5 : {
                'distribution' : (['unit_antlion', 'unit_antlionworker'], 
                                  [0.75, 0.25]),
                                  
                HModGrowEasy('unit_antlion') : 1.05,
                HModGrowNormal('unit_antlion') : 1.15,
                HModGrowHard('unit_antlion') : 1.25,
            },
        7 : {
                'distribution' : (['unit_antlion', 'unit_antlionsuicider', 'unit_antlionworker', 'unit_antlionguard'], 
                                  [0.73, 0.05, 0.20, 0.02]),
                'growrate' : 1.1,
                
                'waveintervaldecreaserate' : 1, # At this point we added a lot of time, so we start decreasing again.
                
                HModGrowEasy('unit_antlionworker') : 1.05,
                HModGrowNormal('unit_antlionworker') : 1.1,
                HModGrowHard('unit_antlionworker') : 1.2,
            },
        10 : {
                'distribution' : (['unit_antlion', 'unit_antlionsuicider', 'unit_antlionworker', 'unit_antlionguard', 'unit_antlionguardcavern'], 
                                  [0.72, 0.05, 0.20, 0.02, 0.01]),
                'growrate' : 1.05,
                
                HModGrowNormal('unit_antlionguard') : 1.05,
                HModGrowHard('unit_antlionguard') : 1.1,
                HModGrowNormal('unit_antlionguardcavern') : 1.05,
                HModGrowHard('unit_antlionguardcavern') : 1.1,
             },
    }
    
class ZombieWaveType(BaseWaveType):
    name = 'zombie'
    
    spawncloseaspossible = False
    
    distribution = {
        0 : {
                # Prepare time
                'easy_waveinterval' : 15,
                'normal_waveinterval' : 10,
                'hard_waveinterval' : 5,
                'waveintervaldecreaserate' : -3,
                
                HModHard('unit_zombie') : 1.2,
                HModHard('unit_fastzombie') : 1.2,
                HModHard('unit_headcrab_fast') : 1.2,
                HModHard('unit_headcrab') : 1.2,
            },
        1 : {
                'distribution' : (['unit_headcrab', 'unit_zombie'], 
                                  [0.75, 0.25]),
                'spawnsize' : 10,
                'growrate' : 1.15,
                
                'waveincome' : 5,
                'waveincomegrow' : 1.15,
            },
        2 : {
                'distribution' : (['unit_headcrab', 'unit_zombie'], 
                                  [0.5, 0.5]),
                'growrate' : 1.10,
                
            },
        3 : {
                'distribution' : (['unit_headcrab_fast', 'unit_zombie', 'unit_fastzombie'], 
                                  [0.2, 0.5, 0.3]),
                       
                HModGrowEasy('unit_zombie') : 1.02,
                HModGrowNormal('unit_zombie') : 1.13,
                HModGrowHard('unit_zombie') : 1.25,
                
                HModGrowEasy('unit_fastzombie') : 1.02,
                HModGrowNormal('unit_fastzombie') : 1.06,
                HModGrowHard('unit_fastzombie') : 1.12,
                       
                HModGrowEasy('unit_headcrab_fast') : 1.02,
                HModGrowNormal('unit_headcrab_fast') : 1.08,
                HModGrowHard('unit_headcrab_fast') : 1.2,
            },
            
        5 : {
                'distribution' : (['unit_headcrab_fast', 'unit_headcrab_poison', 'unit_zombie', 'unit_fastzombie', 'unit_zombine'], 
                                  [0.1, 0.05, 0.45, 0.3, 0.1]),
        
                'waveintervaldecreaserate' : 1, # At this point we added a lot of time, so we start decreasing again.
            },
            
        7 : {
                'distribution' : (['unit_headcrab_fast', 'unit_headcrab_poison', 'unit_zombie', 'unit_fastzombie', 'unit_zombine', 'unit_poisonzombie'], 
                                  [0.1, 0.05, 0.45, 0.3, 0.08, 0.02]),
                                  
                HModGrowEasy('unit_headcrab_poison') : 1.02,
                HModGrowNormal('unit_headcrab_poison') : 1.08,
                HModGrowHard('unit_headcrab_poison') : 1.15,
                
                HModGrowEasy('unit_zombine') : 1.02,
                HModGrowNormal('unit_zombine') : 1.08,
                HModGrowHard('unit_zombine') : 1.15,
            },
    }
    
    spotid = 0
    nextfirecannisters = -1
    minnextfire = 60.0
    maxnextfire = 100.0
    minfirecan = 1
    maxfirecan = 1
    mincansize = 3
    maxcansize = 6
    headcrabtype = "0"
    
    def OnNewWave(self, wave):
        if wave == 6:
            self.headcrabtype = "1"
            
        if wave == 8:
            self.minnextfire = 40.0
            self.maxnextfire = 80.0
            self.minfirecan = 1
            self.maxfirecan = 2
        elif wave == 13:
            self.minnextfire = 30.0
            self.maxnextfire = 45.0
            self.minfirecan = 1
            self.maxfirecan = 2
            
    def Update(self, gamerules):
        if self.nextfirecannisters == -1:
            self.nextfirecannisters = gpGlobals.curtime + random.uniform(50.0, 100.0)
            
        if self.nextfirecannisters < gpGlobals.curtime:
            self.nextfirecannisters = gpGlobals.curtime + random.uniform(self.minnextfire, self.maxnextfire)
            
            # Fire some cannisters
            for i in range(0, random.randint(self.minfirecan, self.maxfirecan)):
                building = self.RandomEnemyBuilding()
                if building:
                    origin = building.GetAbsOrigin()
                    targetpos = RandomNavAreaPositionWithin(origin - Vector(1500, 1500, 0), origin + Vector(1500, 1500, 0))
                else:
                    targetpos = RandomNavAreaPosition()
                self.FireCannister(targetpos)
           
    def RandomEnemyBuilding(self):
        buildings = []
        for i in buildinglist.itervalues():
            buildings += i
        return random.sample(buildings, 1)[0] if buildings else None
           
    def FireCannister(self, targetpos):
        spotname = "hcspot%d" % (self.spotid)
    
        # Create a launch spot
        spot = CreateEntityByName( "info_target" )
        spot.KeyValue("targetname", spotname )
        spot.SetAbsOrigin(targetpos + Vector(64.0, 90.0, 712.0)) # Start position
        spot.SetAbsAngles(QAngle( 60, 0, 0 )) 
        DispatchSpawn(spot)

        # Create and setup the canister
        can = CreateUnitNoSpawn( "unit_headcrabcanister" )
        can.SetOwnerNumber(OWNER_ENEMY)
        can.KeyValue("name", "head" )
        can.KeyValue( "HeadcrabType", "0")
        can.KeyValue( "HeadcrabCount", "%d" % (random.randint(self.mincansize, self.maxcansize)))
        can.KeyValue( "FlightSpeed", "512")
        can.KeyValue( "FlightTime", "1")
        can.KeyValue( "Damage" , "75" )
        can.KeyValue( "DamageRadius", "250" )
        can.KeyValue( "LaunchPositionName", spotname)
        can.SetAbsOrigin(targetpos)
        can.SetAbsAngles(QAngle( -90, 0, 0 ))
        DispatchSpawn(can)      
        
        self.spotid += 1
        
        # Cleanup
        g_EventQueue.AddEvent( can, "FireCanister", variant_t(), 1.0, None, None, 0 )
        g_EventQueue.AddEvent( spot, "kill", variant_t(), 25.0, None, None, 0 )
            
    
class CombineWaveType(BaseWaveType):
    name = 'combine'
    
    distribution = {
        0 : {
                # Prepare time
                'easy_waveinterval' : 20,
                'normal_waveinterval' : 15,
                'hard_waveinterval' : 10,
                'waveintervaldecreaserate' : -3,
            },
        1 : {
                'distribution' : (['unit_combine'], 
                                  [1.0]),
                'spawnsize' : 5,
                'growrate' : 1.1,
                
                'waveincome' : 5,
                'waveincomegrow' : 1.15,
            },
        3 : {
                'distribution' : (['unit_combine', 'unit_combine_sg'], 
                                  [0.5, 0.5]),
                'growrate' : 1.05,
            },
        5 : {
                'distribution' : (['unit_combine', 'unit_combine_sg', 'unit_combine_ar2'], 
                                  [0.35, 0.35, 0.30]),
            },
        7 : {
                'distribution' : (['unit_combine', 'unit_combine_sg', 'unit_combine_ar2', 'unit_combine_elite'], 
                                  [0.30, 0.30, 0.10, 0.30]),
                'waveintervaldecreaserate' : 1, # At this point we added a lot of time, so we start decreasing again.
            },
        10 : {
                'distribution' : (['unit_combine', 'unit_combine_sg', 'unit_combine_ar2', 'unit_combine_elite', 'unit_strider'], 
                                  [0.30, 0.30, 0.10, 0.29, 0.01]),
                'growrate' : 1.02,
            },
    }
    
class InfectedWaveType(BaseWaveType):
    name = 'infected'
    
    @classmethod
    def ShouldAddWaveType(cls):
        return 'l4d' in dbgamepackages.keys() and dbgamepackages['l4d'].loaded
    
    distribution = {
        0 : {
                # Prepare time
                'easy_waveinterval' : 15,
                'normal_waveinterval' : 10,
                'hard_waveinterval' : 5,
                'waveintervaldecreaserate' : -3,
                
                HModHard('unit_infected') : 1.2,
            },
            
        1 : {
                'distribution' : (['unit_infected'],
                                  [1.0]),
                                  
                'spawnsize' : 8,
                
                'waveincome' : 5,
                'waveincomegrow' : 1.15,
            },
        4 : {
                HModGrowEasy('unit_infected') : 1.05,
                HModGrowNormal('unit_infected') : 1.2,
                HModGrowHard('unit_infected') : 1.3,
            },
        6 : {
                'waveintervaldecreaserate' : 1, # At this point we added a lot of time, so we start decreasing again.
            },
    }
    
if isserver:
    @concommand('overrun_nextwave', 'Spawn the next wave.', FCVAR_CHEAT)
    def cc_overrun_nextwave(args):
        if gamerules.info.name != OverrunInfo.name:
            print('Overrun mode not active.')
            return
        gamerules.nextwave = gpGlobals.curtime # Wave time changed to earlier, notify hud.
        gamerules.SpawnWave()

    def GetWaveTypes():
        if gamerules.info.name != OverrunInfo.name:
            return []
        return dbwavetypes.keys()
    
    @concommand('overrun_setwavetype', 'Changes the wave type.', FCVAR_CHEAT, completionfunc=AutoCompletion(GetWaveTypes))
    def cc_overrun_setwavetype(args):
        if gamerules.info.name != OverrunInfo.name:
            return
        if args[1] not in dbwavetypes.keys():
            PrintWarning('Invalid wave type. Valid options are: %s' % (str(dbwavetypes.keys())))
            return
        gamerules.wavetype = args[1]
        
    @concommand('overrun_debug_status', 'Prints current status.', FCVAR_CHEAT)
    def cc_overrun_debug_status(args):
        if gamerules.info.name != OverrunInfo.name:
            print('Overrun mode not active.')
            return
        print('OVERRUN STATUS: ')
        print('\twave: %d' % (gamerules.wave))
        print('\tspawnsleft: %d' % (gamerules.spawnsleft))
        print('\tspawnsize: %d' % (gamerules.spawnsize))
        print('\thealth modifiers: ')
        for unit, modifier in gamerules.healthmodifiers.iteritems():
            print('\t\t%s -> %f ' % (unit, modifier))
        print('\thealth grow modifiers: ')
        for unit, modifier in gamerules.healthgrowmodifiers.iteritems():
            print('\t\t%s -> %f ' % (unit, modifier))

class OverrunInfo(GamerulesInfo):
    name = 'overrun'
    displayname = '#Overrun_Name'
    description = '#Overrun_Description'
    cls = Overrun
    mappattern = '^or_.*$'
    factionpattern = '^overrun_.*$'
    useteams = False
    supportcpu = True
    huds = [
        'wars_game.hud.HudOverrun',
        'core.hud.HudPlayerNames',
    ]
    