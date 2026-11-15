
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.packet_capture import capture_engine


router = APIRouter(
    prefix="/capture",
    tags=["Packet Capture"],
)


class CaptureStartRequest(BaseModel):
    interface: str = Field(
        min_length=1,
        max_length=64,
    )


@router.post("/start")
async def start_capture(request: CaptureStartRequest):
    try:
        return {
            "message": "Packet capture started successfully.",
            "data": capture_engine.start(request.interface),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@router.post("/stop")
async def stop_capture():
    try:
        return {
            "message": "Packet capture stopped.",
            "data": capture_engine.stop(),
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/status")
async def get_capture_status():
    return capture_engine.get_status()


@router.get("/packets")
async def get_captured_packets(
    limit: int = Query(default=100, ge=1, le=500),
):
    status = capture_engine.get_status()

    packets = capture_engine.get_packets(limit=limit)

    return {
        "total_captured": status["stats"]["total_packets"],
        "returned_count": len(packets),
        "packets": packets,
    }
