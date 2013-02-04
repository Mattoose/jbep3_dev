from srcbase import Color
from vmath import Vector, QAngle
#from gameinterface import GetMapHeader, LUMP_ENTITIES
from collections import defaultdict

#def ParseMapEntitiesToBlocks(mapname):
#    """ Read all entity blocks from a map.
#        Return both by a list of blocks as by dictionary with the classnames as keys. """
#     Read all lines
#    header = GetMapHeader(mapname)
#    f = open(mapname, 'rb')
#    f.seek(header.lumps[LUMP_ENTITIES].fileofs)    
#    lines = f.read(header.lumps[LUMP_ENTITIES].filelen)
#    lines = lines.split('\n')
#    f.close()
#    
#     Parse each block
#    assert(lines[0].startswith('{'))
#    blocks = []
#    blocksbyclass = defaultdict( list )
#    for line in lines:
#        if line == '\x00':
#            break
#         Start of a new block
#        if line.startswith('{'):
#            block = defaultdict( list )
#            classname = None
#            continue
#         End of a block
#        if line.startswith('}'):
#             Only save if the block closed
#            blocks.append(block)
#            if classname:
#                blocksbyclass[classname].append(block)
#            continue  
#         Parse field + value
#        fieldvalue = line.split(None, 1)
#        field = fieldvalue[0].replace('"', '')
#        value = fieldvalue[1].replace('"', '')
#        block[field].append(value)
#        
#         Save classname
#        if field == 'classname':
#            classname = value
#
#    return blocks, blocksbyclass
    
def StringToVector(value):   
    """ Try to convert a string to a Vector, if possible. The values must be seperated by spaces """
    v = value.split()
    if len(v) != 3:
        raise ValueError('Value is not a Vector')
    return Vector(float(v[0]), float(v[1]), float(v[2]))
    
def StringToAngle(value):
    """ Try to convert a string to a QAngle, if possible. The values must be seperated by spaces """
    v = value.split()
    if len(v) != 3:
        raise ValueError('Value is not a QAngle')
    return QAngle(float(v[0]), float(v[1]), float(v[2]))
    
def StringToColor(value):
    """ Try to convert a string to a Color, if possible. The values must be seperated by spaces """
    v = value.split()
    if len(v) == 3:
        return Color(float(v[0]), float(v[1]), float(v[2]))
    elif len(v) == 4:
        return Color(float(v[0]), float(v[1]), float(v[2]), float(v[3]))
    raise ValueError('Value is not a Color')
