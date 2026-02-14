@echo off
echo ========================================
echo Tractage Electoral - Les Sables d'Olonne
echo ========================================
echo.

cd tractage-app

echo [1/2] Installation des dependances...
if not exist "node_modules" (
    npm install
) else (
    echo Dependances deja installees
)

echo.
echo [2/2] Demarrage du serveur...
echo.
echo Application disponible sur: http://localhost:3000
echo Appuyez sur Ctrl+C pour arreter
echo.

npm run dev
