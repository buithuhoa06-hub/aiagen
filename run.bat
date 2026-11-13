@echo off
title Thien Minh AI Agent - Next-Gen Tender Evaluation System
echo ========================================================
echo  KHOI DONG HE THONG AI AGENT DANH GIA CHAO GIA DU AN
echo  CONG TY CO PHAN CONG NGHE THIEN MINH
echo ========================================================
echo.
echo 1. Dang kiem tra thu vien...
pip install -r requirements.txt
echo.
echo 2. Dang khoi dong Web App tren Localhost (http://localhost:8501)...
start http://localhost:8501
python server.py
pause
