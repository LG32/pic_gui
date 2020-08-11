rem %~dp0..\..\tools\Python27\python.exe pack.py 0123

set DEST=\\192.168.6.245\Desert\Documents\code\client\res

if exist %DEST%\common\worldmap.*ep*; del /f/q %DEST%\common\worldmap.*ep*
copy /Y ..\output\ios\worldmap.*ep* %DEST%\common\

pause