
import os
import sys
import json
import argparse
import shutil
import math
import re
import hashlib
from dump_lr import dump_lr
from gen_player import do_gen_player
from rm_unused_png import rm_unused_png
from gen_poi import gen_poi
from gen_pkg_dir import gen_bg_dirs, clear_bg_dirs
from gen_pkg_cfg import gen_pkg_id
# from export_complex import gen_activity_city
from util import load_json, dump_json

_pjoin = os.path.join
_pnorm = os.path.normpath
_pabs = os.path.abspath

ROOT = '..'
EASYDB = _pjoin('..', '..', 'bin', 'easydb_cl.exe')
LR2PNG = _pjoin(ROOT, 'script', 'lr2png.exe')


def _run_cmd(cmd):
    print(cmd)
    return os.system(cmd)


def _run_cmdv(*args):
    return _run_cmd(' '.join(args))

PKG_NAME = 'worldmap'

TILE_DIR = _pjoin(ROOT, 'tile')
TILE_OUTPUT = _pjoin(TILE_DIR, 'img')
TILE_SIZE = 1024
TILE_SCALE = 1
WIN_WIDTH = 160
WIN_HEIGHT = 90
DASH_SIZE = 30
GAP_SIZE = 30

COMMON_DIR = _pjoin(ROOT, '..', '..', 'client', 'common')
CITY_XML = _pjoin(COMMON_DIR, 'design', 'city.xml')
LINK_INFO = _pjoin(TILE_DIR, 'link.txt')

DATA_DIR = _pjoin(ROOT, 'data')
EDITOR_DIR = _pjoin(DATA_DIR, 'editor_data')
SRC_LR_ART = _pjoin(EDITOR_DIR, 'map', 'json', 'desert_lr.json')

TMP_DIR = _pjoin(DATA_DIR, '_tmp_pack3')
TMP_MAP = _pjoin(EDITOR_DIR, 'map', '_tmp_pack')
TMP_MAP_JSON = _pjoin(TMP_MAP, 'json')
TMP_MAP_GEN = _pjoin(TMP_MAP_JSON, 'gen')
TMP_PNG = _pjoin(TMP_MAP, 'png')

TMP_LR_ART = _pjoin(TMP_MAP_JSON, 'desert_lr.json')
TMP_LR_LOGIC = _pjoin(TMP_MAP_JSON, 'desert.real_lr.json')
TMP_LR_POINT = _pjoin(TMP_MAP_JSON, 'desert.quest_lr.json')

PKG_CITY_DIR = _pjoin(EDITOR_DIR, 'city')
PKG_MAP_DIR = _pjoin(EDITOR_DIR, 'map')

TP_DIR = _pjoin(ROOT, 'tp')
TP_OUT = _pjoin(TP_DIR, PKG_NAME)

EP_DIR = _pjoin(ROOT, 'ep')
PKG_DIR = _pjoin(ROOT, 'pkg')
# EP_OUT = _pjoin(EP_DIR, PKG_NAME)
TMP_META = _pjoin(ROOT, 'meta')

dirs_custom = None
# dirs_custom = [ 'map', 'city', 'zhangyu']
# dirs_custom = [ v for v in os.listdir(EDITOR_DIR) if os.path.isdir(_pjoin(EDITOR_DIR, v)) and not v.startswith('bg_') ]

MD5_RECORD_FILE = _pjoin(EDITOR_DIR, 'md5.json')
if os.path.exists(MD5_RECORD_FILE):
    MD5_RECORD = load_json(MD5_RECORD_FILE)
else:
    MD5_RECORD = {}

EP_CFG = [
    {
        'platform': 'pc',
        'png_format': 'png',
        'ep_dir': _pjoin(EP_DIR, 'pc'),
        'pkg_dir': _pjoin(PKG_DIR, 'pc'),
        'tp_dir': _pjoin(TP_DIR, 'png')
    },
    {
        'platform': 'android',
        'png_format': 'etc2',
        'quality': 'fastest',
        'ep_dir': _pjoin(EP_DIR, 'android'),
        'pkg_dir': _pjoin(PKG_DIR, 'android'),
        'tp_dir': _pjoin(TP_DIR, 'etc2')
    }
]


