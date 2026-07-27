@echo off
echo ============================================
echo   NS_V47 - Analisis de Modelo Power BI
echo   Verificando prerequisitos...
echo ============================================
echo.

REM --- Verificar Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH.
    echo Descargue Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado:
python --version
echo.

REM --- Instalar dependencias requeridas ---
echo Instalando librerias requeridas para el modelo...
pip install pandas matplotlib --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] pip fallo. Intentando con python -m pip...
    python -m pip install pandas matplotlib --quiet --disable-pip-version-check
)
echo.

echo ============================================
echo   Dependencias instaladas correctamente:
echo   - pandas (tablas de datos)
echo   - matplotlib (graficos Python)
echo ============================================
echo.

REM --- Abrir Power BI ---
echo Abriendo NS.pbip...
start "" "%~dp0NS.pbip"
echo.
echo Listo. En Power BI:
echo   1. Aceptar "Ejecutar scripts Python" si pregunta
echo   2. Ir a pagina "04 Python Analisis Modelo"
echo   3. Ver graficos del modelo
echo.
pause
