from starlette.exceptions import HTTPException
from fastapi import status

class NotFoundException(HTTPException):
    def __init__(
        self, 
        detail: dict = None, 
        status_code: int = status.HTTP_404_NOT_FOUND, 
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, headers)
        self.detail = {
            **detail,
            "status_code": status_code
        }
class InvalidBodyException(HTTPException):
    def __init__(
        self, 
        detail: dict = None, 
        status_code: int = status.HTTP_400_BAD_REQUEST, 
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, headers)
        self.detail = {
            **detail,
            "status_code": status_code
        }
class InvalidOperation(HTTPException):
    def __init__(
        self, 
        detail: dict = None, 
        status_code: int = status.HTTP_406_NOT_ACCEPTABLE, 
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, headers)
        self.detail = {
            **detail,
            "status_code": status_code
        }
class InternalServerException(HTTPException):
    def __init__(
        self, 
        detail: dict = None, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, 
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, headers)
        self.detail = {
            **detail,
            "status_code": status_code
        }