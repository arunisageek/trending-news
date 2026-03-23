from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.event import EventCreate, EventCreateResponse, EventSimulationResponse
from app.services.events.event_ingestion_service import EventIngestionService
from app.services.events.event_simulator_service import EventSimulatorService

router = APIRouter(tags=["events"])
settings = get_settings()


@router.post("/events", response_model=EventCreateResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventCreateResponse:
    service = EventIngestionService(db)
    event = service.ingest_event(payload)
    return EventCreateResponse.model_validate(event)


@router.post("/events/simulate", response_model=EventSimulationResponse)
def simulate_events(
    count: int = Query(default=100, ge=1, le=10000),
    db: Session = Depends(get_db),
) -> EventSimulationResponse:
    simulator = EventSimulatorService(db)
    result = simulator.simulate(count=count)
    return result
