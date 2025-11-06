@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
set FAIRX_PORT=8000
uvicorn src.fairx.server:app --host 0.0.0.0 --port %FAIRX_PORT% --reload