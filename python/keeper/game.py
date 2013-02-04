from srcbase import RegisterTickMethod, UnregisterTickMethod
from vmath import vec3_origin, QAngle
from core.gamerules import GamerulesInfo, WarsBaseGameRules
from core.units import KillAllUnits, unitlistpertype, unitlist
from core.resources import GiveResources, FullResourceUpdatePlayers
from gameinterface import engine, concommand, FCVAR_CHEAT
from gamerules import gamerules
from profiler import profile
import time
import math
import random
from collections import defaultdict
from tiles import ClearTileLists
from rooms.createroom import ClearControllerLists
from rooms import GetGoldInTreasureRooms
from playermgr import dbplayers

from common import *
from taskqueue import taskqueues

import keeperworld

if isserver:
    from utils import UTIL_GetPlayers, UTIL_Remove, UTIL_HudMessageAll, hudtextparms
    from entities import CreateEntityByName, DispatchSpawn, RespawnPlayer, gEntList
    from gold import ResetGold
else:
    from materials import ProceduralTexture, ImageFormat
    
removelist = set([
    'dk_gold',
    'env_projectedtexture',
])
    
class KeeperGame(WarsBaseGameRules):
    nexttaskqueueupdate = 0.0
    nextmarinedroptime = 0.0
    nextpaydaytime = 0.0
    keeperworld = None
    
    if isclient: maxgold = 0
    
    def InitGamerules(self):
        if isclient:
            self.minimapsize = 512
            self.minimaptex = ProceduralTexture('__rt__skminimap', None, self.minimapsize, self.minimapsize, ImageFormat.IMAGE_FORMAT_RGBA8888, 0)
            self.minimaptex.SetAllPixels(0)
            
        super(KeeperGame, self).InitGamerules()
        
        if keeperworld.keeperworld:
            self.keeperworld = keeperworld.keeperworld
        
        # BUG: When reloading a game package, the new keeperworld entity is created on the client
        #      before the modules are reload (when creating it here).
        # BUG2: The initial gold display tends to be incorrect
        RegisterTickMethod(self.LoadDelayed, 0.1, False)
        RegisterTickMethod(self.LoadDelayed2, 1.0, False)
        
        print('%s INITIALIZING KEEPER GAME' % (isclient))
        
        # TODO: Don't really want this here.
        for k, v in dbplayers.iteritems():
            v.faction = 'keeper'
        
        ClearTileLists()
        ClearControllerLists()
        
        if isserver:
            # Remove any old dk entity
            ent = gEntList.FirstEnt()
            while ent:
                if ent.GetClassname() in removelist:
                    UTIL_Remove(ent)
                ent = gEntList.NextEnt(ent)
            gEntList.CleanupDeleteList()
            
            ResetGold()

            # Spawn a dk light
            self.dklight = CreateEntityByName('env_dk_light')
            self.dklight.KeyValue('ambientangles', '0 107 0')
            self.dklight.KeyValue('ambientcolor1', '49 112 157 1')
            self.dklight.KeyValue('ambientcolor2', '90 129 150 1')
            self.dklight.KeyValue('ambientscale1', '.35')
            self.dklight.KeyValue('ambientscale2', '.1')
            self.dklight.KeyValue('angles', '70 0 0')
            self.dklight.KeyValue('color', '182 145 95 50')
            self.dklight.KeyValue('colortransitiontime', '0.5')
            self.dklight.KeyValue('distance', '20000')
            self.dklight.KeyValue('enableshadows', '1')
            self.dklight.KeyValue('fov', '1')
            self.dklight.KeyValue('groundscale', '.1')
            self.dklight.KeyValue('nearz', '4')
            self.dklight.KeyValue('northoffset', '-200')
            self.dklight.KeyValue('specularangles', '64 283 0')
            self.dklight.KeyValue('specularcolor', '114 99 40')
            self.dklight.KeyValue('specularpower', '14')
            self.dklight.KeyValue('texturename', 'effects/keeperlight')

            DispatchSpawn(self.dklight)
            self.dklight.Activate()

        if taskqueues != None:
            # Clear any old taskqueus
            taskqueues.clear()
            
            # Ensure new taskqueues are there
            for i in range(2, 6): taskqueues[i]
            
        # Gold per owner
        self.playergold = defaultdict(lambda : 0)

        if isserver:
            KillAllUnits()
                
        # Make sure everybody is a dk player
        if isserver:
            players = UTIL_GetPlayers()
            for player in players:
                if player.GetClassname() != 'dk_player':
                    print('Respawning player as keeper player')
                    player = RespawnPlayer(player, 'dk_player')
                    player.ChangeFaction('keeper')

            # Init marine drop event
            self.marines = []
            self.nextmarinedroptime = gpGlobals.curtime + sk_marine_invade_init_time.GetFloat()
            self.marinecount = 1 # Start with one
            self.marinekeys = set()
            self.marinetargetkey = (0,0)
            self.marineexpmin = 100
            self.marineexpmax = 400
            
            # Payday time
            self.nextpaydaytime = gpGlobals.curtime + sk_payday_frequency.GetFloat()
                    
    def LoadDelayed(self):
        if isserver:
            # Create the world
            self.CreateKeeperWorld()
            
    def LoadDelayed2(self):
        # Add some starting resources
        if isserver:
            GiveResources(2, [('gold', 4000)])
            
            for o, tq in taskqueues.iteritems():
                totalgold, maxtotalgold = GetGoldInTreasureRooms(tq.ownernumber)
                tq.SetCurrentGold(totalgold, maxtotalgold) # TODO: Move somewhere else?
                tq.UpdateMaxGold()
            
        # Activate game over check
        self.dkgameactive = True

    def ShutdownGamerules(self):
        super(KeeperGame, self).ShutdownGamerules()
        
        if isclient:
            self.minimaptex.Shutdown()
            self.minimaptex = None
        
        # Just to be sure
        try: UnregisterTickMethod(self.LoadDelayed)
        except: pass
        try: UnregisterTickMethod(self.LoadDelayed2)
        except: pass
        
        print('%s SHUTTING DOWN KEEPER GAME' % (isclient))
        
        if isserver:
            if self.dklight:
                self.dklight.Remove()
                self.dklight = None
        
        if isserver:
            engine.ServerCommand('profiling_start\n')
            engine.ServerExecute()
        else:
            engine.ExecuteClientCmd('cl_profiling_start')
        
        self.DestroyKeeperWorld()
    
        if isserver:
            engine.ServerCommand('profiling_stopandprint\n')
            engine.ServerExecute()
            
            #gEntList.CleanupDeleteList()
        else:
            engine.ExecuteClientCmd('cl_profiling_stopandprint')
       
    @profile('KeeperWorldCreation')       
    def CreateKeeperWorld(self):
        keeperworld = CreateEntityByName('keeperworld')
        keeperworld.SetAbsOrigin(vec3_origin)
        DispatchSpawn(keeperworld)
        keeperworld.Activate()
        self.keeperworld = keeperworld
        
    @profile('KeeperWorldDestruction')
    def DestroyKeeperWorld(self):
        starttime = time.time()

        kw = self.keeperworld
        if kw:
            print('%s Destroying keeperworld...' % (isclient))
            if isserver:
                try:
                    kw.Remove()
                except:
                    PrintWarning("Failed to remove keeper world on reloading\n")
                self.keeperworld = None
            else:
                kw.ClearTileGrid()
        print('\tDone. %f' % (time.time() - starttime))
        
    def GetPlayerSpawnSpot(self, player):
        spawnspot = super(KeeperGame, self).GetPlayerSpawnSpot(player)
        
        player.SetLocalAngles(QAngle(-115, 90, 0))
        player.SnapEyeAngles(QAngle(65, 90, 0))
        
        return spawnspot

    def GetPlayerClassname(self):
        return 'dk_player'
        
    def ClientCommand(self, player, args):
        keeperworld = self.keeperworld
        ownernumber = player.GetOwnerNumber()
        if args[0] == 'dk_block_select':
            key = (int(args[1]), int(args[2]))
            b = keeperworld.tilegrid[key]
            if b not in player.selectedblocks:
                player.selectedblocks.add(keeperworld.tilegrid[key])
                b.Select(player)
            return True
        elif args[0] == 'dk_block_deselect':
            key = (int(args[1]), int(args[2]))
            try:
                b = keeperworld.tilegrid[key]
                player.selectedblocks.remove(keeperworld.tilegrid[key])
                b.Deselect(player)
            except KeyError:
                PrintWarning('Invalid key %s\n' % (str(key)))
            return True
            
        elif args[0] == 'dk_blockrange_auto':
            keystart = (int(args[1]), int(args[2]))
            keyend = (int(args[3]), int(args[4]))

            player.StartSelection(keystart)
            player.UpdateSelection(keyend)
            player.EndSelection()
            return True
        elif args[0] == 'dk_release_grabbed':
            # TODO: Get tile at which we are trying to drop and verify
            # Release first valid unit in the list
            grabbedunits = list(player.grabbedunits)
            for unit in grabbedunits:
                try:
                    fngrab = unit.PlayerGrab
                except AttributeError:
                    continue
                fngrab(player, True)
                break
            return True
            
        elif args[0] == 'dk_release_grabbed_all':
            # TODO: Get tile at which we are trying to drop and verify
            # Release first valid unit in the list
            grabbedunits = list(player.grabbedunits)
            for unit in grabbedunits:
                try:
                    fngrab = unit.PlayerGrab
                except AttributeError:
                    continue
                fngrab(player, True)
            return True
            
        elif self.ClientCommandSettings(player, args):
            return True
            
        return super(KeeperGame, self).ClientCommand(player, args)
        
    def ClientCommandSettings(self, player, args):
        command = args[0]
        if command == 'dk_spawn_marines':
            self.SpawnMarines()
            return True
            
        elif command == 'dk_set_marine_interval':
            print 'Setting marine interval to %s and %s' % (args[1], args[2])
            sk_marine_invade_interval_min.SetValue(float(args[1]))
            sk_marine_invade_interval_max.SetValue(float(args[2]))
            self.nextmarinedroptime = gpGlobals.curtime + random.uniform(
                    sk_marine_invade_interval_min.GetFloat(),
                    sk_marine_invade_interval_max.GetFloat())
            return True
            
        return False
        
    def Think(self):
        super(KeeperGame, self).Think()
        
        if self.nexttaskqueueupdate < gpGlobals.curtime:
            for o, tq in taskqueues.iteritems():
                tq.ownernumber = o
                tq.keeperworld = self.keeperworld
                totalgold, maxtotalgold = GetGoldInTreasureRooms(tq.ownernumber)
                tq.SetCurrentGold(totalgold, maxtotalgold) # TODO: Move somewhere else?
                tq.Update()
            self.nexttaskqueueupdate = gpGlobals.curtime + 0.5
            
        if not self.dkgameactive:
            return
        
        # TODO: Make this per player check
        try:
            heart = unitlistpertype[2]['dk_heart'][0]
        except IndexError:
            heart = None
            
        if not heart:
            if not self.dkgameover:
                print('Game Over')
                
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
                params.holdTime = 15.0
                params.fxTime = 10.0
                params.channel = 0
                UTIL_HudMessageAll(params, 'Game Over')
                
                self.dkgameover = True
        else:
            self.marinetargetkey = self.keeperworld.GetKeyFromPos(heart.GetAbsOrigin())
            
        # Payday
        if self.nextpaydaytime < gpGlobals.curtime:
            print('PAYDAY')
            for ownernumber, l in unitlist.iteritems():
                if ownernumber < 2:
                    continue
                for unit in l:
                    try: fndispatchevent = unit.DispatchEvent
                    except AttributeError: continue
                    fndispatchevent('OnPayDay')
        
            self.nextpaydaytime = gpGlobals.curtime + sk_payday_frequency.GetFloat()
        
        # Check drop marines
        hadmarines = len(self.marines) > 0
        self.marines = filter(None, self.marines) # Filter handles which went None
        if not self.marines:
            if hadmarines:
                self.nextmarinedroptime = gpGlobals.curtime + random.uniform(
                        sk_marine_invade_interval_min.GetFloat(),
                        sk_marine_invade_interval_max.GetFloat())
            elif self.nextmarinedroptime < gpGlobals.curtime:
                self.SpawnMarines()
            
    def SpawnMarines(self):
        # TODO: determine target
        try:
            heart = unitlistpertype[2]['dk_heart'][0]
        except IndexError:
            return
    
        tilegrid = self.keeperworld.tilegrid
        if len(self.marinekeys) > 4: # Stop creating new dig routes after 4 times
            print('Using existing spot to drop marines')
            key = random.sample(self.marinekeys, 1)[0]
        else:
            print('Finding spot to drop marines')
            for i in range(0, 100):
                key = random.sample(tilegrid.keys(), 1)[0]
                if tilegrid[key] and keydist(self.marinetargetkey, key) > 10:
                    break

        if tilegrid[key]:
            units = self.keeperworld.DropUnitsAt(key=key, units=['unit_dk_marine']*int(round(self.marinecount)))
            for unit in units: 
                unit.AddExperience(random.randint(int(self.marineexpmin), int(self.marineexpmax)))
                unit.targetheart = heart
                self.marines.append(unit)
            
            self.marinecount = min(5, self.marinecount * 1.35)
            self.marinekeys.add(key)
            
            self.marineexpmin *= 1.25
            self.marineexpmax *= 1.6
            
        self.nextmarinedroptime = gpGlobals.curtime + 1.0 # Just to be sure, in case something goes wrong
    
    def GetCreateImpCost(self, ownernumber):
        n = len(unitlistpertype[ownernumber]['unit_imp'])
        #return int((n * 50) ** 1.25)
        return 150 + n * 150
            
    dkgameover = False
    dkgameactive = False
            
    # Dungeon Keeper music list
    '''musicplaylist = [
        "keeper/music/01_Russell_Shaw_SnuggleDell.wav",
        "keeper/music/02_Russell_Shaw_Talons_39_Barrow.wav",
        "keeper/music/03_Russell_Shaw_The_Lair.wav",
        "keeper/music/04_Russell_Shaw_Troll_Factory.wav",
        "keeper/music/05_Russell_Shaw_Echos.wav",
        "keeper/music/06_Russell_Shaw_Dungeon_Keeper.wav",
    ]'''
    
    # Alien Swarm music list
    musicplaylist = [
        'music/shockstinger01.wav',
        'music/shockstinger02.wav',
        'music/shockstinger03.wav',
        'music/timor_battle.wav',
        'music/as01.wav',
        'music/rydberg_rumble.wav',
        'music/solo/briefing_main.wav',
    ]
    
class KeeperInfo(GamerulesInfo):
    name = 'keeper'
    displayname = '#Keeper_Name'
    description = '#Keeper_Description'
    cls = KeeperGame
    mappattern = '^dk_.*$'
    factionpattern = '^(rebels|combine)$'
    huds = [
        'core.hud.HudPlayerNames',
        'keeper.hud.minimap.Minimap',
    ]
    
if isserver:
    @concommand('keeper_nextwave', 'Trigger next marine wave', FCVAR_CHEAT)
    def cc_keeper_nextwave(args):
        if gamerules.info.name != KeeperInfo.name:
            print('Swarm Keeper mode not active.')
            return
        gamerules.nextmarinedroptime = gpGlobals.curtime 