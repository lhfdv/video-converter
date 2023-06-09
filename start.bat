@echo off
set PYTHONPATH=.
set UVICORN_WORKERS=1
uvicorn main:app --host 0.0.0.0 --port 8000