def save_md5():
    dump_json(MD5_RECORD_FILE, MD5_RECORD)


def calc_md5(src):
    md5 = hashlib.md5()

    if os.path.isdir(src):
        for root, _, files in os.walk(src):
            for filepath in files:
                path = _pjoin(root, filepath)
                # print('check file md5: ' + path)
                f = open(path, 'rb')
                s = f.read()
                f.close()
                md5.update(s)
    elif os.path.isfile(src):
        f = open(src, 'rb')
        s = f.read()
        f.close()
        md5.update(s)
    else:
        md5.update(src)

    return md5.hexdigest()

def calc_png_and_json_md5(src):
    md5 = hashlib.md5()

    items = [ 'png', 'json', 'config.json' ]

    for item in items:
        item_path = _pjoin(src, item)
        if os.path.isdir(item_path):
            for root, _, files in os.walk(item_path):
                for filepath in files:
                    path = _pjoin(root, filepath)
                    # print('check file md5: ' + path)
                    f = open(path, 'rb')
                    s = f.read()
                    f.close()
                    md5.update(s)
        elif os.path.isfile(item_path):
            # print('check file md5: ' + item_path)
            f = open(item_path, 'rb')
            s = f.read()
            f.close()
            md5.update(s)
        else:
            md5.update(item_path)
    
    v = md5.hexdigest()
    print('calc md5: ' + src + ', ' + v)

    return v

def get_md5(key):
    if key in MD5_RECORD:
        info = MD5_RECORD[key]
        return info['md5']
    
    return ''

def record_md5(key, md5):
    if key in MD5_RECORD:
        info = MD5_RECORD[key]
    else:
        info = {}
        MD5_RECORD[key] = info
    
    info['md5'] = md5
    print('record ' + key + ', md5: ' + md5)

def update_dep(key, dep):
    info = MD5_RECORD[key]
    info['dep'] = dep
    info['dep_md5'] = get_md5(dep)

def check_dep(key):
    if not key in MD5_RECORD:
        print('check dep: no key ' + key)
        return False

    info = MD5_RECORD[key]

    if not 'dep' in info:
        return True

    if not 'dep_md5' in info:
        return False
    
    cur_dep_md5 = info['dep_md5']
    dep = info['dep']
    dep_md5 = get_md5(dep)

    ret = cur_dep_md5 == dep_md5

    print('check dep: ' + key + ', ' + dep + ', ' + dep_md5 + ', ret = ' + str(ret))

    return ret

def check_md5(key, only_png_and_json = True):
    md5 = get_md5(key)
    if md5 == '':
        return False
    
    if only_png_and_json:
        cur_md5 = calc_png_and_json_md5(key)
    else:
        cur_md5 = calc_md5(key)

    ret = md5 == cur_md5
    print('check md5 ' + key + ', md5: ' + md5 + ', cur_md5: ' + cur_md5)
    return ret

def rm_dir_aux(path):
    if os.path.exists(path):
        print('remove dir: ' + path)
        shutil.rmtree(path)


def mk_dir_aux(path):
    if not os.path.exists(path):
        print('make dir: ' + path)
        os.makedirs(path)


def clear_tmp(dirs):
    # rm_dir_aux(TMP_DIR)
    for dirname in dirs:
        dirpath = _pjoin(EDITOR_DIR, dirname, '_tmp_pack')
        rm_dir_aux(dirpath)
    # rm_dir_aux(EP_DIR)


def do_copy_tmp(dirname):
    dirpath = _pjoin(EDITOR_DIR, dirname)
    if not os.path.isdir(dirpath):
        return

    png_dir = _pjoin(dirpath, 'png')
    json_dir = _pjoin(dirpath, 'json')
    config_path = _pjoin(dirpath, 'config.json')

    tmp_dir = _pjoin(dirpath, '_tmp_pack')
    tmp_png_dir = _pjoin(tmp_dir, 'png')
    tmp_json_dir = _pjoin(tmp_dir, 'json')
    tmp_config_path = _pjoin(tmp_dir, 'config.json')

    shutil.copytree(png_dir, tmp_png_dir)
    shutil.copytree(json_dir, tmp_json_dir)

    if os.path.exists(config_path):
        shutil.copyfile(config_path, tmp_config_path)


