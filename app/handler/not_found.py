from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if type(exc.detail) == dict:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                **exc.detail,
                "status_code": exc.status_code
            },
        )
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": "Resource unavailable",
                "status_code": 404
            },
        )