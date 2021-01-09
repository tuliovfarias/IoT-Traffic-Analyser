@echo off

echo [%date:~6,10%-%date:~3,2%-%date:~0,2% %time:~0,8%] Runing scripts...

call C:\cygwin64\bin\bash.exe -l "%CD%\sync.sh"
:: Activate python env in cmd
call C:\Users\tulio\Anaconda3\Scripts\activate.bat
:: Execute MySQL import python script
python "%CD%\MySQL_data_import_V3.py"

echo [%date:~6,10%-%date:~3,2%-%date:~0,2% %time:~0,8%] Scripts finished!
echo.

::pause
exit