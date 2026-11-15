@echo off
rem Regenera el sitio y lo publica en https://geobriel.github.io
rem Uso: doble clic en este archivo. Se publica en 1 a 2 minutos.
cd /d "%~dp0"
python build.py
git add -A
git commit -m "Actualización del sitio"
git push
echo.
echo Listo. En 1 a 2 minutos estara en https://geobriel.github.io
pause
