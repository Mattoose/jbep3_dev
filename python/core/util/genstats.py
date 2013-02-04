from srcbase import *
from core.units.info import dbunits, UnitInfo, dmgtypes
from core.units import UnitBaseShared
from core.abilities.info import dbabilities
from core.factions import dbfactions
from core.buildings import WarsBuildingInfo
from gameinterface import concommand, engine
from entities import GetClassByClassname
import srcmgr

from collections import defaultdict
import os
from datetime import datetime

def WriteRow(fp, elements, helpstring=None):
    fp.write('<tr>\n')
    for e in elements:
        if type(e) == tuple:
            fp.write('        <td title="%s">%s</td>\n' % (e[1], e[0]))
        else:
            fp.write('        <td>%s</td>\n' % (e))
    fp.write('</tr>\n')
     
def StringifyCosts(costs):
    if not costs:
        return '-'
    out = ''
    for i, c in enumerate(costs):
        if i != 0: out += ' <b>OR</b> '
        for j, ce in enumerate(c):
            if j != 0: out += ' + '
            out += '%d %s' % (ce[1], ce[0])
    return out
    
def GetAttribute(cls, name, defaultvalue=None):
    try:
        return getattr(cls, name)
    except AttributeError:
        return defaultvalue
        
def WriteHeader(fp, title):
    fp.write('<!DOCTYPE HTML>\n')
    fp.write('<html>\n')
    fp.write('<head>\n')
    fp.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n')
    fp.write('<title>%s</title>\n' % (title))
    fp.write('''<style>
    table.fancy {
      margin: 1em 1em 1em 0;
      background: whitesmoke;
      border-collapse: collapse;
    }
    table.fancy tr:hover {
       background: lightsteelblue !important;
    }
    table.fancy th, table.fancy td {
      border: 1px silver solid;
      padding: 0.2em;
    }
    table.fancy th {
      background: gainsboro;
      text-align: left;
    }
    table.fancy caption {
      margin-left: inherit;
      margin-right: inherit;
    }
</style>''')
    fp.write('</head>\n')
    
    fp.write('<body>\n')
    fp.write('<p><b>Generated %s UTC - Version %s</b></p>' % (datetime.utcnow(), srcmgr.DEVVERSION if srcmgr.DEVVERSION else str(srcmgr.VERSION)))
    
def WriteEnd(fp):
    fp.write('</body>\n</html>\n')

def GenerateStats(filename, units, title='Unit Statistics'):
    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.mkdir(folder)

    fp = open(filename, 'wb')
    WriteHeader(fp, title)

    fp.write('<table class="fancy">\n')
    fp.write('''    <tr>
        <th>Name</th>
        <th>FancyName</th>
        <th>Build Time</th>
        <th>Costs</th>
        <th>Health</th>
        <th>Energy</th>
        <th>Attributes</th>
        <th>View Distance</th>
        <th>Sensing Distance</th>
        <th>Population</th>
        <th>Max Speed</th>
        <th>Detector</th>
        <th>Attacks</th>
    </tr>''')
    
    keys = units.keys()
    keys.sort()
    for name in keys:
        info = units[name]
        cls = GetClassByClassname(info.cls_name)
        
        attacks = list(info.attacks)
        for w in info.weapons:
            wcls = GetClassByClassname(w)
            if not wcls:
                print('Invalid weapon %s' % (w))
                continue
            if wcls.AttackPrimary:
                attacks.append(wcls.AttackPrimary)
            if wcls.AttackSecondary:
                attacks.append(wcls.AttackSecondary)
        
        attackscontent = ''
        for a in attacks:
            if attackscontent:
                attackscontent += ', '
            attackscontent += '(%s)' % (a.GetDescription(info.accuracy))
        attacksinfo = 'Unit has an accuracy of %.2f, damage is adjusted accordingly. DPS is the damage per second of the attack. Note that in some cases this might not be entirely right (e.g hunter shoots in bursts).' % (info.accuracy)
            
        WriteRow(fp, [
            (info.name, 'Internal name, can be used with the command unit_create'),
            (info.displayname, info.description),
            (info.buildtime, 'seconds'),
            StringifyCosts(info.costs),
            info.health,
            (info.unitenergy, 'Max energy of this unit, used by abilities'),
            '%s' % (' - '.join(map(lambda a: a.name,info.attributes))),
            (info.viewdistance, 'hammer units'),
            (info.sensedistance if info.sensedistance != -1 else info.viewdistance, 'hammer units'),
            (info.population, 'Population this unit requires'),
            (GetAttribute(cls, 'maxspeed', '-'), 'hammer units per second'),
            (GetAttribute(cls, 'detector', 'False'), 'True if the unit is capable of detecting cloaked units'),
            (attackscontent, attacksinfo),
        ])
        
    fp.write('</table>\n')
    WriteEnd(fp)
    fp.close()

