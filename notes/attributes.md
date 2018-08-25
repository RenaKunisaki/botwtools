From `http://mk8.tockdom.com/wiki/FMDL_(File_Format)`

# Vertex attributes

| Name| Friendly     | Description |
|-----|--------------|-------------|
| _p0 | position0    | The position of the vertex. |
| _n0 | normal0      | The normal of the vertex used in lighting calculations. |
| _t0 | tangent0     | The tangent of the vertex used in advanced lighting calculations. |
| _b0 | binormal0    | The binormal of the vertex used in advanced lighting calculations. |
| _w0 | blendweight0 | Influence amount of the smooth skinning matrix at the index given in blendindex0. |
| _i0 | blendindex0  | Index of influencing smooth skinning matrix. |
| _u0 | uv0          | Texture coordinates used for texture mapping. |
| _u1 | uv1          | |
| _u2 | uv2          | |
| _u3 | uv3          | |
| _c0 | color0       | Vertex colours used for simple shadow mapping. |
| _c1 | color1       | |


# Texture attributes

| Name| Friendly  | Description |
|-----|-----------|-------------|
| _a0 | albedo0   | Ordinary colour textures for surface albedo. |
| _a1 | albedo1   | |
| _a2 | albedo2   | |
| _a3 | albedo3   | |
| _n0 | normal0   | Normal map texture for altering surface normals. |
| _n1 | normal1   | |
| _s0 | specular0 | Specular highlight texture. |
| _e0 | emission0 | Emissive lighting texture. |
| _b0 | bake0     | Bake textures. |
| _b1 | bake1     | |

these are probably applied to a material, and tell which textures are used for what.