def copy_tmp(dirs):
    for dirname in dirs:
        do_copy_tmp(dirname)


def copy_bg_tmp(name):
    pattern_str = '^%s_[0-9]+$' % name
    pattern = re.compile(pattern_str)
    for dirname in os.listdir(EDITOR_DIR):
        if pattern.search(dirname):
            do_copy_tmp(dirname)


def pack_tex(src_dir, dst_dir, side_min=0, side_max=1024, extrude_min=1, extrude_max=1, png_format='png', quality='', trim=True):
    packtex_params = {
        "src": src_dir,
        "dst": dst_dir,
        "packages":
        [
            {
                "src": src_dir,
                "format": png_format,
                "size_min": side_min,
                "size_max": side_max,
                "extrude_min": extrude_min,
                "extrude_max": extrude_max
            },
        ],
    }
    packages = packtex_params['packages'][0]

    if quality != '':
        packages['quality'] = quality

    # if not 'bg' in src_dir:
    if trim:
        trim_path = _pjoin(src_dir, 'trim.json')
        if os.path.exists(trim_path):
            packtex_params['trim_file'] = trim_path

    if png_format == 'etc2':
        no_compress = _pjoin(src_dir, 'no_compress.tmp')
        compress = _pjoin(src_dir, 'compress.tmp')
        if os.path.exists(no_compress):
            packages['src'] = compress
            packtex_params['packages'].append({
                "src": no_compress,
                "format": "png",
                "size_min": 128,
                "size_max": 1024,
                "extrude_min": extrude_min,
                "extrude_max": extrude_max
            })

    params_str = json.dumps(packtex_params)
    params_str = params_str.replace('"', '""')
    params_str = '"' + params_str + '"'
    ret = _run_cmdv(EASYDB, 'pack-tex', params_str)

    if ret != 0:
        print('pack-tex failed')
        save_md5()
        sys.exit(1)


def do_gen_pkg_id():
    dirs = []
    for dirname in os.listdir(EDITOR_DIR):
        print(dirname)
        dirpath = _pjoin(EDITOR_DIR, dirname)
        if os.path.isdir(dirpath):
            dirs.append(dirname)

    gen_pkg_id('res_worldmap', 'worldmap', dirs, 700)

def check_pattern_aux(pattern_arr, item):
    for pattern in pattern_arr:
        if pattern.search(item):
            return True
    
    return False

def ep_regex(prefix):
    return r'^' + prefix + r'(((\.[0-9]+)?.ep(e|t))|(\.lua)|(_tag\.json)|(_tag\.lua))$'

def rm_unused_ep():
    pattern_arr = []
    for item in os.listdir(EDITOR_DIR):
        pattern = re.compile(ep_regex(item))
        pattern_arr.append(pattern)

    for cfg in EP_CFG:
        ep_dir = cfg['ep_dir']
        
        for item in os.listdir(ep_dir):
            if check_pattern_aux(pattern_arr, item):
                continue

            path = _pjoin(ep_dir, item)
            os.remove(path)

def rm_ep(root, prefix):
    pattern = re.compile(ep_regex(prefix))
    for item in os.listdir(root):
        if pattern.search(item):
            os.remove(_pjoin(root, item))

def calc_ep_md5(root, prefix):
    m = hashlib.md5()

    pattern = re.compile(ep_regex(prefix))
    for item in os.listdir(root):
        if not pattern.search(item):
            continue
            
        path = _pjoin(root, item)
        print('calc ep md5: ' + path)
        f = open(path, 'rb')
        fstr = f.read()
        f.close()
        m.update(fstr)

    return m.hexdigest()

