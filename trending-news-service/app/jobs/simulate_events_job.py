import argparse

from app.db.session import SessionLocal
from app.services.events.event_simulator_service import EventSimulatorService


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate user events for demo data.")
    parser.add_argument("--count", type=int, default=100, help="Number of events to simulate")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        service = EventSimulatorService(db)
        result = service.simulate(count=args.count)
        print(result.model_dump_json(indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
