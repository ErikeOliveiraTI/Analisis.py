@echo off

REM anterior echo Iniciando agendador de backup (SEM ADMIN)...
REM anterior python z:\git\init_\analise_py\agendador_sem_admin.py

REM Script para iniciar o agendador de backup SEM ADMIN - VERSÃO ALTERNATIVA
REM Coloque na pasta Startup do Windows
REM Executa Python em background sem exibir janela

start /B "" python z:\git\init_\analise_py\agendador_sem_admin.py
exit /b 0