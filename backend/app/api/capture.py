
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.packet_capture import capture_engine
from app.services.traffic_history import traffic_history


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
        capture_data = capture_engine.start(request.interface)

        history_data = traffic_history.start()

        return {
            "message": "Packet capture and traffic history started successfully.",
            "data": {
                "capture": capture_data,
                "history": history_data,
            },
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
        history_data = traffic_history.stop()

        capture_data = capture_engine.stop()

        return {
            "message": "Packet capture and traffic history stopped.",
            "data": {
                "capture": capture_data,
                "history": history_data,
            },
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/status")
async def get_capture_status():
    return {
        "capture": capture_engine.get_status(),
        "history": traffic_history.get_status(),
    }


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
