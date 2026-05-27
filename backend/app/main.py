from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import json
import sys
import io

# NEW
from app.safety.middleware import SafetyMiddleware

# FORCEFULLY set UTF-8 encoding
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )

if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer,
        encoding='utf-8',
        errors='replace'
    )

app = FastAPI()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    try:
        error_response = json.dumps(
            {"detail": "Internal server error"},
            ensure_ascii=True
        )
    except:
        error_response = '{"detail":"Internal server error"}'

    return Response(
        content=error_response,
        status_code=500,
        media_type="application/json; charset=utf-8"
    )


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW → Safety Middleware
app.add_middleware(
    SafetyMiddleware
)

# Routes
from app.routes import learning

app.include_router(
    learning.router,
    prefix="/api/learning"
)

@app.get("/")
def read_root():
    return Response(
        content='{"message":"LearnMate AI Backend is running"}',
        media_type="application/json; charset=utf-8"
    )