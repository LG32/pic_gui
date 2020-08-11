# -*- coding: utf-8 -*-

import os
import sys
import git
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'script'))
from ej_slave_util import git_commit, git_push, svn_up, snf, svn_add, svn_ci


j = os.path.join

DIR_RAWRES = j('..', '..')
DIR_RES = j('..', '..', '..', 'client', 'res')
DIR_TEXPACK_DATA = j(DIR_RAWRES, 'texpack_data')
DIR_SVN = os.path.abspath(j('..', 'data', 'editor_data', 'map'))
repo_rawres = git.Repo(DIR_RAWRES)
repo_res = git.Repo(DIR_RES)
repo_texpack_data = git.Repo(DIR_TEXPACK_DATA)

COMMIT_MSG = 'up worldmap'

print(DIR_SVN)
svn_up(DIR_SVN, COMMIT_MSG)

tasks = [
    'gen_lr.bat',
]

n = len(tasks)
for i, task in enumerate(tasks):
    if '.py' in task:
        ret = os.system(r'..\..\tools\Python27\python.exe ' + task)
    else:
        ret = os.system(task)
    assert ret == 0, task

# svn_add(DIR_SVN, COMMIT_MSG)
svn_ci(DIR_SVN, COMMIT_MSG)
