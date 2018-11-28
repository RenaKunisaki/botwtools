<geometry id="geometry0" name="Belt_A_Buckle__Mt_Belt_A.0">
<geometry id="geometry1" name="Belt_C_Buckle__Mt_Belt_C.0">
<geometry id="geometry2" name="Earring__Mt_Earring.0">
<geometry id="geometry3" name="Eye_L__Mt_Eyeball_L.0">
<geometry id="geometry4" name="Eye_R__Mt_Eyeball_R.0">
<geometry id="geometry5" name="Eyelashes__Mt_Eyelashes.0">
<geometry id="geometry6" name="Face__Mt_Face.0">
<geometry id="geometry7" name="Face__Mt_Head.0">
<geometry id="geometry8" name="Skin__Mt_Lower_Skin.0">
<geometry id="geometry9" name="Skin__Mt_Underwear.0">
<geometry id="geometry10" name="Skin__Mt_Upper_Skin.0">

FSKL dump:
[00]  char[4]               magic: b'FSKL'
[04] uint32_t                size:  207800 (00032BB8)
[08] uint32_t               size2:  207800 (00032BB8)
[0C] uint32_t               unk0C:       0 (00000000)
[10] Offset64 bone_idx_group_offs:   19928 (00004DD8)
[18] Offset64     bone_array_offs:    4840 (000012E8)
[20] Offset64    inverse_idx_offs:   14520 (000038B8)
[28] Offset64    inverse_mtx_offs:   14744 (00003998)
[30] Offset64               unk30:       0 (00000000)
[38] uint32_t               flags:    4608 (00001200)
[3C] uint16_t           num_bones:     121 (    0079)
[3E] uint16_t    num_inverse_idxs:     108 (    006C)
[40] uint16_t           num_extra:       3 (    0003)
[44] uint32_t               unk44:       0 (00000000)

<technique_common>
    <accessor source="#pCylinderShape1-skin-weights-array" count="211" stride="1">
        <param name="WEIGHT" type="float"></param>
    </accessor>
</technique_common>

*library_controllers*
  *controller*  id=`Renamon_Tongue-skin` name=`Renamon`
    *skin*  source=`#tongue1-mesh`
      *bind_shape_matrix*: `1 0 0 0  0 1 0 0...`

      *source*  id=`Renamon_Tongue-skin-joints`
        *Name_array*  id=`Renamon_Tongue-skin-joints-array` count=`180`
          `DEF-head DEF-finger_index_03_L ...`
        *technique_common*
          *accessor*  source=`#Renamon_Tongue-skin-joints-array` count=`180` stride=`1`
            *param*  name=`JOINT` type=`name`

      *source*  id=`Renamon_Tongue-skin-bind_poses`
        *float_array*  id=`Renamon_Tongue-skin-bind_poses-array` count=`2880`
          `1 0 0 0...`
        *technique_common*
          *accessor*
            *param*
      ...more sources...

      *joints*
        *input*  semantic=`JOINT` source=`#Renamon_Tongue-skin-joints`
        *input*  semantic=`INV_BIND_MATRIX` source=`#Renamon_Tongue-skin-bind_poses`

      *vertex_weights*  count=`392`
        *input*  semantic=`JOINT` source=`#Renamon_Tongue-skin-joints` offset=`0`
        *vcount*: `4 4 4...`
        *v*: `127 0 131 1 134 2...`

<!-- Renamon -->
<library_controllers>
  <controller id="Renamon_Tongue-skin" name="Renamon">
    <skin source="#tongue1-mesh">
      <bind_shape_matrix>1 0 0 0  0 1 0 0  0 0 1 0  0 0 0 1</bind_shape_matrix>

      <source id="Renamon_Tongue-skin-joints">
        <Name_array id="Renamon_Tongue-skin-joints-array" count="180">
          DEF-head DEF-finger_index_03_L ...
        </Name_array>
        <technique_common>
          <accessor source="#Renamon_Tongue-skin-joints-array" count="180" stride="1">
            <param name="JOINT" type="name"/>
          </accessor>
        </technique_common>
      </source>

      <source id="Renamon_Tongue-skin-bind_poses">
        <float_array id="Renamon_Tongue-skin-bind_poses-array" count="2880">
          1 0 0 0...
        </float_array>
        <technique_common>
          <accessor source="#Renamon_Tongue-skin-bind_poses-array" count="180" stride="16">
            <param name="TRANSFORM" type="float4x4"/>
          </accessor>
        </technique_common>
      </source>

      <source id="Renamon_Tongue-skin-weights">
        <float_array id="Renamon_Tongue-skin-weights-array" count="1425">
          0.4183802...
        </float_array>
        <technique_common>
          <accessor source="#Renamon_Tongue-skin-weights-array" count="1425" stride="1">
            <param name="WEIGHT" type="float"/>
          </accessor>
        </technique_common>
      </source>

      <joints>
        <input semantic="JOINT" source="#Renamon_Tongue-skin-joints"/>
        <input semantic="INV_BIND_MATRIX" source="#Renamon_Tongue-skin-bind_poses"/>
      </joints>

      <vertex_weights count="392">
        <input semantic="JOINT" source="#Renamon_Tongue-skin-joints" offset="0"/>
        <vcount>4 4 4...</vcount>
        <v>127 0 131 1 134 2...</v>
      </vertex_weights>
    </skin>
  </controller>
