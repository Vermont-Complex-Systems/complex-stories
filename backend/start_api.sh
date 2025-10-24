#!/bin/bash
# Start FastAPI server for Complex Stories backend

cd /users/j/s/jstonge1/complex-stories-main/backend
uv run fastapi run app/main.py --host 0.0.0.0 --port 3001