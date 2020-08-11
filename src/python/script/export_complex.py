import os
import copy
from util import load_json, dump_json, filename_no_ext, TMP_COMPLEX, TMP_SPR

city_paths = [
    'png/paopaodao-1.png',
    'png/paopaodao-2.png',
    'png/paopaodao-3.png',
]

def gen_complex(complex_path, export, filepath):
    if os.path.exists(complex_path):
        return
        
    dst_dir = os.path.dirname(complex_path)
    spr_jval = copy.deepcopy(TMP_SPR)
    spr_jval['filepath'] = os.path.relpath(filepath, dst_dir)

    dst_jval = copy.deepcopy(TMP_COMPLEX)
    dst_jval['name'] = export
    dst_jval['sprite'].append(spr_jval)

    dump_json(complex_path, dst_jval)

def gen_activity_city(dst_dir, base_dir = None):
    for path in city_paths:
        basename = os.path.basename(path)
        name_no_ext = filename_no_ext(basename)
        complex_path = os.path.join(dst_dir, name_no_ext + '_complex.json')
        print('gen activity city dst_dir:%s, name_no_ext:%s, complex_path:%s' % (dst_dir, name_no_ext, complex_path))
        export = name_no_ext
        
        if base_dir:
            # relpath = os.path.relpath(base_dir, dst_dir)
            # print('relpath:%s, path:%s' % (relpath, path))
            # path = os.path.normpath(os.path.join(relpath, path))
            # print('final path ' + path)
            path = os.path.join(base_dir, path)
        
        gen_complex(complex_path, export, path)