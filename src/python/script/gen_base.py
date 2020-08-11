import sys
import os
import io
import json
import argparse
import copy
from util import dump_json, load_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate grid')
    parser.add_argument('src', type=str, help='src path')
    args = parser.parse_args(sys.argv[1:])

    src = args.src
    if not os.path.exists(src):
        print('file does not exists: ' + src)
        sys.exit(1)
    
    jval = load_json(src)

    basename = os.path.basename(src)
    for layer in jval['layer']:
        layer.pop('sprite', None)
        layer['base filepath'] = basename

    dirname = os.path.dirname(src)
    dst = os.path.join(dirname, 'new_' + basename)

    dump_json(dst, jval)