@concommand('generate_stats')
def CCGenerateStats(args):
    GenerateStats('stats/stats.html', dbunits)
    
def RecursiveCollectAbilities(info, done, rsabilities):
    if info in done:
        return
        
    rsabilities[info.name] = info
    done.add(info)
    
    try: abilities = info.abilities
    except AttributeError: abilities = None
    try: successorability = info.successorability
    except AttributeError: successorability = None
        
    if abilities:
        for name in abilities.values():
            RecursiveCollectAbilities(dbabilities[name], done, rsabilities)
                
    if successorability:
        RecursiveCollectAbilities(dbabilities[successorability], done, rsabilities)
        
def FilterBuildings(abilities):
    filtered = dict()
    for name, info in abilities.iteritems():
        if issubclass(info, WarsBuildingInfo):
            continue
        filtered[name] = info
    return filtered
    
def FilterUnits(abilities):
    filtered = dict()
    for name, info in abilities.iteritems():
        if issubclass(info, UnitInfo) and not issubclass(info, WarsBuildingInfo):
            continue
        filtered[name] = info
    return filtered
    
def FilterAbilities(abilities):
    filtered = dict()
    for name, info in abilities.iteritems():
        if not issubclass(info, WarsBuildingInfo) and not issubclass(info, UnitInfo):
            continue
        filtered[name] = info
    return filtered
        
def GetAbilitiesFaction(faction):
    factionabi = dict()
    faction  = dbfactions[faction]
    RecursiveCollectAbilities(dbabilities[faction.startbuilding], set(), factionabi)
    return factionabi
    
@concommand('generate_statsfaction')
def CCGenerateStatsFaction(args):
    if args.ArgC() < 2:
        print('Usage: generate_statsfaction faction')
        return
    factionabi = GetAbilitiesFaction(args[1])
    factionabi = FilterAbilities(factionabi)
    GenerateStats('stats/%s.html' % (args[1]), factionabi, title='%s Unit Statistics' % (args[1]))
    
@concommand('generate_statsfaction_unitsonly')
def CCGenerateStatsFactionUnitsOnly(args):
    if args.ArgC() < 2:
        print('Usage: generate_statsfaction_unitsonly faction')
        return
    factionabi = GetAbilitiesFaction(args[1])
    factionabi = FilterBuildings(factionabi)
    factionabi = FilterAbilities(factionabi)
    GenerateStats('stats/%s_unitsonly.html' % (args[1]), factionabi, title='%s Unit Statistics (units only)' % (args[1]))
    
@concommand('generate_statsfaction_buildingsonly')
def CCGenerateStatsFactionBuildingsOnly(args):
    if args.ArgC() < 2:
        print('Usage: generate_statsfaction_buildingsonly faction')
        return
    factionabi = GetAbilitiesFaction(args[1])
    factionabi = FilterUnits(factionabi)
    factionabi = FilterAbilities(factionabi)
    GenerateStats('stats/%s_buildingsonly.html' % (args[1]), factionabi, title='%s Unit Statistics (buildings only)' % (args[1]))
    
@concommand('generate_statsfaction_all')
def CCGenerateStatsFactionAll(args):
    engine.ClientCommand('generate_stats')
    for faction in dbfactions.itervalues():
        engine.ClientCommand('generate_statsfaction %s' % (faction.name))
        engine.ClientCommand('generate_statsfaction_unitsonly %s' % (faction.name))
        engine.ClientCommand('generate_statsfaction_buildingsonly %s' % (faction.name))
        
'''
@concommand('generate_statsarmortypes')
def CCGenerateStatsArmorTypes(args):
    filename = 'stats/armortypes.html'

    folder = os.path.dirname(filename)
    if not os.path.exists(folder):
        os.mkdir(folder)

    fp = open(filename, 'wb')
    WriteHeader(fp, 'Armor Types')
    fp.write('<table class="fancy">\n')
    
    armortypes = UnitBaseShared.damagetables.keys()
    fp.write('    <tr>\n')
    fp.write('        <th>Damage Type</th>\n')
    for armortype in armortypes:
        fp.write('        <th>%s</th>\n' % (armortype))
    fp.write('    </tr>\n')
    
    for dmgtype in [DMG_GENERIC, DMG_SLASH, DMG_BULLET, DMG_BLAST, DMG_SHOCK]:
        elements = [dmgtypes[dmgtype]]
        for armortype in armortypes:
            elements.append(UnitBaseShared.damagetables[armortype][dmgtype])
        WriteRow(fp, elements)
    
    WriteEnd(fp)
    fp.close()
'''