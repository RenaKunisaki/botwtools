Map of `Animal_Fox.fres` file:

000000 FRES header, name="Animal_Fox"
    header_len: 0xC
    fmdl_cnt:   1
    fska_cnt:   0
    fmaa_cnt:   1
    fvis_cnt:   0
    fshu_cnt:   0
    fscn_cnt:   0
    embed_cnt:  1
0000D0 FMDL "Fox"
    fvtx_count:  2
    fshp_count:  2
    fmat_count:  2
    udata_count: 0
    total_vtxs:  1634 (0x662)
000148 FMAA
0001E0 Embedded file, offset=0x1E200, size=1
0001F0 FMDL Dict:
    0,
    1, -1, 1, ""
    3,  1, 0, "Fox"
000218 FMAA Dict:
    0,
    1, -1, 1, ""
    4,  1, 0, "Fox_color_ftp"
000240 Embed Dict:
    0,
    1, -1, 1, ""
    2,  1, 0, "TexInfo.txt"
000268 FMDL[0].FVTX[0] - 1504 (0x5E0) vtxs, skin_weight_influence=3 num_attrs=8 num_bufs=4
0002C8 FMDL[0].FVTX[1] - 24 (0x18) vtxs, skin_weight_influence=2 num_attrs=7 num_bufs=4
       FMDL[0].FSHP[1].FVTX[0]
000328 FMDL[0].FMAT[0] - "Mt_Body" flags=1 tex_ref_cnt=3 sampler_cnt=3
0003E0 FMDL[0].FMAT[1] - "Mt_Eye" flags=1 tex_ref_cnt=3 sampler_cnt=3
000498 FMDL[0].FSHP[0] - "Model__Mt_Body", flags=2 idx=0 skin_bone_idx_cnt=29 vtx_skin_cnt=3 lod_cnt=2
000508 FMDL[0].FSHP[1] - "Model__Mt_Eye", flags=6 idx=1 skin_bone_idx_cnt=1 vtx_skin_cnt=2 lod_cnt=2
000578 FMDL[0].FSKL[0]: "Fox", 31 bones, 29 inverse idxs
    0005C0 bone_array_offs
    000F70 inverse_idx_offs
         2,  3,  4,  5,  6,  7,  8,  9,
        10, 11, 12, 13, 14, 15, 16, 17,
        18, 19, 20, 21, 22, 23, 24, 25,
        26, 27, 28, 29, 30
    000FB0 inverse_mtx_offs - space for 21 mtxs plus some padding.
    001200 flags (probably not an offset)
        note the FSHP[1] visibility_groups are 0 and 0x12...
    001520 bone_idx_group_offs
001728 FMDL[0].FSHP_dict
    0: 2, -1,  1, ``
    1: 0,  2,  0, `Model__Mt_Body`
    2: 2,  2,  1, `Model__Mt_Eye`
001760 FMDL[0].FMAT_dict
    0: 2, -1,  1, ``
    1: 0,  2,  0, `Mt_Body`
    2: 2,  2,  1, `Mt_Eye`
001798 FMDL[0].FSHP[0]
    001798 LOD[0]
        idx_cnt=3348 (0xD14)
        type=1 fmt=3 unk34=1
    0017D0 LOD[1]
        idx_cnt=816 (0x330)
        type=1 fmt=3 unk34=1
        visibility_group=1097 (0x449)
    001808 fskl_idx_array_offs
         2,  3,  4,  5,  6,  7,  8,  9,
        10, 11, 12, 13, 14, 15, 16, 17,
        18, 19, 20, 21, 22, 23, 24, 25,
        26, 27, 28, 29, 30
    001848 bbox_offset - some floats/doubles
    0018A8 bradius_offset - one double/two floats
    0018B0 LOD[0]
        0018B0 submesh_array_offs: 00 00 00 00  14 0d 00 00
        0018B8 unk10 - all zeros
        001900 idx_buf_offs: 28 1a 00 00...
    001930 LOD[1]
        001930 submesh_array_offs: 00 00 00 00  30 03 00 00
        001938 unk10 - all zeros
        001980 face_offs: 60 06 00 00...
0019B0 FMDL[0].FSHP[1]
    0019B0 LOD[0] - idx_cnt=24 (0x18) type=1 fmt=3 unk34=1
    0019E8 LOD[1] - idx_cnt=24 (0x18) type=1 fmt=3 unk34=1 visibility_group=12 (0xC)
    001A20 fskl_idx_array_offs: 0d 00 00 00  00 00 00 00
    001A28 LOD[1].face_offs, bbox_offset
    001A88 bradius_offset
    001B10 LOD[1].submesh_array_offs: 00 00 00 00  18 00 00 00
    001B18 LOD[1].unk10 - all zeros
    001B60 LOD[1].idx_buf_offs: 30 00 00 00...
