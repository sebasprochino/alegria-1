@echo off
SETLOCAL EnableDelayedExpansion

:: --- CONFIGURACIÓN DE COLORES ---
COLOR 0B

echo.
echo  #################################################################
echo  #                                                               #
echo  #      🚀  ALEGRIA_OS - SISTEMA DE COHERENCIA CREATIVA         #
echo  #                                                               #
echo  #################################################################
echo.
echo  [*] Iniciando nucleos del sistema...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"
echo.


:: --- BUSCAR VENV ---
IF NOT EXIST "backend\venv" (
    echo  [!] ADVERTENCIA: No se encontro el entorno virtual en backend\venv
    echo  [!] Es posible que el backend requiera instalar dependencias.
)

:: --- SINCRONIZAR DB (PRISMA) ---
echo  [+] Sincronizando Base de Datos y Generando Cliente Prisma...
start "ALEGRIA_OS - DB SYNC" /WAIT cmd /c "TITLE ALEGRIA_OS - DB SYNC && cd backend && set DATABASE_URL=file:./dev.db && npx prisma db push --skip-generate && npx prisma generate"
echo  [OK] Prisma Sync completado.

:: --- INICIAR BACKEND ---
echo  [+] Activando BACKEND CORE (Puerto 8000)...
:: Usamos /min para que no estorbe pero cmd /k para que si hay error el usuario lo vea al restaurar la ventana
start "ALEGRIA_OS - BACKEND" cmd /k "TITLE ALEGRIA_OS - BACKEND && cd backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && uvicorn src.server:app --reload"

:: --- INICIAR FRONTEND ---
echo  [+] Activando FRONTEND UI (Puerto 5173)...
start "ALEGRIA_OS - FRONTEND" cmd /k "TITLE ALEGRIA_OS - FRONTEND && cd frontend && npm.cmd run dev"

echo.
echo  [OK] Lanzamiento completado exitosamente.
echo  ---------------------------------------------------------------
echo  [*] Backend:  http://127.0.0.1:8000
echo  [*] Frontend: http://127.0.0.1:5173
echo  ---------------------------------------------------------------
echo.
echo  [CONSEJO] Si el frontend dice 'Connection Refused', espera 5 segundos
echo  y recarga (F5). El backend esta cargando modelos de IA.
echo.
echo  Presione cualquier tecla para cerrar este lanzador...
echo  (Las ventanas de Backend y Frontend seguiran abiertas)
pause > nul
