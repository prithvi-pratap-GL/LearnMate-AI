from fastapi import Request
from fastapi.responses import JSONResponse

async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Log the exception
        print(f"An error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected error occurred."},
        )