001B90 FMDL[0].FVTX[0]
    001B90 vtx_attrib_array_offs
    001C10 unk18 - all zeros
    001D30 vtx_bufsize_offs
        1D30 00 2f 00 00...
        1D40 00 00 00 00...
        1D50 00 5e 00 00...
        1D60 80 17 00 00...
    001D70 vtx_stridesize_offs
        1D70 08 00 00 00...
        1D80 00 00 00 00...
        1D90 10 00 00 00...
        1DA0 04 00 00 00...
        1DB0 00 00 00 00...
        1DC0 00 00 00 00...
    001DD0 unk20 - all zeros
    001DF0 vtx_attrib_dict_offs, unk00 = 0
        0: -1,  6,  0, ``
        1:  4,  0,  5, `_p0`
        2:  9,  3,  4, `_n0`
        3: 10,  1,  3, `_t0`
        4: 10,  4,  2, `_b0`
        5:  8,  2,  8, `_u0`
        6:  0,  1,  6, `_u1`
        7: 10,  7,  5, `_i0`
        8:  9,  7,  8, `_w0`
001E88 FMDL[0].FVTX[1]
    001E88 vtx_attrib_array_offs
    001EF8 unk18 - all zeros
    002018 vtx_bufsize_offs
    002058 vtx_stridesize_offs
    0020B8 unk20, LOD[1].face_offs - all zeros
    0020D8 vtx_attrib_dict_offs
        0: -1, 1, 0, ``
        1:  4, 0, 5, `_p0`
        2:  9, 3, 4, `_n0`
        3: 10, 1, 3, `_t0`
        4: 10, 4, 2, `_b0`
        5:  8, 2, 7, `_u0`
        6: 10, 6, 5, `_i0`
        7:  9, 6, 7, `_w0`
0020E8 FMDL[0].FVTX[0].vtx_buf_offs
002160 FMDL[0].FMAT[0]
    002160 render_param_offs
    002568 unk30_offs - all zeros
    002580 sampler_list_offs
    0025E0 unk40_offs - all zeros
    002748 shader_param_array_offs
    002F08 shader_param_data_offs
    003120 volatile_flag_offs
    003128 sampler_slot_offs
    003140 tex_slot_offs
    003158 tex_ref_array_offs
    003170 shader_assign_offs
        vtx attrs: `_p0`, `_n0`, `_t0`, `_w0`, `_i0`, `_u0`, `_u1`
        tex attrs: `_a0`, `_s0`, `_n0`
    003F90 mat_params: (407 items)
        0: -1,  1,   0, ``
        1:  0,  3,   6, `uking_enable_hide_normal_pass`
        2:  2, 17, 108, `uking_reverse_polygon_offset`
        3:  1,  2,  96, `uking_edit_expand_depthshadow_far`
    005918 render_param_dict_offs
    005B40 sampler_dict_offs
        0: -1, 1, 0, ``
        1:  4, 0, 2, `_a0`
        2:  8, 2, 3, `_n0`
        3:  9, 1, 3, `_s0`
    005B88 shader_param_dict_offs (62 items)
        0: -1,  1,  0, ``
        1:  0, 18,  6, `uk_user_data`
        2:  4, 17, 21, `uk_user_data1`
005F80 FMDL[0].FMAT[1]
    005F80 render_param_offs
    0063A0 unk30_offs - all zeros
    0063B8 sampler_list_offs
    006418 unk40_offs - all zeros
    006580 shader_param_array_offs
    006D40 shader_param_data_offs
    006F58 volatile_flag_offs
    006F60 sampler_slot_offs
    006F78 tex_slot_offs
    006F90 tex_ref_array_offs
    006FA8 shader_assign_offs
    007DB0 mat_params (407 items)
        0: -1,  1,   0, ``
        1:  0,  3,   6, `uking_enable_hide_normal_pass`
        2:  2, 17, 108, `uking_reverse_polygon_offset`
        3:  1,  2,  96, `uking_edit_expand_depthshadow_far`
    009738 render_param_dict_offs (33 items)
        0: -1,  1, 0, ``
        1:  0,  8, 3, `gsys_pass`
        2:  2, 23, 4, `gsys_dynamic_depth_shadow`
        3:  1, 15, 2, `gsys_dynamic_depth_shadow_only`
0098F0 FMDL[0].FSKL[0].size
009960 FMDL[0].FMAT[1].sampler_dict_offs (3 items)
    0: -1, 1, 0, ``
    1:  4, 0, 2, `_a0`
    2:  8, 2, 3, `_n0`
    3:  9, 1, 3, `_s0`
0099A8 FMDL[0].FMAT[1].shader_param_dict_offs (62 items)
    0: -1,  1,  0, ``
    1:  0, 18,  6, `uk_user_data`
    2:  4, 17, 21, `uk_user_data1`
    3:  3,  2,  4, `uking_wind_vtx_transform_intensity`
009DA0 FMAA[0]
    009DA0 field28 - FF FF 00 00  00 00 00 00
    009DA8 field30 - material names
    009DE8 field58 - FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF
    009DF8 field38 - zeros
    009E08 field40 - texture names
009E68 FSKL offset + size ---------------------------------------
009E68 String table, size=0x14498, 602 strings
009E7C String table first entry ("")
00D4A0 String table end, even though the size disagrees...
00F468 FMDL[0].FVTX[1].vtx_buf_offs
01E000 buf_mem_pool
       FMDL[0].FVTX[0,1].unk10
       FMDL[0].FSHP[1].LOD[1].unk08
01E200 Embed[0]: "7", padding until 1E300
01E300 RLT, end of string table, according to its size
    0x1E300 (the offset of the RLT itself...)
    should probably figure out what this is.
01E5A0 End of file
