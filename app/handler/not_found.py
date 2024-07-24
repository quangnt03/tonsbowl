from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": "The requested resource was not found"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )