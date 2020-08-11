
import sys
import argparse
import os
import copy
import shutil
import re
import imagesize
from util import load_json, dump_json, TMP_COMPLEX, TMP_SPR

def get_fname_no_ext(path):
    pkg_name = os.path.splitext(os.path.basename(path))[0]
    return pkg_name

def get_png_dst(src, dst_dir):
    src = os.path.normpath(src)
    dst_dir = os.path.normpath(dst_dir)

    src_base = os.path.basename(src)
    src_dir = os.path.dirname(src)
    src_dir_base = os.path.basename(src_dir)

    newname = src_dir_base + '_' + src_base
    dst = os.path.join(dst_dir, newname)

    return dst

def copy_png(src, dst_dir):
    dst = get_png_dst(src, dst_dir)
    print('copy %s to %s' % (src, dst))
    shutil.copy(src, dst)

def fix_anim_png(src, dst_png_dir):
    src_dir = os.path.dirname(src)
    jval = load_json(src)
    for layer in jval['layer']:
        for frame in layer['frame']:
            for spr in frame['actor']:
                if not spr['filepath'].endswith('.png'):
                    continue
                
                src_png = os.path.join(src_dir, spr['filepath'])
                dst_png = get_png_dst(src_png, dst_png_dir)

                relpath = os.path.relpath(dst_png, src_dir)
                spr['filepath'] = relpath
    
    dump_json(src, jval)

def gen_complex(src, dst_json_dir):
    fpath = src
    m = re.search('(ship[0-9])_real_anim.json', fpath)
    if m == None:
        return

    export = m.group(1)

    dst_json = os.path.join(dst_json_dir, export + '_complex.json')
    relpath = os.path.relpath(src, dst_json_dir)

    comp = copy.deepcopy(TMP_COMPLEX)
    comp['name'] = export

    spr = copy.deepcopy(TMP_SPR)
    spr['filepath'] = relpath
    comp['sprite'].append(spr)

    dump_json(dst_json, comp)

    return export

def do_gen_player(src, dst, meta_dir):
    if not os.path.isdir(src):
        print('%s is not a dir' % src)
        sys.exit(1)

    dst_json_dir = os.path.join(dst, 'json', 'player')
    # dst_png_dir = os.path.join(dst, 'png')

    dst_player_info = os.path.join(meta_dir, 'player.json')
    export_list = []

    src = os.path.normpath(src)

    for root, _, files in os.walk(src):
        for fpath in files:
            fullpath = os.path.join(root, fpath) 
            # if fpath.endswith('.png'):
            #     copy_png(fullpath, dst_png_dir)
            #     continue
            
            if fpath.endswith('_anim.json'):
                if fpath.endswith('_real_anim.json'):
                    export = gen_complex(fullpath, dst_json_dir)
                    export_list.append(export)

                # fix_anim_png(fullpath, dst_png_dir)
    
    export_list.sort()
    print('dst player info ' + dst_player_info)
    dump_json(dst_player_info, export_list)

    # print('remove src player dir: ' + src)
    # shutil.rmtree(src)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen player')
    parser.add_argument('src', type=str)
    parser.add_argument('dst', type=str)
    args = parser.parse_args(sys.argv[1:])

    src = args.src
    dst = args.dst

    if not os.path.exists(src):
        print('path no founed: ' + src)
        sys.exit(1)
    
    do_gen_player(src, dst, dst)
