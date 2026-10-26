from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VerificationResponse:
    mode: str  # "format", "internal", "simulated", "external"
    format_valid: bool
    internal_match: bool
    provider_status: str  # "Mock provider", "Online", "Unavailable", "Error"
    is_simulated: bool
    simulation_label: str
    checked_at: str
    student_details: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class VerificationProvider(ABC):
    @abstractmethod
    def verify(self, clean_apaar: str, internal_student: Optional[Any] = None) -> VerificationResponse:
        pass
