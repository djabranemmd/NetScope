
from fastapi import APIRouter, HTTPException, Query

from app.services.traffic_analytics import get_traffic_analytics


router = APIRouter(
    prefix="/analytics",
    tags=["Traffic Analytics"],
)


@router.get("/")
async def get_analytics(
    window_seconds: int = Query(
        default=10,
        ge=1,
        le=60,
        description="Traffic measurement window in seconds.",
    ),
    top_limit: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of top IP addresses.",
    ),
):
    """
    Return analytics calculated from real captured packets.
    """

    try:
        return {
            "message": "Traffic analytics retrieved successfully.",
            "data": get_traffic_analytics(
                window_seconds=window_seconds,
                top_limit=top_limit,
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Traffic analytics failed: {str(error)}",
        )
