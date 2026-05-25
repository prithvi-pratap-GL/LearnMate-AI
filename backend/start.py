#!/usr/bin/env python
"""
Minimal wrapper to start FastAPI without encoding issues on Windows.
"""
import sys
import os
import io
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Force UTF-8 everywhere
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Redirect stdout/stderr to UTF-8
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Silent mode - minimal output
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Run with minimal logging
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        access_log=False,
        log_level="critical",
        workers=1,
        loop="asyncio",
    )
