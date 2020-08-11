# -*- coding: utf-8 -*-

import os
import sys
import git
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'script'))
from ej_slave_util import git_pull, git_commit, git_push, svn_up, snf


j = os.path.join

DIR_RAWRES = j('..', '..')
DIR_CLIENT = j('..', '..', '..', 'client')
DIR_RES = j(DIR_CLIENT, 'res')
DIR_COMMON = j(DIR_CLIENT, 'common')
DIR_SVN = os.path.abspath(j('..', 'data', 'editor_data', 'map'))
repo_rawres = git.Repo(DIR_RAWRES)
repo_res = git.Repo(DIR_RES)
repo_common = git.Repo(DIR_COMMON)

git_pull(repo_rawres)
git_pull(repo_common)
git_pull(repo_res)

COMMIT_MSG = 'up worldmap'

print(DIR_SVN)
svn_up(DIR_SVN, COMMIT_MSG)

tasks = [
    'pack_new.py',
    'deploy.bat',
]

parser = argparse.ArgumentParser(description='slave_pack')
parser.add_argument('-p', action='store_true')
parser.add_argument('-ep', action='store_true')
args = parser.parse_args(sys.argv[1:])

print('---------- args: ----------')
print(sys.argv[1:])
if args.p:
    print('pack with pic')
    tasks[0] += ' -p'

n = len(tasks)
for i, task in enumerate(tasks):
    if '.py' in task:
        ret = os.system(r'..\..\tools\Python27\python.exe ' + task)
    else:
        ret = os.system(task)
    assert ret == 0, task

snf(u'[_PROGRESS_] GIT COMMIT')

git_commit(repo_rawres, COMMIT_MSG)
git_commit(repo_res, COMMIT_MSG)

git_push(repo_rawres)
git_push(repo_res)

