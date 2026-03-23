from app.services.events.event_simulator_service import EventSimulatorService


def test_simulator_creates_events(db_session) -> None:
    service = EventSimulatorService(db_session)
    result = service.simulate(count=10)
    assert result.created_count == 10
    assert len(result.buckets_touched) >= 1
