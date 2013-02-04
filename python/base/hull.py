from vmath import Vector, vec3_origin

# Format for each type: mins maxs smallmins smallmaxs
hull = {
    None : (vec3_origin, vec3_origin, vec3_origin, vec3_origin),
    'HULL_HUMAN' : ( Vector(-13,-13,   0), Vector(13, 13, 72), 
                     Vector(-8,-8,   0), Vector( 8,  8, 72) ), # Combine, Stalker, Zombie...
    'HULL_SMALL_CENTERED' : ( Vector(-20,-20, -20), Vector(20, 20, 20), 
                              Vector(-12,-12,-12), Vector(12, 12, 12) ), # Scanner
    'HULL_WIDE_HUMAN' : ( Vector(-15,-15,   0), Vector(15, 15, 72), 
                          Vector(-10,-10, 0), Vector(10, 10, 72) ), # Vortigaunt
    'HULL_TINY' : ( Vector(-12,-12,   0), Vector(12, 12, 24), 
                    Vector(-12,-12, 0), Vector(12, 12, 24) ), # Headcrab
    'HULL_WIDE_SHORT' : ( Vector(-35,-35,   0), Vector(35, 35, 32), 
                          Vector(-20,-20, 0), Vector(20, 20, 32) ), # Bullsquid
    'HULL_MEDIUM' : ( Vector(-16,-16,   0), Vector(16, 16, 64), 
                      Vector(-8,-8, 0), Vector(8, 8, 64) ), # Cremator
    'HULL_TINY_CENTERED' : ( Vector(-8,	-8,  -4), Vector(8, 8,  4), 
                             Vector(-8,-8, -4), Vector( 8, 8, 4) ), # Manhack 
    'HULL_LARGE' : ( Vector(-40,-40,   0), Vector(40, 40, 100), 
                     Vector(-40,-40, 0), Vector(40, 40, 100) ), # Antlion Guard
    'HULL_LARGE_CENTERED' : ( Vector(-38,-38, -38), Vector(38, 38, 38), 
                              Vector(-30,-30,-30), Vector(30, 30, 30) ), # Mortar Synth
    'HULL_MEDIUM_TALL' : ( Vector(-18,-18,   0), Vector(18, 18, 100), 
                           Vector(-12,-12, 0), Vector(12, 12, 100) ), # Hunter
    'HULL_TINY_FLUID' : ( Vector(-8,-8,   0), Vector(8, 8, 16),
                          Vector(-8,-8, 0), Vector(8, 8, 16) ), # Blob?
    'HULL_MEDIUMBIG' : ( Vector(-20,-20,   0), Vector(20, 20, 69),
                         Vector(-20,-20, 0), Vector(20, 20, 69) ), # Drones
}

def Mins(id):
    return hull[id][0]

def Maxs(id):
    return hull[id][1]

def SmallMins(id):
    return hull[id][2]

def SmallMaxs(id):
    return hull[id][3]

def Length(id):
    return (hull[id][1].x - hull[id][0].x) 

def Width(id):
    return (hull[id][1].y - hull[id][0].y)

def Height(id):
    return (hull[id][1].z - hull[id][0].z)
