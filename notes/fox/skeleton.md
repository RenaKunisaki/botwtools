FMDL 'Fox' contains 1 skeletons, 2 FVTXs, 2 FSHPs, 2 FMATs, 0 udatas, total 1634 vertices
FSKL dump from 0x00000578:
[00]  char[4]               magic: b'FSKL'
[04] uint32_t                size:   39152 (000098F0)
[08] uint32_t               size2:   39152 (000098F0)
[0C] uint32_t               unk0C:       0 (00000000)
[10] Offset64 bone_idx_group_offs:    5408 (00001520)
[18] Offset64     bone_array_offs:    1472 (000005C0)
[20] Offset64    inverse_idx_offs:    3952 (00000F70)
[28] Offset64    inverse_mtx_offs:    4016 (00000FB0)
[30] Offset64               unk30:       0 (00000000)
[38] uint32_t               flags:    4608 (00001200)
[3C] uint16_t           num_bones:      31 (    001F)
[3E] uint16_t    num_inverse_idxs:      29 (    001D)
[40] uint16_t           num_extra:       0 (    0000)
[44] uint32_t               unk44:       0 (00000000)

seems to be no more than 21 matrices, since #21 (0-based) has a NaN value in it.
Blender seems to expect the same number of matrices and joints.

bone idx group: ???
bone array: ???
inverse idx: which matrix to use for each bone?
inverse mtx: the transform matrix for each joint

there also should be some vertices defined for the skeleton,
no idea what they do or where they're stored...

what           |offset|maxsiz|comment
---------------|------|------|-------
FSKL header    |000578|000048|
bone_array     |0005C0|0009B0|31 bones
inverse_idx    |000F70|000040|64 bytes = 32 idxs (29 + padding)
inverse_mtx    |000FB0|000570|21.75 mtxs? probably 21 + padding
bone_idx_group |001520|000210|16 bytes x 31 bones + 32 byte header
FMDL and etc   |001730|0081C0|
size           |0098F0|  N/A |
but if the FMDL starts at 1730, how is the size 98F0?
unless that FMDL belongs to the skeleton?
anyway that's only the FSHP_dict, the FMDL header is at 0xD0

so 21 matrices is correct, but what tells us that?
just the fact that whatever references them never goes beyond 20?

Inverse idxs: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
can't be correlated with matrices since > 21 here.

# The actual bones
No|Name     | Parents | Rotation XYZ     | Position XYZ    |
--|---------|---------|------------------|-----------------|
 0|Root     |  1   -1 |    0     0     0 |    0     0     0|
 1|Skl_Root |  0   -1 | +1.6     0     0 |    0  +0.6  -0.1|
 2|Spine_1  |  1    0 | -1.6     0  +1.6 |    0     0     0|
 3|Spine_2  |  2    1 |    0     0     0 | +0.3     0     0|
 4|Arm_1_L  |  3    2 |    0     0  -2.0 | +0.1  -0.1  -0.1|
 5|Arm_2_L  |  4    3 |    0     0  +0.5 | +0.2     0     0|
 6|Wrist_L  |  5    4 |    0     0  +0.2 | +0.3     0     0|
 7|Toe_1_FL |  6    5 |    0     0  +1.3 | +0.1     0     0|
 8|Arm_1_R  |  3    6 |    0     0  +1.1 | +0.1  -0.1  +0.1|
 9|Arm_2_R  |  8    7 |    0     0  +0.5 | -0.2     0     0|
10|Wrist_R  |  9    8 |    0     0  +0.2 | -0.3     0     0|
11|Toe_1_FR | 10    9 |    0     0  +1.3 | -0.1     0     0|
12|Neck_1   |  3   10 |    0     0  +0.5 | +0.2  -0.0     0|
13|Head     | 12   11 |    0     0  -0.6 | +0.2     0     0|
14|Chin     | 13   12 |    0     0  -0.2 | +0.1  -0.1     0|
15|Ear_L    | 13   13 | +1.6  +0.4  +1.3 |    0  +0.1  -0.1|
16|Ear_R    | 13   14 | +1.6  +0.4  -1.9 |    0  +0.1  +0.1|
17|Eyelid_L | 13   15 | +0.3  +0.5  +0.7 | +0.1     0  -0.0|
18|Eyelid_R | 13   16 | +0.3  +0.5  -2.4 | +0.1     0     0|
19|Waist    |  1   17 | -1.6     0  -1.6 |    0     0     0|
20|Leg_1_L  | 19   18 | -3.1     0  -2.0 | +0.1  -0.0  +0.1|
21|Leg_2_L  | 20   19 |    0     0  -1.5 | +0.2     0     0|
22|Ankle_L  | 21   20 |    0     0  +1.1 | +0.2     0     0|
23|Toe_1_BL | 22   21 |    0     0  +1.3 | +0.2     0     0|
24|Leg_1_R  | 19   22 | -3.1     0  +1.1 | +0.1  -0.0  -0.1|
25|Leg_2_R  | 24   23 |    0     0  -1.5 | -0.2     0     0|
26|Ankle_R  | 25   24 |    0     0  +1.1 | -0.2     0     0|
27|Toe_1_BR | 26   25 |    0     0  +1.3 | -0.2     0     0|
28|Tail_1   | 19   26 |    0     0     0 | +0.2     0     0|
29|Tail_2   | 28   27 |    0     0     0 | +0.3     0     0|
30|Tail_3   | 29   28 |    0     0     0 | +0.3     0     0|
(parent -1 = none)
all bones have 4 parents but the last 2 are always -1 here.
all bones have a scale but all are (1,1,1) here.
all bones' rotation is XYZW but all have W=1.0 here.
parent B just increments, except the first two.
maybe parent A is the bone it's connected to, and number of joints
(and hence number of mtxs) is the number of unique values here?
guess what, there are 21 unique values...
then there should be something telling which mtx to use for each?
or does it just increment a counter?
that might explain why it doesn't need anything telling how many
mtxs there are; it would just use them in order as needed.
actually, there don't seem to be any inverse mtxs in the file
at all; these are 4x3 "smooth matrices".

