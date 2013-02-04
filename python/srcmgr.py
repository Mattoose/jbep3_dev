"""
Provides general information and intializes the Python side of the game.
"""
import sys, gc, os, re
import weakref
import pickle
import pkgutil
import traceback 
from collections import defaultdict

try:
    import sqlite3
except ImportError:
    Warning('sqlite3 missing')
    sqlite3 = None
    
from Queue import Queue

from srcbase import AbsToRel, RegisterTickMethod
from gameinterface import engine
from gamerules import GameRules
from kvdict import LoadFileIntoDictionaries

import makedocs

# Global indicating the current version of Half-Life 2: Wars
# MACRO / MINOR / MICRO
VERSION = (2, 0, 5)
DEVVERSION = None

# Gameinfo
gameinfo = {}
steamappid = None

# Level related globals
levelname = ""
levelinit = False
levelpreinit = False

revisioninfopath = os.path.join(os.path.split(__file__)[0], 'srcmgr.info')
versioninfopath = os.path.join(os.path.split(__file__)[0], 'version.info')
def _Init():
    """ Initialize """
#    global gameinfo, steamappid, DEVVERSION
#    
#    # Load gameinfo
#    gameinfo = LoadFileIntoDictionaries('gameinfo.txt')
#    steamappid = int(gameinfo['FileSystem']['SteamAppId'])
#    
#    if isclient or engine.IsDedicatedServer():
#        # In case of the developers/svn build, check the revision number
#        # In the other case check the global version number
#        # The current version is retrieved from the web.
#        revision = get_svn_revision()
#        if revision != 'SVN-unknown':
#            DEVVERSION = revision
#            try:
#                fp = open(revisioninfopath, 'rb')
#                oldrevision = pickle.load(fp)
#                fp.close()
#                if revision != oldrevision:
#                    OnRevisionChanged(oldrevision, revision)
#            except IOError:
#                OnRevisionChanged(None, revision)
#                
#            if CommandLine() and CommandLine().FindParm('-override_vpk') == 0:
#                if isclient:
#                    from vgui.notification import Notification
#                    Notification('Specify -override_vpk', 
#                        ('The developers build must be runned with the launch parameter "-override_vpk".\n')
#                    )
#                else:
#                    print('The developers build must be runned with the launch parameter "-override_vpk".')
#        else:
#            try:
#                fp = open(versioninfopath, 'rb')
#                oldrversion = pickle.load(fp)
#                fp.close()
#                if VERSION != oldrversion:
#                    OnVersionChanged(oldrversion, VERSION)
#            except IOError:
#                OnVersionChanged(None, VERSION)
#    else:
#        # Grab revision
#        revision = get_svn_revision()
#        if revision != 'SVN-unknown':
#            DEVVERSION = revision
            
    # Turn off garbage collect, so it won't cleanup on unpredictable moments.
    # Instead we just cleanup on end of the level
    # NOTE: This doesn't affects cleanup of simple things, but only of cyclic garbage collecting
    # gc.disable()
    
    # Don't need to check very often
    # IMPORTANT: If you run a thread you might want to temporary change this.
    sys.setcheckinterval(500)

def RemoveJunkPycFiles(path):
    try:
        for filename in os.listdir(path):
            fullpath = os.path.join(path, filename)
            root, ext = os.path.splitext(filename)
            if os.path.isdir(fullpath):
                RemoveJunkPycFiles(fullpath)
            elif ext == '.pyc':
                fullpypath = os.path.join(path, root+'.py')
                if not os.path.exists(fullpypath):
                    print 'Removing: %s' % (fullpath)
                    os.remove(fullpath)
    except IOError:
        PrintWarning('RemoveJunkPycFiles: failed to remove junk pyc files\n')
        
def OnRevisionChanged(oldrevision, revision):
    """ Called when the revision changed. Deletes pyc files without py files """
    print('Revision number changed from %s to %s, performing checks...' % (oldrevision, revision))

    # Check if each .pyc file has a .py file. If that's not the case the .py file got deleted.
    # Then we can also remove the .pyc file.
    RemoveJunkPycFiles('maps')
    RemoveJunkPycFiles('python')
    
    # Write new revision number away
    fp = open(revisioninfopath, 'wb')
    pickle.dump(revision, fp)
    fp.close()
    
