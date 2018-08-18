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
