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

# bone idx group data:
1520  00 00 00 00  1f 00 00 00  ff ff ff ff  03 00 00 00  
1530  7c 9e 00 00  00 00 00 00  02 00 00 00  00 00 05 00  
1540  da ab 00 00  00 00 00 00  20 00 00 00  01 00 02 00  
1550  e2 ab 00 00  00 00 00 00  00 00 00 00  04 00 1f 00  
1560  1e c2 00 00  00 00 00 00  01 00 00 00  01 00 0f 00  
1570  8a b9 00 00  00 00 00 00  03 00 00 00  0e 00 08 00  
1580  38 ac 00 00  00 00 00 00  10 00 00 00  07 00 17 00

as int16:
0,      0, 31, 0, -1, -1,  3,  0  some header? 31=#bones
0x9E7C, 0,  0, 0,  2,  0,  0,  5  name is ""
0xABDA, 0,  0, 0, 32,  0,  1,  2  first is name offset "Root"
0xABE2, 0,  0, 0,  0,  0,  4, 31  "Skl_Root"
0xC21E, 0,  0, 0,  1,  0,  1, 15  "Spine_1"
0xB98A, 0,  0, 0,  3,  0, 14,  8  "Spine_2"
0xAC38, 0,  0, 0, 16,  0,  7, 23  "Arm_1_L"
this is just a dict.

guessed format:
u32 name_offset
s32 unk_04 ;padding?
s32 unk_08 ;observed: 0 to 33
s16 unk_0A ;observed: 0 to 30
s16 unk_0C ;observed: 0 to 31
0A/0C don't seem to be bone idxs, the relations make no sense.

ix| 04 | 08 | 08 bin   | 0A | 0C |S|#| Name
--|----|----|----------|----|----|-|-|----
-1| 31 | -1 | 11 11 11 |  3 |  0 | | | <null>
 0|  0 |  2 | .. .. 1. |  0 |  5 | | | <empty>
 1|  0 | 32 | 1. .. .. |  1 |  2 | | | Root
 2|  0 |  0 | .. .. .. |  4 | 31 | | | Skl_Root
 3|  0 |  1 | .. .. .1 |  1 | 15 | |1| Spine_1
 4|  0 |  3 | .. .. 11 | 14 |  8 | |2| Spine_2
 5|  0 | 16 | .1 .. .. |  7 | 23 |L|1| Arm_1_L
 6|  0 | 17 | .1 .. .1 | 18 | 16 |L|2| Arm_2_L
 7|  0 |  8 | .. 1. .. | 24 |  6 |L| | Wrist_L
 8|  0 |  5 | .. .1 .1 | 12 | 30 |L|1| Toe_1_FL
 9|  0 | 16 | .1 .. .. | 11 | 27 |R|1| Arm_1_R
10|  0 | 17 | .1 .. .1 | 19 | 17 |R|2| Arm_2_R
11|  0 |  8 | .. 1. .. | 28 | 10 |R| | Wrist_R
12|  0 | 17 | .1 .. .1 |  3 | 13 |R|1| Toe_1_FR
13|  0 |  4 | .. .1 .. | 14 | 20 | |1| Neck_1
14|  0 |  2 | .. .. 1. |  9 | 15 | | | Head
15|  0 | 22 | .1 .1 1. | 22 | 16 | | | Chin
16|  0 | 22 | .1 .1 1. | 26 | 17 |L| | Ear_L
17|  0 | 20 | .1 .1 .. | 18 |  7 |R| | Ear_R
18|  0 | 20 | .1 .1 .. | 19 | 11 |L| | Eyelid_L
19|  0 | 10 | .. 1. 1. | 20 |  2 |R| | Eyelid_R
20|  0 | 33 | 1. .. .1 |  5 | 21 | | | Waist
21|  0 | 33 | 1. .. .1 |  6 | 22 |L|1| Leg_1_L
22|  0 | 18 | .1 .. 1. | 21 | 23 |L|2| Leg_2_L
23|  0 | 10 | .. 1. 1. | 24 |  8 |L| | Ankle_L
24|  0 | 33 | 1. .. .1 |  9 | 25 |L|1| Toe_1_BL
25|  0 | 33 | 1. .. .1 | 10 | 26 |R|1| Leg_1_R
26|  0 | 18 | .1 .. 1. | 25 | 27 |R|2| Leg_2_R
27|  0 | 10 | .. 1. 1. | 28 | 12 |R| | Ankle_R
28|  0 | 16 | .1 .. .. | 29 | 13 |R|1| Toe_1_BR
29|  0 | 16 | .1 .. .. | 30 |  4 | |1| Tail_1
30|  0 |  1 | .. .. .1 | 29 | 31 | |2| Tail_2
31|  0 |  0 | .. .. .. |  2 |  0 | |3| Tail_3

