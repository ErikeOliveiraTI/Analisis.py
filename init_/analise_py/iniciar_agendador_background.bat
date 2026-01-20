@echo off
REM Inicia agendador de backup em background permanente
REM Executa a cada login do Windows

cd /d z:\git\init_\analise_py

REM Executar Python em background permanente
start "" /b python backup_scheduler.py

REM Ou usar nohup se preferir:
REM bash -c "nohup python /z/git/init_/analise_py/backup_scheduler.py > /z/git/rotina/log/agendador.log 2>&1 &"

exit
