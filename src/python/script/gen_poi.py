# coding=utf-8

import os
import sys
import re
import argparse
import copy
from util import load_json, dump_json, filename_no_ext, TMP_COMPLEX, TMP_SPR

LAYER_POINT = 3
EDITOR_DATA = os.path.join('..', 'data', 'editor_data')
LR_FILE = '../data/daditu/json/desert.quest_lr.json'

_pnorm = os.path.normpath
_pjoin = os.path.join
_relpath = os.path.relpath
_dirname = os.path.dirname

p_vaild_json = re.compile(r'_(complex|anim)\.json')
p_pkg = re.compile(r'[^\\]*')
p_poi = re.compile('([^-]+)-(.*)')

def get_pkg_name(filepath):
    dirpath = _pnorm(_dirname(filepath))
    relpath = _relpath(dirpath, EDITOR_DATA)
    m = p_pkg.match(relpath)
    return 'worldmap/' + m.group(0)

def gen_point(spr, poi_list, base_dir='.', dst_dir = '.'):
    name = spr['name']
    m = p_poi.search(name)
    if not m:
        return

    filepath = _pnorm(spr['filepath'])
    
    gen_complex = False
    filepath = os.path.normpath(os.path.join(base_dir, filepath))

    is_valid_json = p_vaild_json.search(filepath)
    if is_valid_json:
        jval = load_json(filepath)
        if 'name' in jval and jval['name'] != '':
            export = jval['name']
        else:
            name_no_ext = filename_no_ext(os.path.basename(filepath))
            export = 'map_' + name_no_ext
            jval['name'] = export
            dump_json(filepath, jval)
        
        dst_filepath = filepath
    else:
        name_no_ext = filename_no_ext(os.path.basename(filepath))
        export = 'map_' + name_no_ext
        gen_complex_name = name_no_ext + '_complex.json'
        gen_complex_path = os.path.join(dst_dir, gen_complex_name)
        dst_filepath = gen_complex_path
        gen_complex = True

    pos = spr['position']

    data = {}
    data['name'] = name
    data['export'] = export
    data['pkg'] = get_pkg_name(dst_filepath)
    data['x'] = pos['x']
    data['y'] = pos['y']
    data['scale_x'] = spr.get('x scale', 1)
    data['scale_y'] = spr.get('y scale', 1)

    poi_list[name] = data

    if gen_complex and not os.path.exists(gen_complex_path):
        spr_jval = copy.deepcopy(TMP_SPR)
        spr_jval['filepath'] = os.path.relpath(filepath, dst_dir)
        spr_jval['name'] = 'main'

        dst_jval = copy.deepcopy(TMP_COMPLEX)
        dst_jval['name'] = export
        dst_jval['sprite'].append(spr_jval)

        dump_json(gen_complex_path, dst_jval)

def gen_poi(lr_path, dst_dir, meta_dir):
    jval = load_json(lr_path)
    layer = jval['layer'][LAYER_POINT]

    poi_list = {}
    base_dir = os.path.dirname(lr_path)

    if layer.has_key('sprite') :
        for spr in layer['sprite']:
            gen_point(spr, poi_list, base_dir, dst_dir)
    
    dst_poi = os.path.join(meta_dir, 'poi.json')
    dump_json(dst_poi, poi_list, encoding='utf8')
