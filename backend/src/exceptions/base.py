from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class ApplicationException(HTTPException):
    """Generic Application Exception"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "InternalServerError"
    detail: Any = "An internal server error has occurred, please try again in some time."
    debug_message: Optional[str | Exception] = ""
    headers: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        debug_message: Optional[str | Exception] = "",
        detail: Any = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.debug_message = debug_message
        self.headers = headers

        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code

        super().__init__(status_code=self.status_code, detail=self.detail, headers=headers)
