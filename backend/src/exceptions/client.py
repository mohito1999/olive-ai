from fastapi import status

from .base import ApplicationException


# Internal server error
class InternalServerException(ApplicationException):
    """Internal Server Error exception"""


class InvalidAccessTokenException(InternalServerException):
    detail = "Invalid access token from identity provider"


# Too many requests
class TooManyRequestsException(ApplicationException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "TooManyRequests"
    detail = "Request made too soon. Please retry after some time."


# Unauthorized
class UnauthorizedException(ApplicationException):
    """Unauthorized exception"""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "Unauthorized"
    detail = "Unauthorized request"


# Bad request
class BadRequestException(ApplicationException):
    """Bad request exception"""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "InvalidRequest"
    detail = "Invalid request body"


class InvalidHeadersException(BadRequestException):
    detail = "Invalid headers sent in request"


class InvalidPayloadException(BadRequestException):
    detail = "Invalid payload sent in request"


# Not found
class NotFoundException(ApplicationException):
    """Not found exception"""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NotFound"
    detail = "The resource you are looking for was not found"


# Forbidden
class ForbiddenException(ApplicationException):
    """Forbidden exception"""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "Forbidden"
    detail = "The access to the resource is forbidden"
