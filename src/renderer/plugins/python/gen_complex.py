import sys, os, copy
from util import load_json, dump_json, TMP_COMPLEX, TMP_SPR

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    dirpath = sys.argv[1]
    png_dir = os.path.join(dirpath, 'png')
    json_dir = os.path.join(dirpath, 'json')

    for root, _, files in os.walk(png_dir):
        for filename in files:
            filename = filename.lower()
            if not filename.endswith('.png'):
                continue
            
            export = filename[:-4]
            dst_path = os.path.join(json_dir, export + '_complex.json')
            filepath = os.path.join(root, filename)

            spr_jval = copy.deepcopy(TMP_SPR)
            spr_jval['filepath'] = os.path.relpath(filepath, json_dir)
            
            dst_jval = copy.deepcopy(TMP_COMPLEX)
            dst_jval['name'] = filename[:-4]
            dst_jval['sprite'].append(spr_jval)

            dump_json(dst_path, dst_jval)