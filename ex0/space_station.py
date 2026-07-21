from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ValidationError  # type: ignore


class SpaceStation(BaseModel):
    """
    Pydantic model representing a Space Station with built-in data validation.
    """
    station_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    crew_size: int = Field(..., ge=1, le=20)
    power_level: float = Field(..., ge=0.0, le=100.0)
    oxygen_level: float = Field(..., ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = Field(default=True)
    notes: Optional[str] = Field(default=None, max_length=200)


def main() -> None:
    """
    Demonstrates successful validation and handles validation failure.
    """
    print("Space Station Data Validation")
    print("========================================")

    try:
        maintenance_date = datetime.fromisoformat("2026-07-16T17:45:00")
        valid_station = SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=6,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance=maintenance_date,
            is_operational=True,
            notes="Standard orbital parameters."
        )
        print("Valid station created:")
        print(f"ID: {valid_station.station_id}")
        print(f"Name: {valid_station.name}")
        print(f"Crew: {valid_station.crew_size} people")
        print(f"Power: {valid_station.power_level}%")
        print(f"Oxygen: {valid_station.oxygen_level}%")
        status = "Operational" if valid_station.is_operational else "Inactive"
        print(f"Status: {status}")

    except ValidationError as e:
        print(f"Unexpected Validation Error: {e}")

    print("\n========================================")

    try:
        SpaceStation(
            station_id="ISS002",
            name="Alpha Base",
            crew_size=25,
            power_level=95.0,
            oxygen_level=88.0,
            last_maintenance=datetime.now()
        )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
