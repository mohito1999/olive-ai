from fastapi import APIRouter

from schemas import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health():
    return HealthResponse()