def OnVersionChanged(oldversion, version):
    """ Called when the version changed. Deletes pyc files without py files """
    print('Version number changed from %s to %s, performing checks...' % (oldversion, version))
    
    # Check if each .pyc file has a .py file. If that's not the case the .py file got deleted.
    # Then we can also remove the .pyc file.
    RemoveJunkPycFiles('maps')
    RemoveJunkPycFiles('python')
    
    # Write new version number away
    fp = open(versioninfopath, 'wb')
    pickle.dump(version, fp)
    fp.close()
    
# Dealing with threads
threadcallbacks = Queue()
def DoThreadCallback(method, args):
    threadcallbacks.put( (method, args) )
    
def CheckThreadsCallbacks():
    while not threadcallbacks.empty():
        callback = threadcallbacks.get_nowait()
        if callback:
            try:
                callback[0](*callback[1])
            except:
                traceback.print_exc()
                
RegisterTickMethod(CheckThreadsCallbacks, 0.2)

# Level init and shutdown methods
def _LevelInitPreEntity(lvlname):
    global levelname, levelpreinit
    levelname = lvlname
    
    levelpreinit = True
    
def _LevelInitPostEntity():
    """ Called when all map entities are created.
    """
    global levelinit

    # Set level init to true
    levelinit = True
            
def _LevelShutdownPreEntity():
    """ Called before the entities are removed from the map.
        Dispatches related callbacks.
    """
    pass
    
def _LevelShutdownPostEntity():
    """ Called when all entities are removed.
        Dispatches related callbacks. """    
    global levelpreinit, levelinit, levelname

    # Put levelinit to false
    levelpreinit = False
    levelinit = False    
    levelname = ""
   
    # Cleanup memory
    gc.collect()

def _OnChatPrintf(playerindex, filter, msg):
    if GameRules() and GameRules().info.name == 'gamelobbyrules':
        GameRules().gl.PrintChat(playerindex, filter, msg)
        
def _GetVersion():
    return '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
        
# Temporary signal methods for c++
def _CheckReponses(responses):
    for r in responses:
        if isinstance(r[1], Exception):
            PrintWarning('Error in receiver %s (module: %s): \n%s' % 
                (r[0], r[0].__module__, r[2]))
            
def _CallSignal(method, kwargs):
    _CheckReponses(method(**kwargs))

# Useful methods        
def VerifyIsClient():
    """ Throws an exception if this is not the client. To be used when importing modules. """
    if not isclient:
        raise ImportError('Cannot import this module on the server')
            
def VerifyIsServer():
    """ Throws an exception if this is not the client. To be used when importing modules. """
    if not isserver:
        raise ImportError('Cannot import this module on the client')

def ImportSubMods(mod):
    """ Import all sub modules for the specified module. """
    name = mod.__name__
    path = mod.__path__
    pathrel = []
    for v in path:
        pathrel.append(os.path.normpath(AbsToRel(os.path.normpath(v)))) 
    for item in pkgutil.iter_modules(pathrel):
        submod = '%s.%s' % (name,item[1])
        try:
            __import__(submod)   
            sys.modules[submod]
        except:
            traceback.print_exc()

def ReloadSubMods(mod, exludelist=None):
    """ Reloads all sub modules for the specified module. """
    name = mod.__name__
    path = mod.__path__
    pathrel = []
    for v in path:
        pathrel.append(os.path.normpath(AbsToRel(os.path.normpath(v)))) 
    for item in pkgutil.iter_modules(pathrel):
        submod = '%s.%s' % (name,item[1])
        try:
            __import__(submod)  # Might not be imported in the first place because the module is just added
            submod_ref = sys.modules[submod]
            if not exludelist or not (submod_ref in exludelist):
                reload(sys.modules[submod])
        except:
            traceback.print_exc()

