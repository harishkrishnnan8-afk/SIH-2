from datetime import datetime, timezone
import re
from typing import Any, Optional
from backend.app.core.masking import mask_apaar
from backend.app.verification.adapter import VerificationProvider, VerificationResponse

SIMULATION_DISCLAIMER = "SIMULATED — NOT OFFICIAL APAAR VERIFICATION"


class MockVerificationProvider(VerificationProvider):
    """
    Deterministic simulated provider for local testing and demonstration.
    Separates verification business logic from any external provider.
    Explicitly tags all responses as simulated.
    """

    def verify(self, clean_apaar: str, internal_student: Optional[Any] = None) -> VerificationResponse:
        digits = re.sub(r"\D", "", clean_apaar or "")
        format_valid = len(digits) == 12
        internal_match = internal_student is not None
        now_iso = datetime.now(timezone.utc).isoformat()

        student_data = None
        if internal_student:
            student_data = {
                "id": internal_student.id,
                "name": internal_student.name,
                "programme": internal_student.programme if hasattr(internal_student, "programme") else None,
                "category": internal_student.category if hasattr(internal_student, "category") else None,
                "status": internal_student.status,
                "dob": internal_student.dob,
                "gender": internal_student.gender,
                "masked_apaar": internal_student.masked_apaar,
            }

        return VerificationResponse(
            mode="simulated",
            format_valid=format_valid,
            internal_match=internal_match,
            provider_status="Mock provider",
            is_simulated=True,
            simulation_label=SIMULATION_DISCLAIMER,
            checked_at=now_iso,
            student_details=student_data,
            message="Mock response. Not connected to live AICTE/DigiLocker/APAAR gateway.",
        )


def get_verification_provider() -> VerificationProvider:
    """Factory returning the active verification provider."""
    # Production gateway would check credentials here; fallback to deterministic mock
    return MockVerificationProvider()
