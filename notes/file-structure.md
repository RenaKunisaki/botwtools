# File/object Hierarchy

- FRES (Resource)
    - `_RLT` (Relocation Table)
    - `_STR` (String Table)
    - FMDL (Model)
        - FSKL (Skeleton)
            - bone
        - FVTX (Vertx Buffer)
            - buffer
            - attribute
        - FSHP (Shape)
            - LOD model
                - face
                    - vertex
        - FMAT (Material)
            - render params
            - shader params
            - source params
            - shader assignment
            - tex ref array
            - sampler
            - user data (generic data)
    - FSKA (Skeleton Animation)
    - FMAA (Material Animation)
    - FVIS (Visual Animation)
    - FSCN (Scene Animation)
    - FSHU (Shape Animation)
    - embedded file
        - BNTX (Binary Texture)
            - NX (Texture)
                - `_DIC` (Dictionary)
                - BRTI (Texture Image)
            - `_STR`
        - `TexInfo.txt`
            - a text file, usually containing only the number of textures used by this model


# Naming Conventions

- `F` apparently comes from Cafe, the WiiU OS
- File extensions:
    - `s` prefix seems to mean compressed (YAZ0)
        - ie every ".bfoo" is a YAZ0-compressed ".foo"
    - `b` prefix might mean binary?


# File Extensions

| Extension | Type | Description |
|-----------|------|-------------|
|bactorpack | SARC | |
|baiprog    | AAMP | Defines how actors interact with eachother |
|beventpack | SARC | |
|bfarc      | SARC | Font graphics |
|bfres      | FRES | Model/texture resource archive |
|blarc      | SARC | |
|blwp       | PrOD | mesh transformation data |
|bmodellist | AAMP | Model list |
|bxml       | AAMP | Binary XML file |
|byml       | BYML | Binary YAML file (magic is `BY` or `YB`) |
|esetlist   | VFXB | |
|fmc        | ?    | Used by FarModelCullMgr, so FMC probably stands for that |
|mubin      | BYML | related to maps
|stats      | SARC | related to maps
