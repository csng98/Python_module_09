from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field  # type: ignore
from pydantic import ValidationError, model_validator  # type: ignore


class ContactType(str, Enum):
    """
    Enum representing the allowed types of alien contact.
    """
    radio = "radio"
    visual = "visual"
    physical = "physical"
    telepathic = "telepathic"


class AlienContact(BaseModel):
    """
    Pydantic model representing an Alien Contact Log with
    complex custom business rules validation.
    """
    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_business_rules(self) -> "AlienContact":
        """
        Validates complex multi-field business rules after default
        field-level validations are complete.
        """
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")

        if self.contact_type == ContactType.physical and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        if (
            self.contact_type == ContactType.telepathic
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
                )

        if self.signal_strength > 7.0:
            if not self.message_received or not self.message_received.strip():
                raise ValueError(
                    "Strong signals (> 7.0) should include received messages"
                )

        return self


def main() -> None:
    """
    Demonstrates successful custom validation and handles validation failure.
    """
    print("Alien Contact Log Validation")
    print("======================================")

    try:
        contact_date = datetime.fromisoformat("2026-07-16T18:00:00")
        valid_contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp=contact_date,
            location="Area 51, Nevada",
            contact_type=ContactType.radio,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli",
            is_verified=True
        )
        print("Valid contact report:")
        print(f"ID: {valid_contact.contact_id}")
        print(f"Type: {valid_contact.contact_type.value}")
        print(f"Location: {valid_contact.location}")
        print(f"Signal: {valid_contact.signal_strength}/10")
        print(f"Duration: {valid_contact.duration_minutes} minutes")
        print(f"Witnesses: {valid_contact.witness_count}")
        print(f"Message: '{valid_contact.message_received}'")

    except ValidationError as e:
        print(f"Unexpected Validation Error: {e}")

    print("\n======================================")

    try:
        contact_date = datetime.now()
        AlienContact(
            contact_id="AC_2024_002",
            timestamp=contact_date,
            location="Roswell, New Mexico",
            contact_type=ContactType.telepathic,
            signal_strength=4.0,
            duration_minutes=10,
            witness_count=1,
            is_verified=False
        )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