logical connections:
0 -> 1 -> 2 -> 3
     1 -> 4 -> 5 -> 6 -> 7
     1 -> 8 -> 9 -> 10 -> 11
     1 -> 12 -> 13 -> 14
                13 -> 15
                13 -> 16
                13 -> 17
                13 -> 18
     1 -> 19 -> 20 -> 21 -> 22 -> 23
          19 -> 24 -> 25 -> 26 -> 27
     1 -> 28 -> 29 -> 30

[ 0] Root
    [ 1] Skl_Root
        [ 2] Spine_1
            [ 3] Spine_2
        [ 4] Arm_1_L
            [ 5] Arm_2_L
                [ 6] Wrist_L
                    [ 7] Toe_1_FL
        [ 8] Arm_1_R
            [ 9] Arm_2_R
                [10] Wrist_R
                    [11] Toe_1_FR
        [12] Neck_1
            [13] Head
                [14] Chin
                [15] Ear_L
                [16] Ear_R
                [17] Eyelid_L
                [18] Eyelid_R
        [19] Waist
            [20] Leg_1_L
                [21] Leg_2_L
                    [22] Ankle_L
                        [23] Toe_1_BL
            [24] Leg_1_R
                [25] Leg_2_R
                    [26] Ankle_R
                        [27] Toe_1_BR
        [28] Tail_1
            [29] Tail_2
                [30] Tail_3

Offset|MaxSiz|What
------|------|----
0000D0|000078|FMDL header (x1)
000148|000098|FMAA header (x1)
0001E0|000010|Embed header (x1)
0001F0|000028|FMDL dict
000218|000028|FMAA dict
000240|009C3C|Embed dict
003636|      |unkB8 - in midst of some data, so maybe not offset
009E7C|014184|String table
01E000|000300|buf_mem_pool
01E300|0002A0|RLT offset
01E5A0|------|End of file

0000D0: FMDL "Fox":
    000258: size
    000268: FVTX (x2)
    000328: FMAT (x2)
    000498: FSHP (x2)
    000578: FSKL
    001728: FSHP dict
    001760: FMAT dict
    009E7C: str_tab_end

What are we missing?
    - which geometry the skeleton is attached to
    - vertex_weights values:
        - vcount (number of influences)
        - v (joint/weight influence idxs)
    - support formats other than `triangles`

The vertex_weights tag associates the weights and joints from
the previously defined sources with the vertices in the geometry
being skinned.
Each entry in this list matches a vertex in the original geometry,
so the count here should be the same as the count in the geometry
being skinned.
Each weight/joint pair is referred to as an "influence", a vertex
can have any number of influences applied to it.
The <vcount>  value for a vertex defines the number of influences
on that vertex.
In this case every vertex has 5 influences.
The values in the <v> array are the indices of the joint and weight
that make up that influence.

<vertex_weights count="42">
    <input semantic="JOINT" source="#pCylinderShape1-skin-joints" offset="0"></input>
    <input semantic="WEIGHT" source="#pCylinderShape1-skin-weights" offset="1"></input>
    <vcount>5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
    5 5 5 5 5 5 5 5 5 5 5 5 </vcount>
    <v>0 1 1 2 2 3 3 4 4 5 0 6...

The FSKL may specify an Smooth Matrix for any Bone. It does this by creating an entry in the Inverse Index array which is the index of the bone, and in the corresponding place in the Smooth Matrix array it places a 4×3 transformation matrix which reverses the full transformation of the bone and all its parents. Smooth Matrices are optional, it is Unknown if they are ever referenced. The position of and number of elements in the Smooth Matrix array and the Smooth Index array are given in the FSKL Header.

Q28. How do I generate a rotation matrix in the X-axis?
-------------------------------------------------------

  Use the 4x4 matrix:

         |  1  0       0       0 |
     M = |  0  cos(A) -sin(A)  0 |
         |  0  sin(A)  cos(A)  0 |
         |  0  0       0       1 |


Q29. How do I generate a rotation matrix in the Y-axis?
-------------------------------------------------------

  Use the 4x4 matrix:

         |  cos(A)  0   sin(A)  0 |
     M = |  0       1   0       0 |
         | -sin(A)  0   cos(A)  0 |
         |  0       0   0       1 |


Q30. How do I generate a rotation matrix in the Z-axis?
-------------------------------------------------------

  Use the 4x4 matrix:

         |  cos(A)  -sin(A)   0   0 |
     M = |  sin(A)   cos(A)   0   0 |
         |  0        0        1   0 |
         |  0        0        0   1 |