def pack_ep():
    print('------------------- pack ep -------------------')
    # rm_dir_aux(EP_DIR)
    mk_dir_aux(EP_DIR)

    for cfg in EP_CFG:
        mk_dir_aux(cfg['ep_dir'])

    if dirs_custom:
        dirs = dirs_custom
    else:
        dirs = os.listdir(EDITOR_DIR)

    if 'map_individual' in dirs:
        dirs.remove('map_individual')
        dirs.insert(0, 'map_individual')

    # move map to end
    if 'map' in dirs:
        dirs.remove('map')
        dirs.append('map')

    for dirname in dirs:
        dirpath = _pjoin(EDITOR_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue

        print('pack ep: ' + dirname)

        json_dir = _pjoin(EDITOR_DIR, dirname, '_tmp_pack')  # , 'json')
        png_dir = _pjoin(EDITOR_DIR, dirname, '_tmp_pack')  # , 'png')
        root_dir = _pjoin(EDITOR_DIR, dirname)

        src_md5 = calc_png_and_json_md5(json_dir)
        record_md5(json_dir, src_md5)

        only_png = False
        texture_cfg_path = _pjoin(EDITOR_DIR, dirname, 'pack_texture.json')
        texture_cfg = load_json(texture_cfg_path)
        if texture_cfg:
            only_png = 'only_png' in texture_cfg and texture_cfg['only_png'] or False

        for cfg in EP_CFG:
            ep_dir = cfg['ep_dir']
            ep_output = _pjoin(ep_dir, dirname)

            if check_dep(ep_output):
                expected_md5 = get_md5(ep_output)
                dst_md5 = calc_ep_md5(ep_dir, dirname)
                if expected_md5 == dst_md5:
                    continue
        
            rm_ep(ep_dir, dirname)

            platform = cfg['platform']

            if only_png:
                tp_dir = _pjoin(TP_DIR, 'png', dirname, dirname + '_')
            else:
                tp_dir = _pjoin(cfg['tp_dir'], dirname, dirname + '_')

            do_pack_ep(json_dir, tp_dir, png_dir, ep_output, root_dir, platform)

            dst_md5 = calc_ep_md5(ep_dir, dirname)
            record_md5(ep_output, dst_md5)
            update_dep(ep_output, json_dir)
    
    rm_unused_ep()

# json_dir: tmp/bg_01/json/
# tp_out: tp/bg_01/bg_01
# tp_png: tmp/bg_01/png/
# ep_out EP_DIR/bg_01_
# root editor_data/bg_01/


def do_pack_ep(json_dir, tp_dir, png_dir, ep_dir, root_dir, platform):
    print('----------pack ep----------')
    LOD = '0'
    SCALE = '1'
    OUTPUT_TYPE = 'all'
    # PLATFORM = 'pc'
    PKG_CFG_FILE = _pjoin('..', '..', 'id', 'pkg_cfg.json')
    ret = _run_cmdv(EASYDB,
                    'pack-ep-new',
                    _pabs(json_dir),
                    _pabs(tp_dir),
                    _pabs(png_dir),
                    _pabs(ep_dir),
                    OUTPUT_TYPE,
                    LOD,
                    SCALE,
                    'null',
                    platform,
                    _pabs(PKG_CFG_FILE),
                    _pabs(root_dir)
                    )
    if ret != 0:
        save_md5()
        sys.exit(1)

def rm_unused_pkg():
    name_map = {}
    for item in os.listdir(EDITOR_DIR):
        name_map[item] = True
    
    pattern = re.compile(r'^([a-zA-Z0-9_]+)\.pkg')
    for cfg in EP_CFG:
        pkg_dir = cfg['pkg_dir']
        for item in os.listdir(pkg_dir):
            m = pattern.search(item)
            if not m or not m.group(1) in name_map:
                path = _pjoin(pkg_dir, item)
                os.remove(path)

def pack_pkg():
    if dirs_custom:
        dirs = dirs_custom
    else:
        dirs = os.listdir(EDITOR_DIR)

    for cfg in EP_CFG:
        root_dir = cfg['ep_dir']
        pkg_dir = cfg['pkg_dir']

        mk_dir_aux(pkg_dir)

        for dirname in dirs:
            dirpath = _pjoin(EDITOR_DIR, dirname)
            if not os.path.isdir(dirpath):
                continue

            ep_output = _pjoin(root_dir, dirname)
            pkg_output = _pjoin(pkg_dir, dirname + '.pkg')
            
            if check_dep(pkg_output) and check_md5(pkg_output, False):
                continue

            _run_cmdv(
                EASYDB,
                'pack-pkg',
                root_dir,
                dirname)

            pkg_tmp = ep_output + '.pkg'
            print('copy ' + pkg_tmp + ' to ' + pkg_output)
            shutil.copyfile(pkg_tmp, pkg_output)
            
            md5 = calc_md5(pkg_output)
            record_md5(pkg_output, md5)
            update_dep(pkg_output, ep_output)
    
    rm_unused_pkg()

def dump_bg_info(all_bg, meta_dir):
    unit_size = TILE_SIZE / TILE_SCALE
    logic = load_json(_pjoin(meta_dir, 'logic.json'))
    scene_height = logic['height']
    scene_width = logic['width']

    info = {}
    info['unit_size'] = TILE_SIZE / TILE_SCALE

    for bg in all_bg:
        x = bg['x'] + bg['w'] / 2 - scene_width / 2
        y = bg['y'] + bg['h'] / 2 - scene_height / 2

        bg['x'] = x
        bg['y'] = y
        bg['pkg'] = 'worldmap/' + bg['dir']
        bg['export'] = bg['name']

        gx = int(math.floor(x / unit_size))
        gy = int(math.floor(y / unit_size))
        key = '%d_%d' % (gx, gy)

        if key in info:
            area = info[key]
        else:
            area = []
            info[key] = area

        area.append(bg)

    dump_json(_pjoin(meta_dir, 'bg.json'), info)


def gen_tiles(lr_path, link_info, output, unit_size, scale, dash_size=30, gap_size=30):
    ret = _run_cmdv(LR2PNG,
                    lr_path,
                    '-o', output,
                    '-u', str(unit_size),
                    '-s', str(scale),
                    # '-l', link_info,
                    # '--dash_size', str(dash_size),
                    # '--gap_size', str(gap_size),
                    '--win_size', '%dx%d' % (WIN_WIDTH, WIN_HEIGHT)
                    )

    if ret != 0:
        save_md5()
        sys.exit(1)


def gen_no_compress(src_dir):
    config_path = _pjoin(src_dir, 'config.json')
    print('compress path = ' + config_path)
    if not os.path.exists(config_path):
        return

    _run_cmdv(
        EASYDB,
        'gen-no-compress',
        src_dir,
        config_path,
        src_dir
    )


def trim_png(src_dir):
    if 'bg' in src_dir:
        return

    _run_cmdv(
        EASYDB,
        'trim-image',
        src_dir,
        src_dir,
    )

def calc_tiles_src_md5(src_lr_path):
    m = hashlib.md5()

    jval = load_json(src_lr_path)
    bg_jval = jval['layer'][0]
    bg_str = json.dumps(bg_jval, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')).encode('GBK')
    m.update(bg_str)

    base_dir = os.path.dirname(src_lr_path)
    if 'sprite' in bg_jval:
        for spr in bg_jval['sprite']:
            path = _pjoin(base_dir, spr['filepath'])
            f = open(path, 'rb')
            fstr = f.read()
            f.close()
            m.update(fstr)

    ret = m.hexdigest()
    return ret

def gen_tiles_aux(lr_path, name):
    src_md5 = calc_tiles_src_md5(lr_path)
    dep_key = 'tiles_src_' + name
    out_dir = _pjoin(TILE_DIR, name)

    record_md5(dep_key, src_md5)

    if check_dep(out_dir) and check_md5(out_dir, False):
        return

    rm_dir_aux(out_dir)
    mk_dir_aux(out_dir)

    tile_out = _pjoin(out_dir, 'img')
    gen_tiles(lr_path, LINK_INFO, tile_out,
              TILE_SIZE, TILE_SCALE, DASH_SIZE, GAP_SIZE)
    
    dst_md5 = calc_md5(out_dir)
    record_md5(out_dir, dst_md5)
    update_dep(out_dir, dep_key)

def gen_bg_aux(lr_files_cfg):
    for name in lr_files_cfg.keys():
        cfg = lr_files_cfg[name]
        lr_path = cfg['base']
        lr_path = lr_path.replace(r'\_tmp_pack', '')

        gen_tiles_aux(lr_path, name)

        bg_name = 'bg_' + name
        clear_bg_dirs(EDITOR_DIR, bg_name)
        all_bg = gen_bg_dirs(EDITOR_DIR, name, bg_name)
        copy_bg_tmp(bg_name)

        meta_dir = _pjoin(TMP_META, name)
        dump_bg_info(all_bg, meta_dir)

def rm_unused_bg_dir(lr_files_cfg):
    pattern = re.compile(r'^bg(_([a-zA-Z0-9]+))?_[0-9]+$')
    for item in os.listdir(EDITOR_DIR):
        m = pattern.search(item)
        if not m:
            continue

        name = m.group(2)
        if not name or not name in lr_files_cfg:
            path = _pjoin(EDITOR_DIR, item)
            shutil.rmtree(path)
    

def do_pack_tex():
    print('---------- pack tex ----------')

    if dirs_custom:
        dirs = dirs_custom
    else:
        dirs = os.listdir(EDITOR_DIR)

    # rm_dir_aux(TP_DIR)
    mk_dir_aux(TP_DIR)
    for cfg in EP_CFG:
        mk_dir_aux(cfg['tp_dir'])

    for dirname in dirs:
        dirpath = _pjoin(EDITOR_DIR, dirname, '_tmp_pack')

        if not os.path.isdir(dirpath):
            continue

        json_dir = _pjoin(dirpath, 'json')
        png_dir = _pjoin(dirpath, 'png')
        rm_unused_png(json_dir, png_dir)

        side_max = 0
        side_min = 0
        extrude = 0
        # only_png = False
        trim = not 'bg_' in dirpath
        texture_cfg_path = _pjoin(EDITOR_DIR, dirname, 'pack_texture.json')
        texture_cfg = load_json(texture_cfg_path)
        if texture_cfg:
            side_max = texture_cfg['side_max']
            side_min = texture_cfg['side_min']
            extrude = texture_cfg['extrude']

            if 'no_trim' in texture_cfg:
                trim = not texture_cfg['no_trim']

            # only_png = 'only_png' in texture_cfg and texture_cfg['only_png'] or False
        
        if trim:
            trim_png(dirpath)
        
        gen_no_compress(dirpath)
        
        src_md5 = calc_md5(png_dir)
        record_md5(png_dir, src_md5)

        for cfg in EP_CFG:
            quality = cfg.get('quality', '')
            png_format = cfg['png_format']
            tp_dir = _pjoin(cfg['tp_dir'], dirname)
            tp_out = _pjoin(tp_dir, dirname + "_")

            if check_dep(tp_dir) and check_md5(tp_dir, False):
                continue

            pack_tex(dirpath, tp_out, side_min, side_max, extrude, extrude, png_format, quality, trim)

            dst_md5 = calc_md5(tp_dir)
            record_md5(tp_dir, dst_md5)
            update_dep(tp_dir, png_dir)

def do_fix_tmp_ref_path(tmp_dir, dirpath, filename):
    pattern = re.compile(r'"filepath" *: *"([^"]+)"')

    filepath = _pjoin(dirpath, filename)
    f = open(filepath, 'r')
    lines = f.readlines()
    f.close()

    dirty = False
    new_lines = []
    for line in lines:
        m = pattern.search(line)
        if not m:
            new_lines.append(line)
            continue
        
        raw_path = os.path.normpath(m.group(1))
        item_path = os.path.normpath(_pjoin(dirpath, raw_path))
        item_dirpath = os.path.dirname(item_path)
        relpath = os.path.normpath(os.path.relpath(item_dirpath, tmp_dir))
        if relpath.startswith('..'):
            fix_raw_path = os.path.normpath(_pjoin('..', raw_path))
            # print('tmp_dir: %s, item_path: %s, relpath: %s\nraw_path: %s, fix_raw_path: %s' % (tmp_dir, item_path, relpath, raw_path, fix_raw_path))

            new_line = line.replace(
                raw_path.replace('\\', '\\\\'), 
                fix_raw_path.replace('\\', '\\\\'))
            new_lines.append(new_line)

            # print('raw line: ' + line)
            # print('new line: ' + new_line)

            dirty = True
        else:
            new_lines.append(line)
    
    if dirty:
        print('fix ref file: ' + filepath)
        f = open(filepath, 'w')
        f.write(''.join(new_lines))
        f.close()


def fix_tmp_ref_path(dirpath):
    for root, _, files in os.walk(dirpath):
        for filename in files:
            if '.json' in filename:
                do_fix_tmp_ref_path(dirpath, root, filename)


def prepare_dirs():
    dirs = [ v for v in os.listdir(EDITOR_DIR) if os.path.isdir(_pjoin(EDITOR_DIR, v)) and not v.startswith('bg_') ]

    if dirs_custom:
        dirs = [ v for v in dirs if v in dirs_custom ]
    
    for dir in dirs:
        path = _pjoin(EDITOR_DIR, dir)
        md5 = calc_png_and_json_md5(path)
        record_md5(path, md5)

    dirs = [ v for v in dirs if not check_dep(_pjoin(EDITOR_DIR, v, '_tmp_pack')) or not check_md5(_pjoin(EDITOR_DIR, v, '_tmp_pack')) ]

    clear_tmp(dirs)
    copy_tmp(dirs)

    # gen_activity_city(TMP_MAP_GEN, TMP_MAP)

    for subdir in dirs:
        subdir = _pjoin(EDITOR_DIR, subdir)
        tmp_dir = _pjoin(subdir, '_tmp_pack')
        fix_tmp_ref_path(tmp_dir)
        
        md5 = calc_png_and_json_md5(tmp_dir)
        record_md5(tmp_dir, md5)
        update_dep(tmp_dir, subdir)


def scan_lr_files(dir):
    lr_files_cfg = {}
    pattern = re.compile(r'^([a-zA-Z0-9_]+)(\.([a-z]+))?_lr\.json$')
    for item in os.listdir(dir):
        m = pattern.search(item)
        if not m:
            continue
        
        name = m.group(1)
        filetype = m.group(3) or 'base'

        if name in lr_files_cfg:
            cfg = lr_files_cfg[name]
        else:
            cfg = {}
            lr_files_cfg[name] = cfg
        
        cfg[filetype] = _pjoin(dir, item)
        print('name = %s filetype = %s' % (name, filetype))
    
    return lr_files_cfg

def gen_lr_info(lr_files_cfg, out_dir):
    for name in lr_files_cfg.keys():
        out_meta_dir = _pjoin(out_dir, name)
        cfg = lr_files_cfg[name]

        base = cfg['base']
        print('base = %s' % base)

        if 'real' in cfg:
            logic = cfg['real']
            print('real = %s' % logic)
        else:
            logic = ''
        
        dump_lr(base, logic, TMP_MAP_GEN, out_meta_dir)

        if 'quest' in cfg:
            point = cfg['quest']
            print('quest = %s' % point)
            gen_poi(point, TMP_MAP_GEN, out_meta_dir)


def copy_android_id_to_ios():
    id_dir = _pjoin('..', '..', 'id', 'spr')
    android_dir = _pjoin(id_dir, 'android')
    ios_dir = _pjoin(id_dir, 'ios')

    copy_names = [ v for v in os.listdir(EDITOR_DIR) if os.path.isdir(_pjoin(EDITOR_DIR, v)) and not v.startswith('bg_') ]

    for name in copy_names:
        filename = name + '.json'
        src_path = _pjoin(android_dir, filename)
        dst_path = _pjoin(ios_dir, filename)

        if os.path.exists(src_path):
            shutil.copyfile(src_path, dst_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='worldmap_pack')
    parser.add_argument('-p', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    prepare_dirs()
    
    lr_files_cfg = scan_lr_files(TMP_MAP_JSON)
    gen_lr_info(lr_files_cfg, TMP_META)

    gen_bg_aux(lr_files_cfg)
    rm_unused_bg_dir(lr_files_cfg)

    do_gen_pkg_id()

    if args.p:
        do_pack_tex()

    pack_ep()
    pack_pkg()
    copy_android_id_to_ios()

    save_md5()

