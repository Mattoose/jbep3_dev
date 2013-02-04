from _te import *

if isclient:
    from entities import C_LocalTempEntity
    
    # Redefine ClientSideEffect to make it automatically register to the effect list by default
    ClientSideEffectInternal = ClientSideEffect
    class ClientSideEffect(ClientSideEffectInternal):
        def __init__(self, name, autoregister=True):
            super(ClientSideEffect, self).__init__(name)
            if autoregister:
                AddToClientEffectList(self)
    
    # Quad flags
    FXQUAD_BIAS_SCALE = 0x0001 # Bias the scale's interpolation function
    FXQUAD_BIAS_ALPHA = 0x0002 # Bias the alpha's interpolation function
    FXQUAD_COLOR_FADE = 0x0004 # Blend the color towards black via the alpha (overcomes additive ignoring alpha)

    # Client effects (move somewhere else?)
    from srcbase import Color
    from vmath import Vector, VectorScale, VectorNormalize, AngleMatrix, TransformAABB, VectorRotate, matrix3x4_t, VectorVectors
    from math import radians, sin, cos
    
    class FXQuad(ClientSideEffect):
        def __init__(self, material, color, scale, origin, normal, yaw=0.0, alpha=1.0, flags=0):
            super(FXQuad, self).__init__('FXQuad')
            
            self.material = material
            self.color = self.VectorToColor(color)
            self.scale = scale
            self.origin = origin
            self.normal = normal
            self.yaw = yaw
            self.alpha = alpha
            self.flags = flags

            mesh = MeshBuilder(self.material, MATERIAL_QUADS)
            
            pos = Vector()
            vRight = Vector()
            vUp = Vector()
    
            if self.flags & self.FXQUAD_COLOR_FADE:
                self.color = Color(self.color.r()*alpha, self.color.g()*alpha, self.color.b()*alpha, int(alpha*255))
            else:
                self.color = Color(self.color.r(), self.color.g(), self.color.b(), int(alpha*255))

            VectorVectors( self.normal, vRight, vUp )

            rRight = ( vRight * cos( radians( self.yaw ) ) ) - ( vUp * sin( radians( self.yaw ) ) )
            rUp = ( vRight * cos( radians( self.yaw+90.0 ) ) ) - ( vUp * sin( radians( self.yaw+90.0 ) ) )

            vRight = rRight * ( scale * 0.5 )
            vUp = rUp * ( scale * 0.5 )

            pos = self.origin + vRight - vUp
            vertex = MeshVertex()
            vertex.position = pos
            vertex.normal = self.normal
            vertex.color = self.color
            vertex.stage = 0
            vertex.s = 1.0
            vertex.t = 1.0
            mesh.AddVertex(vertex)
            
            pos = self.origin - vRight - vUp
            vertex = MeshVertex()
            vertex.position = pos
            vertex.normal = self.normal
            vertex.color = self.color
            vertex.stage = 0
            vertex.s = 0.0
            vertex.t = 1.0
            mesh.AddVertex(vertex)

            pos = self.origin - vRight + vUp
            vertex = MeshVertex()
            vertex.position = pos
            vertex.normal = self.normal
            vertex.color = self.color
            vertex.stage = 0
            vertex.s = 0.0
            vertex.t = 0.0
            mesh.AddVertex(vertex)
            
            pos = self.origin + vRight + vUp
            vertex = MeshVertex()
            vertex.position = pos
            vertex.normal = self.normal
            vertex.color = self.color
            vertex.stage = 0
            vertex.s = 1.0
            vertex.t = 0.0
            mesh.AddVertex(vertex)

            self.AddMeshBuilder(mesh)
            
        def VectorToColor(self, v):
            return Color(int(v.x*255), int(v.y*255), int(v.z*255), 255)
            
        FXQUAD_COLOR_FADE = 0x0004
            
    class FXCube(ClientSideEffect):
        """ Based on the c++ version, but not an exact copy. Can additional take an origin and angles."""
        def __init__(self, material, color, mins, maxs, origin=None, angles=None, texturex=128.0, texturey=128.0):
            super(FXCube, self).__init__('FXCube')

            self.material = material
            self.color = color
            self.texturex = texturex
            self.texturey = texturey
            
            # Rotate if needed
            self.origin = origin
            self.angles = angles

            # Create all sides
            vLightDir = Vector(-1,-2,-3)
            VectorNormalize( vLightDir )
            
            self.CreateBoxSide(1, 2, 0, mins[1], mins[2], maxs[1], maxs[2], mins[0], False,  vLightDir.x * 0.5 + 0.5)
            self.CreateBoxSide(1, 2, 0, mins[1], mins[2], maxs[1], maxs[2], maxs[0], True,  -vLightDir.x * 0.5 + 0.5)

            self.CreateBoxSide(0, 2, 1, mins[0], mins[2], maxs[0], maxs[2], mins[1], True,   vLightDir.y * 0.5 + 0.5)
            self.CreateBoxSide(0, 2, 1, mins[0], mins[2], maxs[0], maxs[2], maxs[1], False, -vLightDir.y * 0.5 + 0.5)

            self.CreateBoxSide(0, 1, 2, mins[0], mins[1], maxs[0], maxs[1], mins[2], False,  vLightDir.z * 0.5 + 0.5)
            self.CreateBoxSide(0, 1, 2, mins[0], mins[1], maxs[0], maxs[1], maxs[2], True,  -vLightDir.z * 0.5 + 0.5)
                
        def SetupVec(self, dim1, dim2, fixedDim, dim1Val, dim2Val, fixedDimVal):
            v = Vector()
            v[dim1] = dim1Val
            v[dim2] = dim2Val
            v[fixedDim] = fixedDimVal
            
            if self.angles:
                xform = matrix3x4_t()
                AngleMatrix( self.angles, xform )
                vNew = Vector()
                VectorRotate(v, xform, vNew)
                v = vNew
                
            if self.origin:
                v += self.origin
            return v
            
        def VectorToColor(self, v):
            return Color(int(v.x*255), int(v.y*255), int(v.z*255), 255)
            
        def CreateBoxSide(self,
            dim1, dim2, fixedDim, 
            minX, minY, 
            maxX, maxY, 
            fixedDimVal, 
            bFlip, 
            shade):
            v = Vector()
            color = Vector()
            VectorScale( self.color, shade, color );

            mesh = MeshBuilder(self.material, MATERIAL_TRIANGLE_STRIP)
            
            vertex1 = MeshVertex()
            vertex1.position = self.SetupVec(dim1, dim2, fixedDim, minX, maxY, fixedDimVal)
            vertex1.color = self.VectorToColor(color)
     
            vertex2 = MeshVertex()
            vertex2.position = self.SetupVec(dim1, dim2, fixedDim, maxX if bFlip else minX, maxY if bFlip else minY, fixedDimVal)
            vertex2.color = self.VectorToColor(color)

            vertex3 = MeshVertex()
            vertex3.position = self.SetupVec(dim1, dim2, fixedDim, minX if bFlip else maxX, minY if bFlip else maxY, fixedDimVal)
            vertex3.color = self.VectorToColor(color)
     
            vertex4 = MeshVertex()
            vertex4.position = self.SetupVec(dim1, dim2, fixedDim, maxX, minY, fixedDimVal)
            vertex4.color = self.VectorToColor(color)

            vertex1.s = 0.0
            vertex1.t = 0.0
            if not bFlip:
                vertex2.s = 0.0
                vertex2.t = (vertex2.position - vertex1.position).Length() / self.texturey
                vertex3.s = (vertex3.position - vertex2.position).Length() / self.texturex
                vertex3.t = 0.0
                vertex4.s = (vertex4.position - vertex1.position).Length() / self.texturex
                vertex4.t = (vertex4.position - vertex3.position).Length() / self.texturey
            else:
                vertex2.s = (vertex2.position - vertex1.position).Length() / self.texturex
                vertex2.t = 0.0
                vertex3.s = 0.0
                vertex3.t = (vertex3.position - vertex1.position).Length() / self.texturey
                vertex4.s = (vertex4.position - vertex1.position).Length() / self.texturex
                vertex4.t = (vertex4.position - vertex2.position).Length() / self.texturey
                
            mesh.AddVertex(vertex1)
            mesh.AddVertex(vertex2)
            mesh.AddVertex(vertex3)
            mesh.AddVertex(vertex4)
            
            self.AddMeshBuilder(mesh)
