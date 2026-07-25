@echo off
title Dictee Medicale IA - Demarrage...
echo.
echo  ==========================================
echo   Demarrage de l'application...
echo   Chargement du modele Vosk (~1 minute)
echo  ==========================================
echo.
cd /d "c:\Users\Lenovo\Desktop\Stage\vosk_radiology"
.venv311\Scripts\python.exe DicteeMedicaleAI\main.py
pause
