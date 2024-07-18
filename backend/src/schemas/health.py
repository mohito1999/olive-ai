from pydantic import Field

from .base import BaseSchema


class HealthResponse(BaseSchema):
    message: str = Field("OK")
