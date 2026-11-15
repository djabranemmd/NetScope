
from fastapi import APIRouter, Query

from app.services.traffic_history import traffic_history


router = APIRouter(
    prefix="/history",
    tags=["Traffic History"],
)


@router.get("/")
async def get_traffic_history(
    limit: int = Query(
        default=60,
        ge=1,
        le=3600,
        description="Number of historical samples to return.",
    ),
):
    samples = traffic_history.get_history(
        limit=limit,
    )

    return {
        "message": "Traffic history retrieved successfully.",
        "collector": traffic_history.get_status(),
        "returned_samples": len(samples),
        "samples": samples,
    }
