@echo off  
REM Установка NODE.js 
node-v22.13.1-x64.msi
REM Установка Python-зависимостей  
python -m pip install --upgrade pip  
python -m pip install -r requirements.txt  
pause  