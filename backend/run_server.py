#!/usr/bin/env python
"""
Run the FastAPI server with proper UTF-8 encoding on Windows.
This script forces UTF-8 encoding and prevents encoding errors.
"""
import sys
import os
import io

# CRITICAL: Set UTF-8 encoding BEFORE anything else
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Force sys.stdout and sys.stderr to use UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Disable all colored output and fancy logging that might cause encoding issues
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['NO_COLOR'] = '1'

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting LearnMate AI Backend with UTF-8 encoding...")
    print("Server running on http://127.0.0.1:5000")

    # Run uvicorn with UTF-8 safe settings
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        reload=True,
        # Disable access logs which might cause encoding issues
        access_log=False,
        log_level="critical",  # Minimize logging
    )
