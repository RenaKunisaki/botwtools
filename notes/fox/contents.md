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
