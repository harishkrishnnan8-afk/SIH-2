from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleDefinition:
    code: str
    category: str
    severity: str  # "High", "Medium", "Low"
    message: str
    explanation: str
    next_steps: str


RULES = {
    "R-REQ-01": RuleDefinition(
        code="R-REQ-01",
        category="Missing attribute",
        severity="Medium",
        message="Student full name is required.",
        explanation="Student name was missing or empty in the record.",
        next_steps="Provide the full legal name of the student according to admission documents.",
    ),
    "R-REQ-02": RuleDefinition(
        code="R-REQ-02",
        category="Missing attribute",
        severity="High",
        message="Programme code is required and must correspond to an active institution programme.",
        explanation="Programme code was missing or not recognised.",
        next_steps="Select an approved programme code for this institution.",
    ),
    "R-REQ-04": RuleDefinition(
        code="R-REQ-04",
        category="Missing attribute",
        severity="Medium",
        message="Admission category is required for all admitted students.",
        explanation="Admission category field was empty in the uploaded row or registration form.",
        next_steps="Update the admission record with the correct category (e.g. General, Supernumerary, NRI, OCI, Foreign National).",
    ),
    "R-FMT-02": RuleDefinition(
        code="R-FMT-02",
        category="Identifier format",
        severity="Medium",
        message="APAAR identifier must contain exactly 12 digits.",
        explanation="Submitted identifier failed the 12-digit format check.",
        next_steps="Request a corrected APAAR identifier from the student or admissions office.",
    ),
    "R-DUP-01": RuleDefinition(
        code="R-DUP-01",
        category="Possible duplicate",
        severity="High",
        message="Two records share the same name and date of birth within one institution.",
        explanation="Name and date of birth match another active record in this programme.",
        next_steps="Compare both records with admission documents. A possible duplicate is not proof of fraud.",
    ),
    "R-DUP-02": RuleDefinition(
        code="R-DUP-02",
        category="Possible duplicate",
        severity="High",
        message="Two records share the same APAAR identifier within this institution.",
        explanation="The APAAR identifier matches another active student identity in the institution.",
        next_steps="Review original enrollment documents to verify whether multiple admissions were assigned to the same identity.",
    ),
    "R-DUP-03": RuleDefinition(
        code="R-DUP-03",
        category="Possible duplicate",
        severity="High",
        message="Identifier repeated within this file.",
        explanation="The same APAAR identifier appears multiple times in this upload batch.",
        next_steps="Deduplicate the CSV rows and verify individual admission entries.",
    ),
    "R-CROSS-01": RuleDefinition(
        code="R-CROSS-01",
        category="Possible duplicate",
        severity="High",
        message="Potential cross-institution match detected.",
        explanation="An active student record in another institution shares the same APAAR hash.",
        next_steps="Escalate to central reviewer for cross-institution admission verification. Do not automatically cancel.",
    ),
    "R-CAT-01": RuleDefinition(
        code="R-CAT-01",
        category="Category mismatch",
        severity="Medium",
        message="Category must be one of: General, Supernumerary, NRI, OCI, Foreign National.",
        explanation="The provided admission category does not match configured AICTE intake categories.",
        next_steps="Update category to an approved category.",
    ),
    "R-CAT-03": RuleDefinition(
        code="R-CAT-03",
        category="Category mismatch",
        severity="Medium",
        message="OCI status must be confirmed for OCI category admissions.",
        explanation="Record is marked OCI category but OCI status or card number is not confirmed.",
        next_steps="Request a correction or attach OCI confirmation.",
    ),
    "R-INT-01": RuleDefinition(
        code="R-INT-01",
        category="Intake exceeded",
        severity="High",
        message="Enrolment in a programme exceeds the configured approved intake.",
        explanation="Programme enrolment is above the configured approved intake value.",
        next_steps="Confirm whether supernumerary seats apply under the intake configuration.",
    ),
    "R-INT-WARN": RuleDefinition(
        code="R-INT-WARN",
        category="Intake capacity",
        severity="Low",
        message="Programme enrolment is approaching approved intake threshold.",
        explanation="Enrolment has reached or exceeded 95% of approved intake.",
        next_steps="Monitor remaining vacancies before completing subsequent admission rounds.",
    ),
}
