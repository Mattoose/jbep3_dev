from srcbase import *
from vmath import *
from entities import entity, CBaseAnimating, DENSITY_GAUSSIAN
from utils import *

@entity('ent_dota_tree')
class DotaTree(CBaseAnimating):
    def Precache(self):
        self.PrecacheModel(self.GetModelName())
        
    def Spawn(self):
        self.Precache()
        super(DotaTree, self).Spawn()
        self.SetModel(self.GetModelName())
        self.SetSolid(SOLID_BBOX)
        UTIL_SetSize(self, -Vector(16, 16, 0), Vector(16, 16, 150))
        self.SetDensityMapType(DENSITY_GAUSSIAN)