@echo off

::Configurar para iniciar task pelo diretório deste script
cd ..
IF NOT EXIST %CD%\logs\ mkdir %CD%\logs
SET LOG_FILE=%CD%\logs\data_sync_import.log

ECHO -------------------------------------------------- >> %LOG_FILE%
echo [%date:~6,10%/%date:~3,2%/%date:~0,2% %time:~0,8%] Runing scripts... >> %LOG_FILE%

call C:\cygwin64\bin\bash.exe -l "%CD%\scripts\download_files.sh" >> %LOG_FILE%
:: Activate python env in cmd
::call %HomePath%\Anaconda3\Scripts\activate.bat
:: Execute MySQL import python script
python "%CD%\scripts\MySQL_data_import_V3.py" >> %LOG_FILE% 2>&1

echo [%date:~6,10%/%date:~3,2%/%date:~0,2% %time:~0,8%] Scripts finished! >> %LOG_FILE%
::PAUSE
exit