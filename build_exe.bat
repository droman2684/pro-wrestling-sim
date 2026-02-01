@echo off
echo ==========================================
echo   Building Pro Wrestling Sim EXE
echo ==========================================

python -m PyInstaller ^
    --name "ProWrestlingSim" ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --paths "src" ^
    --add-data "src/ui/web/templates;src/ui/web/templates" ^
    --add-data "src/ui/web/static;src/ui/web/static" ^
    --hidden-import "jinja2.ext" ^
    --collect-all "flask" ^
    play_desktop.py

echo.
echo ==========================================
echo   Build Complete!
echo   Packaging dependencies...
echo ==========================================

xcopy "data" "dist\ProWrestlingSim\data" /E /I /Y
xcopy "saves" "dist\ProWrestlingSim\saves" /E /I /Y

echo.
echo ==========================================
echo   SUCCESS!
echo   The folder 'dist/ProWrestlingSim' is ready.
echo   You can now ZIP that folder and share it!
echo ==========================================
pause
