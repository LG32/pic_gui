
set RES_PATH=..\..\..\client\res

call :copy_meta

for %%p IN (pc android) do (
    call :copy_pkg %%p %%p
)
call :copy_pkg android ios

goto:eof

:copy_meta
set DST_DIR=%RES_PATH%\common\worldmap
if exist %DST_DIR%; rd /s /q %DST_DIR%
mkdir %DST_DIR%
xcopy /Y /S ..\meta\* %DST_DIR%
exit /b 0

:copy_pkg
set SRC_DIR=..\pkg\%~1
set DST_DIR=%RES_PATH%\%~2\worldmap
if exist %DST_DIR%; rd /s /q %DST_DIR%
mkdir %DST_DIR%
copy /Y %SRC_DIR%\*.pkg %DST_DIR%
exit /b 0