of the 3 groups in '08 bin' every bone has a max of one bit
set in each group, except Spine_2.
none of the bits correspond to L/R (Arm_1_L/R are both 16)
could be 4 groups where the first is always 00

Grouped by 0A/0C:
0A | Bone 0   | Bone 1   || 0C | Bone 0   | Bone 1   |Binary
---|----------|----------||----|----------|----------|------
 0 |          |          ||  0 | Tail_3   |          |......
 1 | Root     | Spine_1  ||  1 |          |          |.....1
 2 | Tail_3   |          ||  2 | Root     | Eyelid_R |....1.
 3 | Toe_1_FR |          ||  3 |          |          |....11
 4 | Skl_Root |          ||  4 | Tail_1   |          |...1..
 5 | Waist    |          ||  5 |          |          |...1.1
 6 | Leg_1_L  |          ||  6 | Wrist_L  |          |...11.
 7 | Arm_1_L  |          ||  7 | Ear_R    |          |...111
 8 |          |          ||  8 | Spine_2  | Ankle_L  |..1...
 9 | Head     | Toe_1_BL ||  9 |          |          |..1..1
10 | Leg_1_R  |          || 10 | Wrist_R  |          |..1.1.
11 | Arm_1_R  |          || 11 | Eyelid_L |          |..1.11
12 | Toe_1_FL |          || 12 | Ankle_R  |          |..11..
13 |          |          || 13 | Toe_1_FR | Toe_1_BR |..11.1
14 | Spine_2  | Neck_1   || 14 |          |          |..111.
15 |          |          || 15 | Spine_1  | Head     |..1111

16 |          |          || 16 | Arm_2_L  | Chin     |.1....
17 |          |          || 17 | Arm_2_R  | Ear_L    |.1...1
18 | Arm_2_L  | Ear_R    || 18 |          |          |.1..1.
19 | Arm_2_R  | Eyelid_L || 19 |          |          |.1..11
20 | Eyelid_R |          || 20 | Neck_1   |          |.1.1..
21 | Leg_2_L  |          || 21 | Waist    |          |.1.1.1
22 | Chin     |          || 22 | Leg_1_L  |          |.1.11.
23 |          |          || 23 | Arm_1_L  | Leg_2_L  |.1.111
24 | Wrist_L  | Ankle_L  || 24 |          |          |.11...
25 | Leg_2_R  |          || 25 | Toe_1_BL |          |.11..1
26 | Ear_L    |          || 26 | Leg_1_R  |          |.11.1.
27 |          |          || 27 | Arm_1_R  | Leg_2_R  |.11.11
28 | Wrist_R  | Ankle_R  || 28 |          |          |.111..
29 | Toe_1_BR | Tail_2   || 29 |          |          |.111.1
30 | Tail_1   |          || 30 | Toe_1_FL |          |.1111.
31 |          |          || 31 | Skl_Root | Tail_2   |.11111
- none of these rows are empty
- no bone has 0A == 0C
- neither 0A or 0C have more than 2 bones per value

Grouped by 08:
08 | 08 bin | bone 0   | bone 1   | bone 2   | bone 3
---|--------|----------|----------|----------|--------
 0 |.. .. ..| Skl_Root | Tail_3   |          |
 1 |.. .. .1| Spine_1  | Tail_2   |          |
 2 |.. .. 1.| Head     |          |          |
 3 |.. .. 11| Spine_2  |          |          |
 4 |.. .1 ..| Neck_1   |          |          |
 5 |.. .1 .1| Toe_1_FL |          |          |
 8 |.. 1. ..| Wrist_L  | Wrist_R  |          |
10 |.. 1. 1.| Eyelid_R | Ankle_L  | Ankle_R  |
16 |.1 .. ..| Arm_1_L  | Arm_1_R  | Toe_1_BR | Tail_1
17 |.1 .. .1| Arm_2_L  | Arm_2_R  | Toe_1_FR |
18 |.1 .. 1.| Leg_2_L  | Leg_2_R  |          |
20 |.1 .1 ..| Ear_R    | Eyelid_L |          |
22 |.1 .1 1.| Chin     | Ear_L    |          |
32 |1. .. ..| Root     |          |          |
33 |1. .. .1| Waist    | Leg_1_L  | Toe_1_BL | Leg_1_R

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
    - how to know the number of inverse mtxs in the file
    - support formats other than `triangles`
Blender seems to expect one inverse mtx for each joint,
but there are only 21 mtxs.
So there must be 21 joints...

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
