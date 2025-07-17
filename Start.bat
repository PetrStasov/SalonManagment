@ECHO OFF
start cmd.exe /C "python manage.py runserver"
timeout /T 6 /NOBREAK >NUL
start "" "http://127.0.0.1:8000/"
