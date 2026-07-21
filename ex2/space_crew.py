from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field  # type: ignore
from pydantic import ValidationError, model_validator  # type: ignore


class Rank(str, Enum):
    """
    Enum representing allowed crew ranks.
    """
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    """
    Model representing an individual crew member.
    """
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    """
    Model representing a space mission with nested crew members
    and mission-wide safety validation rules.
    """
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_safety(self) -> "SpaceMission":
        """
        Validates safety requirements across the entire mission and crew.
        """
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        has_leadership = any(
            member.rank in (Rank.commander, Rank.captain)
            for member in self.crew
        )
        if not has_leadership:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced_count = sum(
                1 for member in self.crew if member.years_experience >= 5
            )
            required_count = len(self.crew) / 2.0
            if experienced_count < required_count:
                raise ValueError(
                    "Long missions (> 365 days) need 50% experienced crew "
                    "(5+ years)"
                )

        if any(not member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")

        return self


def main() -> None:
    """
    Demonstrates successful nested model validation and failure handling.
    """
    print("Space Mission Crew Validation")
    print("=========================================")

    try:
        cmd_date = datetime.fromisoformat("2026-07-21T08:00:00")
        crew_list = [
            CrewMember(
                member_id="CM001",
                name="Sarah Connor",
                rank=Rank.commander,
                age=42,
                specialization="Mission Command",
                years_experience=12,
                is_active=True
            ),
            CrewMember(
                member_id="CM002",
                name="John Smith",
                rank=Rank.lieutenant,
                age=30,
                specialization="Navigation",
                years_experience=6,
                is_active=True
            ),
            CrewMember(
                member_id="CM003",
                name="Alice Johnson",
                rank=Rank.officer,
                age=28,
                specialization="Engineering",
                years_experience=5,
                is_active=True
            )
        ]

        valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=cmd_date,
            duration_days=900,
            crew=crew_list,
            budget_millions=2500.0
        )

        print("Valid mission created:")
        print(f"Mission: {valid_mission.mission_name}")
        print(f"ID: {valid_mission.mission_id}")
        print(f"Destination: {valid_mission.destination}")
        print(f"Duration: {valid_mission.duration_days} days")
        print(f"Budget: ${valid_mission.budget_millions}M")
        print(f"Crew size: {len(valid_mission.crew)}")
        print("Crew members:")
        for member in valid_mission.crew:
            print(
                f"- {member.name} ({member.rank.value}) - "
                f"{member.specialization}"
            )

    except ValidationError as e:
        print(f"Unexpected Validation Error: {e}")

    print("\n=========================================")

    try:
        invalid_crew = [
            CrewMember(
                member_id="CM004",
                name="Bob Builder",
                rank=Rank.officer,
                age=25,
                specialization="Construction",
                years_experience=2
            )
        ]

        SpaceMission(
            mission_id="M2024_LUNA",
            mission_name="Moon Base Alpha",
            destination="Moon",
            launch_date=datetime.now(),
            duration_days=100,
            crew=invalid_crew,
            budget_millions=500.0
        )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
