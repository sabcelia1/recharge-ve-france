@echo off
REM Lance tout le pipeline : environnement Python, ingestion, nettoyage.
REM Double-cliquez sur ce fichier, ou tapez "lancer" dans une console ouverte dans ce dossier.
cd /d "%~dp0"
"%SystemRoot%\System32\chcp.com" 65001 >nul 2>&1

if not exist ".venv\Scripts\python.exe" (
    echo === Creation de l'environnement Python...
    python -m venv .venv || goto :erreur
)

echo === Installation des librairies...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || goto :erreur

echo.
echo === Etape 1 : telechargement des donnees
".venv\Scripts\python.exe" src\ingest.py || goto :erreur

echo.
echo === Etape 2 : nettoyage
".venv\Scripts\python.exe" src\clean.py || goto :erreur

echo.
echo === Termine ! Rapport qualite : reports\qualite_donnees.md
pause
exit /b 0

:erreur
echo.
echo *** Une erreur s'est produite : copiez tout le texte ci-dessus et envoyez-le a Claude.
pause
exit /b 1
