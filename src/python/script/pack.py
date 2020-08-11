# -*- coding: utf-8 -*-

import os, sys

_pjoin = os.path.join

ROOT     = _pjoin('..', '..')
EASYDB   = _pjoin(ROOT, 'bin', 'easydb_cl.exe')
LUA      = _pjoin(ROOT, 'tools', 'lua', 'lua.exe')


LOD    = '0'
SCALE  = '1'

NAME = 'worldmap'

TMP_DIR = '..\_tmp_pack3'
TEXPACK_DATA_DIR = 'texpack_data'



def _run_cmd(cmd):
    print cmd
    os.system(cmd)

def _run_cmdv(*args):
    _run_cmd(' '.join(args))

def data_dir(*args):
    return _pjoin('..', 'data', *args)

def output_dir(*args):
    return _pjoin('..', 'output', *args)

WORK_ITEMS = [
    {
        'pkg_dir': '..',
        'origin_dir': data_dir('editor_data'),
        'cfg_file': data_dir(TMP_DIR, 'editor_data\\config.json'),        
        # trim
        'src_dir': data_dir(TMP_DIR, 'editor_data'),
        'tmp_dir': data_dir(TMP_DIR),
        # pack texture
        'tp_compress': data_dir(TMP_DIR, 'editor_data', 'compress.tmp'),
        'tp_no_compress': data_dir(TMP_DIR, 'editor_data', 'no_compress.tmp'),
        'tp_src': data_dir(TMP_DIR, 'image'),
        'tp_dst': data_dir(TMP_DIR, 'tp', NAME),
        # pack ep
        'json_dir': data_dir(TMP_DIR, 'editor_data'),
        'tp_json': data_dir(TEXPACK_DATA_DIR, NAME),
        'tp_dir': data_dir(TMP_DIR, 'image'),
        'output_file': output_dir('ios', NAME),
        'output_uiifle': output_dir('ios', "worldmap.json"),
        'outdir': output_dir("ios"),
        'meta_worldmap': output_dir("ios"),
        'output_type': 'all',
        # id
        'platform_pc': 'pc',
        'platform_ios': 'ios',
        'platform_android': 'android',
        'pkg_id_file': _pjoin('..', '..', 'id', 'pkg_cfg.json'),
    },
]

if len(sys.argv) != 2:
    print "usage: %s options" % os.path.basename(sys.argv[0])
    print ""
    print " options: 0 - clear"
    print "          1 - copy editor_data"
    print "          2 - pack texture"
    print "          3 - pack ep"
    exit(0)
else:
    options = sys.argv[1]


for entry in WORK_ITEMS:
    if "0" in options:
        # clear dir
        _run_cmdv(
            "rd /s /q",
            entry["tmp_dir"]
        )
        _run_cmdv(
            "rd /s /q",
            output_dir(".")
        )        
        _run_cmdv(
            "rd /s /q",
            data_dir(TEXPACK_DATA_DIR),
        )

    if "1" in options:
        # copy editor_data
        _run_cmdv(
            "rd /s /q",
            entry["src_dir"],
        )

        _run_cmdv(
            "mkdir",
            entry["src_dir"]
        )

        _run_cmdv(
            "xcopy /s /e /q",
            entry["origin_dir"],
            entry["src_dir"]
        )

        _run_cmdv(
            "mkdir",
            data_dir(TEXPACK_DATA_DIR)
        )
        _run_cmdv(
            "mkdir",
            output_dir('ios')
        )

    if "2" in options:
        # trim
        _run_cmdv(
            EASYDB,
            'rect-cut-with-json',
            entry["src_dir"],
            entry["tmp_dir"],
            entry["cfg_file"],
        )

        # pack texture
        packtex_params = """
        {
            ""src"" : ""%s"",
            ""dst"" : ""%s"",
            ""packages"" :
            [
                {
                    ""src"" : ""%s"",
                    ""format"" : ""png"",
                    ""size_min"" : 128,
                    ""size_max"" : 1024,
                    ""extrude_min"" : 1,
                    ""extrude_max"" : 1
                },
                {
                    ""src"" : ""%s"",
                    ""format"" : ""etc2"",
                    ""quality"" : ""fastest"",
                    ""size_min"" : 128,
                    ""size_max"" : 2048,
                    ""extrude_min"" : 1,
                    ""extrude_max"" : 1
                }
            ],
        }
        """
        packtex_params = "\"" + packtex_params % (entry["tp_src"], entry["tp_dst"], entry["tp_no_compress"], entry["tp_compress"]) + "\""
        packtex_params = packtex_params.replace('\n','')
        packtex_params = packtex_params.replace('\t','')
        packtex_params = packtex_params.replace('\\','\\\\')
        # packtex_params = packtex_params.replace(' ','')
        _run_cmdv(
            EASYDB,
            'pack-tex',
            packtex_params,
        )

        # clear texpack
        _run_cmdv(
            "del /f /s /q",
            data_dir(TEXPACK_DATA_DIR)
        )

        # copy to texpack_data
        _run_cmdv(
            'xcopy /s /e /q',
            data_dir(TMP_DIR, 'tp'),
            data_dir(TEXPACK_DATA_DIR)
        )


    if "3" in options:
        pkg_dir_abs = os.path.abspath(entry["pkg_dir"]).lower()
        print(pkg_dir_abs)

        # pack ep
        _run_cmdv(
            EASYDB,
            'pack-ep-new',
            entry["json_dir"],
            entry["tp_json"],
            entry["tp_dir"],
            entry["output_file"],
            entry["output_type"],
            LOD,
            SCALE,
            'null',
            entry["platform_pc"],
            entry["pkg_id_file"],
            entry["pkg_dir"]
        )
        
    # if "4" in options: 
    #     # gen layout
    #     _run_cmdv(
    #         LUA,
    #         "gen_layout.lua",
    #         entry["meta_worldmap"]
    #     )
