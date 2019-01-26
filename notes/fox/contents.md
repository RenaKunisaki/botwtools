Examining `Animal_Fox` because it's probably fairly simple and it's one of the first actors alphabetically.

Files:
 - romfs/Actor/Pack/Animal_Fox_A.sbactorpack
 - romfs/Actor/Pack/Animal_Fox_B.sbactorpack
 - romfs/Model/Animal_Fox_Animation.sbfres
 - romfs/Model/Animal_Fox.sbfres
 - romfs/Model/Animal_Fox.Tex.sbfres

# sbactorpack

A SARC archive containing lots of params, all in an Actor dir:
```
Actor
├── [  34]  ActorLink
│   └── [ 580]  Animal_Fox_A.bxml
├── [  22]  AIProgram
│   └── [ 14K]  Fox.baiprog
├── [  44]  AnimationInfo
│   └── [ 224]  Animal_Fox_A.baniminfo
├── [1000]  AS
│   ├── [1.2K]  Animal_Boar_Attack_Gear_1.bas
│   ├── [ 168]  Animal_Boar_Damage.bas
│   ├── [ 952]  Animal_Boar_Escape_Gear_1.bas
│   ├── [ 960]  Animal_Boar_Escape_Gear_2.bas
│   ├── [ 140]  Animal_Boar_Free_Fall.bas
│   ├── [ 920]  Animal_Boar_Hearing.bas
│   ├── [ 176]  Animal_Boar_Hearing_End.bas
│   ├── [ 836]  Animal_Boar_Look.bas
│   ├── [1008]  Animal_Boar_Move_Gear_1.bas
│   ├── [ 952]  Animal_Boar_Move_Gear_2.bas
│   ├── [ 960]  Animal_Boar_Move_Gear_3.bas
│   ├── [ 960]  Animal_Boar_Move_Gear_4.bas
│   ├── [ 596]  Animal_Boar_Notice_Turn.bas
│   ├── [ 208]  Animal_Boar_Search.bas
│   ├── [ 568]  Animal_Boar_Turn_Attack.bas
│   ├── [ 452]  Animal_Boar_Turn_Escape.bas
│   ├── [ 124]  Animal_Fox_A_Dead.bas
│   ├── [ 704]  Animal_Fox_A_Eat.bas
│   ├── [ 124]  Animal_Fox_A_Notice.bas
│   └── [4.3K]  Animal_Fox_A_Wait.bas
├── [  40]  ASList
│   └── [3.0K]  Animal_Fox_A.baslist
├── [  42]  AttClient
│   └── [ 428]  Hunting_AutoAim.batcl
├── [  48]  AttClientList
│   └── [ 200]  Hunting_Ground.batcllist
├── [  46]  Awareness
│   └── [ 612]  Animal_Fox_A.bawareness
├── [  44]  BoneControl
│   └── [ 656]  Animal_Fox_A.bbonectrl
├── [  48]  Chemical
│   └── [ 212]  Animal_Default.bchemical
├── [  46]  DamageParam
│   └── [1.5K]  AnimalDefault.bdmgparam
├── [  36]  DropTable
│   └── [ 384]  Animal_Small.bdrop
├── [  48]  GeneralParamList
│   └── [1.2K]  Animal_Fox_A.bgparamlist
├── [  46]  ModelList
│   └── [ 660]  Animal_Fox_A.bmodellist
└── [  42]  Physics
 └── [1.2K]  Animal_Fox_A.bphysics
```

In the `.bmodellist` file is a node `unknown_050C1373/Base/Folder` with value `Animal_Fox`, which most likely is how it locates the model `Model/Animal_Fox.sbfres`.
The `Animal_Fox.Tex.sbfres` is derived from the filename in the model sbfres.
Presumably `Animal_Fox_Animation` is either named in one of these files or is inferred from the name just like the texture.

Map of `Animal_Fox.bfres`:
Offset| Size |Description
------|------|-----------
000000|0000D0|FRES header
0000D0|      |FMDL 1 of 1
000148|      |FMAA 1 of 1
0001E0|000010|Embedded file table
0001F0|      |FMDL Dict
000218|      |FMAA Dict
000240|      |Embedded file Dict
001B90|      |FVTX 0 Attrib Array
001C10|      |FVTX 0 Unk14
001D30|      |FVTX 0 Buffer Sizes
001DD0|      |FVTX 0 Unk18
001DF0|      |FVTX 0 Attrib Dict
001E88|      |FVTX 1 Attrib Array
001EF8|      |FVTX 1 Unk14
0020B8|      |FVTX 1 Unk18
0020D8|      |FVTX 1 Attrib Dict
0020E8|      |FVTX 0 Buffer Data
009E7C|003636|String table
00D4B2|      |
0100E8|002F00|FVTX 0 Buffer 0 (p0)
012FE8|002F00|FVTX 0 Buffer 1 (i0, w0)
015EE8|005E00|FVTX 0 Buffer 2 (n0, t0, u0, u1)
01BCE8|001780|FVTX 0 Buffer 3 (b0)
01E000|      |Buffer, FVTX 0 Unk10, FVTX 1 Unk10
01E200|000001|Embedded file 1 of 1 "TexInfo.txt"
01E201|      |
01E300|      |Relocation Table
01E5A0| ---- |End of file


Object│Cnt │Offset  │DictOffs
FMDL  │0001│000000D0│000001F0
FSKA  │0000│00000000│00000000
FMAA  │0001│00000148│00000218
FVIS  │0000│00000000│00000000
FSHU  │0000│00000000│00000000
EMBED │0001│000001E0│00000240
Buffer│ ?? │0001E000│000001C0
StrTab│N/A │00009E7C│N/A     │size=0x003636 num_strs=602
RelTab│N/A │0001E300│N/A     |data=0x00E000 unk04=1E300 5 0  0 0 0 D49E  0 3D 0 0
