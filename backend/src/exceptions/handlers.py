from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from exceptions import ApplicationException, InvalidPayloadException, NotFoundException
from log import log
from schemas import ErrorSchema


def compute_validation_error_string(errors: list[dict]) -> str:
    def get_location_string(loc):
        return " -> ".join([str(segment) for segment in loc])

    error_message = InvalidPayloadException.detail
    if isinstance(errors, list):
        messages = [f"{get_location_string(e['loc'])}: {e['msg']}" for e in errors]
        error_message = f"{len(messages)} validation error(s):"
        error_message += "".join(f" [{i+1}] {message}" for i, message in enumerate(messages))
    return error_message


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = jsonable_encoder(exc.errors())
        error_message = compute_validation_error_string(errors=errors)
        error_response = ErrorSchema(
            error_code=InvalidPayloadException.error_code, error_msg=error_message
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.dict(by_alias=True),
        )

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        log.error(exc.detail)
        log.exception(exc)
        if exc.debug_message:
            log.error(f"Debug message: {exc.debug_message}")

        error_response = ErrorSchema(error_code=exc.error_code, error_msg=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(by_alias=True),
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        if exc.status_code == 405 or exc.status_code == 404:
            error_response = ErrorSchema(
                error_code=NotFoundException.error_code, error_msg=exc.detail
            )

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=error_response.dict(by_alias=True),
                headers=exc.headers,
            )
        return await http_exception_handler(request, exc)
