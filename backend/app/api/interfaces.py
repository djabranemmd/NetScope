
from fastapi import APIRouter, HTTPException

from app.services.interface_discovery import discover_interfaces


router = APIRouter(
    prefix="/interfaces",
    tags=["Network Interfaces"],
)


@router.get("/")
async def get_network_interfaces():
    try:
        return discover_interfaces()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Interface discovery failed: {str(error)}",
        )
