set ROOT_DIR=..\data\daditu\json\
set SRC=%ROOT_DIR%desert.real_lr.json
set DST=%ROOT_DIR%block.json
python generate_grid.py %SRC% %DST%

pause