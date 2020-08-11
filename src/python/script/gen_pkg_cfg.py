# -*- coding: utf-8 -*-

import os
from os import listdir
from os.path import isdir, join
import json
import re


# 获得pkg 包名对应的ID
def get_pkg_map():
    max_id = 0
    pkg_json_path = os.path.join("..", "..", "id", "pkg_cfg.json")
    pkg_map = {}
    id_map = {}
    with open(pkg_json_path, "r") as handlefile:
        json_source = handlefile.read()
        patt = re.compile(r"//[^\n\r]+\n", re.MULTILINE | re.DOTALL)
        def capture(obj):
            return "\n"

        data = re.sub(patt, capture, json_source)
        pkg_list = json.loads(data)
        for entry in pkg_list:
            pkg_id = entry["pkg_id"]
            pkg_map[entry["name"]] = pkg_id
            id_map[pkg_id] = entry["name"]
            if pkg_id > max_id:
                max_id = pkg_id 
    return pkg_map, id_map, max_id


# 生成新的pkg_json内容
def gen_pkg_json_string(dir_name, pkg_dir, tasks, from_id):
    print("gen_pkg_json_string!!!")
    dir_names = tasks
    pkg_map, id_map, max_id = get_pkg_map()
    out_json = []
    for name in dir_names:
        entry_name = pkg_dir and (pkg_dir + "/" + name) or name
        pkg_id = from_id

        if entry_name in pkg_map:
            pkg_id = pkg_map[entry_name]
        else:
            while from_id in id_map:
                from_id = from_id + 1
                pkg_id = from_id

        entry = {
            "name": entry_name,
            "path": "..\\" + dir_name + "\\data\\editor_data\\" + name,
            "pkg_id": pkg_id
        }
        out_json.append(entry)
        id_map[pkg_id] = entry_name

    s = json.dumps(out_json, indent=4)
    patt = re.compile(r"^\[(.+)\n\]$", re.MULTILINE | re.DOTALL)
    data = re.match(patt, s)
    return data.group(1) + ","


# 更新pkg_json文件
def gen_pkg_id(dir_name, pkg_dir, tasks, from_id):
    pkg_json_path = os.path.join("..", "..", "id", "pkg_cfg.json")
    data = False
    with open(pkg_json_path) as handlefile:
        s = handlefile.read().decode("gbk")
        def capture(obj):
            cs1 = obj.group(1)
            # cs2 = obj.group(2)
            cs2 = gen_pkg_json_string(dir_name, pkg_dir, tasks, from_id)
            cs3 = obj.group(3)
            ret = cs1 + "\n" + cs2 + "\n" + cs3
            return ret

        patt = re.compile(r"(//-+" + dir_name + "\s+begin[^\r\n]*)(.+)(\s*//.*" + dir_name + "\s+end[^\r\n]*)", re.MULTILINE | re.DOTALL)
        data = re.sub(patt, capture, s)
        handlefile.close()
        with open(pkg_json_path, "w") as handlefile:
            data = data.encode("gbk")
            print("update pkg_cfg.json!!!!")
            handlefile.write(data)
