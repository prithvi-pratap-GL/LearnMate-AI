from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .gateway import SafetyGateway


class SafetyMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        if request.method == "POST":

            try:
                body = await request.json()

                # Try multiple common fields
                text = (
                    body.get("topic")
                    or body.get("prompt")
                    or body.get("question")
                    or body.get("text")
                    or body.get("message")
                    or ""
                )

                if text:

                    result = SafetyGateway.validate_input(
                        text
                    )

                    if not result.is_safe:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": result.reason
                            },
                        )

            except Exception as e:
                print(
                    "Safety middleware error:",
                    e
                )

        return await call_next(
            request
        )