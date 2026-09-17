@echo off
title Clothing IR System
color 0F
echo.
echo  ============================================================
echo    CLOTHING INFORMATION RETRIEVAL SYSTEM
echo  ============================================================
echo    1) Run command-line version
echo    2) Run web front end
echo    3) Exit
echo  ============================================================
echo.
set /p choice="Choose an option (1, 2 or 3): "

if "%choice%"=="1" (
    echo.
    echo  Starting interactive mode...
    python clothing_ir_model.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo  Starting web server... open http://127.0.0.1:5000 in your browser
    python webapp.py
    pause
) else (
    echo Goodbye!
)

echo.
pause