from entities import GetAllClassnames, GetClassByClassname
from gameinterface import concommand
from fields import GetAllFields

basefilecontents = '''//=============================================================================
//
// Purpose: Half-Life 2: Wars game definition file (.fgd) 
//
//=============================================================================

@include "base.fgd"

@BaseClass = Wars
[ 
	ownernumber(choices) : "Owner Number" : 0 : "Ownernumber of this entity." =
	[
		0 : "Neutral"
		1 : "Enemy"
		2 : "Player 0"
		3 : "Player 1"
		4 : "Player 2"
		5 : "Player 3"
		6 : "Player 4"
		7 : "Player 5"
		8 : "Player 6"
		9 : "Player 7"
	]
]

@BaseClass base(Targetname, Angles, RenderFields, DamageFilter, ResponseContext, Shadow, Wars) color(0 200 200) = BaseUnit
[
]

@PointClass base(Angles) = env_detail_controller : "An entity that lets you control the fade distances for detail props."
[
	fademindist(float) : "Start Fade Dist/Pixels" : 400 : "Distance at which the prop starts to fade."
	fademaxdist(float) : "End Fade Dist/Pixels" : 1200 : "Maximum distance at which the prop is visible."
]

'''

derivedfilecontents = '''//=============================================================================
//
// Purpose: Half-Life 2: Wars game definition file (.fgd) 
//
//=============================================================================

@include "hl2wars.fgd"

'''

fgdtemplate = '''%(ClassType)s %(EntityProperties)s %(EntityExtraProperties)s = %(EntityName)s :
	"%(HelpString)s" 
[%(CPPProperties)s
%(PythonProperties)s]
'''

@concommand('generate_fgd')
def CCGenFGD(args):
    gamepackages = set(args.ArgS().split())
    entities = GetAllClassnames()
    entities.sort()

    if gamepackages:
        fgdfilename = '_'.join(gamepackages) + '.fgd'
        content = derivedfilecontents
    else:
        fgdfilename = 'hl2wars.fgd'
        content = basefilecontents
    
    for clsname in entities:
        cls = GetClassByClassname(clsname)
        if not cls:
            continue
            
        if gamepackages:
            try:
                modname = cls.__module__.split('.')[0]
            except: 
                modname = ''
                
            if modname not in gamepackages:
                continue

        try:
            factoryname = 'factory__%s' % (clsname)
            factory = getattr(cls, factoryname)
        except AttributeError:
            print('generate_fgd: %s has no factory!' % (clsname))
            continue
            
        if factory.nofgdentry:
            continue
            
        # Fields/properties
        pythonproperties = ''
        fields = GetAllFields(cls)
        for field in fields:
            if not field.keyname or field.nofgd:
                continue
                
            pythonproperties += '\t%s\n'% (field.GenerateFGDProperty())
            
        # Inputs. Must check each method
        for name, attribute in cls.__dict__.iteritems():
            try:
                entry = attribute.fgdinputentry
            except AttributeError:
                continue
            pythonproperties += '\t%s\n'% (entry)
            
            
        # Entity properties
        entityproperties = ''
        if factory.fgdbase:
            entityproperties += 'base(%s) ' % (','.join(factory.fgdbase))
        if factory.fgdstudio:
            entityproperties += 'studio("%s") ' % (factory.fgdstudio)
        if factory.fgdiconsprite:
            entityproperties += 'iconsprite("%s") ' % (factory.fgdiconsprite)
        if factory.fgdcylinder:
            entityproperties += 'cylinder(%s) ' % (','.join(factory.fgdcylinder))
        if factory.fgdcolor:
            entityproperties += 'color(%s) ' % (factory.fgdcolor)
        if factory.fgdsize:
            entityproperties += 'size(%s) ' % (factory.fgdsize)
            
        entry = fgdtemplate % {
            'EntityName' : factory.entityname,
            'ClassType' : factory.clstype,
            'EntityProperties' : entityproperties,
            'EntityExtraProperties' : factory.entityextraproperties,
            'HelpString' : factory.helpstring,
            'CPPProperties' : factory.cppproperties,
            'PythonProperties' : pythonproperties,
        
        }
            
        content += entry
        content += '\n\n'
            
    fp = open(fgdfilename, 'wb')
    fp.write(content)
    fp.close()