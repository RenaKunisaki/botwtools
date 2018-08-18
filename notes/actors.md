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

## ActorLink

`Animal_Fox_A.bxml` describes how the actor relates to other things:
- LinkTarget:
    | Param Name       | Value           | Notes |
    | -----------------|-----------------|-------|
    | ActorNameJpn     |ヘイゲンギツネ    |"heigengitsune","Hagen Fox"|
    | Priority         |Default          ||
    | AIProgramUser    |Fox              ||
    | AIScheduleUser   |Dummy            ||
    | ASUser           |Animal_Fox_A     ||
    | AttentionUser    |Hunting_Ground   ||
    | AwarenessUser    |Animal_Fox_A     ||
    | BoneControlUser  |Animal_Fox_A     ||
    | ActorCaptureUser |Dummy            ||
    | ChemicalUser     |Animal_Default   ||
    | DamageParamUser  |AnimalDefault    ||
    | DropTableUser    |Animal_Small     ||
    | ElinkUser        |Animal_Fox_A     ||
    | GParamUser       |Animal_Fox_A     ||
    | LifeConditionUser|Dummy            ||
    | LODUser          |Dummy            ||
    | ModelUser        |Animal_Fox_A     ||
    | PhysicsUser      |Animal_Fox_A     ||
    | ProfileUser      |Prey             ||
    | RgBlendWeightUser|Dummy            ||
    | RgConfigListUser |Dummy            ||
    | RecipeUser       |Dummy            ||
    | ShopDataUser     |Dummy            ||
    | SlinkUser        |Animal_Fox_A     ||
    | UMiiUser         |Dummy            ||
    | XlinkUser        |Quadruped_Animal ||
    | AnimationInfo    |Animal_Fox_A     ||
    | ActorScale       |1.25             ||

- Tags:
    | Param Name       | Value           | Notes |
    | -----------------|-----------------|-------|
    | unknown_205B2B32 | RevivalRandom   ||
    | unknown_575C1BA4 | UnderGodForest  ||
    | unknown_CE554A1E | UseAnimalUnit   ||
    | unknown_B9527A88 | ZukanAnimal     ||

- unknown_42808CD2:
    | Param Name       | Value           | Notes |
    | -----------------|-----------------|-------|
    | unknown_205B2B32 | FitTerrain      ||

no idea what most of these params mean. `unknown` means I don't know
the actual string. (element names are stored as a CRC32)

`AIProgram/Fox.baiprog`: another AAMP file containing only a `DemoAIActionIdx` node:
| Param Name             | Value | Notes |
| -----------------------|------:|-------|
| unknown_095C9668       |   102 ||
| Demo_Idling            |   103 ||
| unknown_FDEB883F       |   104 ||
| unknown_D9991D64       |   105 ||
| unknown_A19C16B0       |   106 ||
| Demo_PlayASForTimeline |   107 ||
| unknown_FE995F57       |   108 ||
| unknown_D40F7B8C       |   109 ||
| Demo_SendSignal        |   110 ||
| unknown_8EFDF265       |   111 ||
| unknown_CCFE00D1       |   112 ||
| unknown_833AF8B4       |   113 ||
| Demo_VisibleOff        |   114 ||
| unknown_774C68D1       |   115 ||
| unknown_0EB8597D       |   116 ||
| unknown_43C4E2B4       |   117 ||


# Texture lookup:

the internal filename is used to find the textures.
if the name in the model file is `Fox` then it loads textures
from `Fox.Tex.bfres`. but there's more to it:

the texture file is `Model/%s.Tex.bfres` or `Model/%s.Tex2.bfres`
where `%s` is the internal name.
On WiiU, `Tex` is texures, `Tex2` is mipmaps.
On Switch, `Tex` is both and `Tex2` is never used.
(but there may be a flag telling it to use `Tex2` that's just never set?)
Also, the last 3 characters of the name are removed if they're `-##`
where `#` is a digit.
