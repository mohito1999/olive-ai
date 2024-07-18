from pydantic import Field

from .base import BaseSchema


class ErrorSchema(BaseSchema):
    error_code: str = Field(..., alias="code")
    error_msg: str = Field(..., alias="message")
