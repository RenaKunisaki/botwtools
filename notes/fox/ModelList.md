`Animal_Fox_A.bmodellist` is lots of parameters:
param_root > ControllerInfo: (some values are empty)

| Param Name               | Value              | Notes |
| -------------------------|--------------------|-------|
| unknown_1AFE6DAF         | True               ||
| MulColor                 | 1.0, 1.0, 1.0, 1.0 ||
| AddColor                 | 0.0, 0.0, 0.0, 0.0 ||
| unknown_8B36C62F         |                    ||
| unknown_1BE5F0C1         | Fill               ||
| unknown_B820FD50         | MapUnitShape       ||
| unknown_9A86E2F3         |                    ||
| unknown_C6907D93         |                    ||
| unknown_BB4ECFEA         |                    ||
| BaseScale                | 1.0, 1.0, 1.0      ||
| VariationMatAnim         |                    ||
| VariationMatAnimFrame    | 0                  ||
| VariationShaderAnim      |                    ||
| VariationShaderAnimFrame | 0                  ||
| unknown_5B1D79C4         | Auto               ||
| unknown_63F44D30         | 0.0, 0.0, 0.0      ||
| unknown_1878C84E         | 0.0                ||
| unknown_D649431B         | 0.0                ||
| CalcAABBASKey            | Wait               ||

param_root > Attention: (some values are empty)
(some floats rounded, eg 0.10000000149011612)

| Param Name                | Value         | Notes |
| --------------------------|---------------|-------|
| IsEnableAttention         | True          ||
| LookAtBone                | Head          ||
| LookAtOffset              | 0.1, 0.0, 0.0 ||
| CursorOffsetY             | 0.5           ||
| AIInfoOffsetY             | 0.0           ||
| CutTargetBone             | Root          ||
| CutTargetOffset           | 0.0, 0.3, 0.2 ||
| GameCameraBone            |               ||
| GameCameraOffset          | 0.0, 0.0, 0.0 ||
| BowCameraBone             |               ||
| BowCameraOffset           | 0.0, 0.0, 0.0 ||
| AttackTargetBone          |               ||
| AttackTargetOffset        | 0.0, 0.0, 0.0 ||
| AttackTargetOffsetBack    | 0.0           ||
| AtObstacleChkOffsetBone   |               ||
| AtObstacleChkOffset       | 0.0, 0.0, 0.0 ||
| AtObstacleChkUseLookAtPos | True          ||
| CursorAIInfoBaseBone      |               ||
| CursorAIInfoBaseOffset    | 0.0, 0.0, 0.0 ||

ModelData: empty
AnmTarget: empty
unknown_050C1373:
    Base:
        Folder: Animal_Fox
        - this must be the name of the model file since the name isn't anywhere else in here or any other file I looked at
Unit:
    unknown_C5AFF8F9
        UnitName: Fox
        BindBone: empty
unknown_CBEC2E83:
    Base:
        NumASSlot: 3
        IsParticalEnable: false
        TargetType: 0
