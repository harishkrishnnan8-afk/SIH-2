import hashlib
import re
from typing import Optional


def mask_apaar(apaar_str: Optional[str]) -> str:
    """Mask an APAAR identifier, revealing only the last 4 digits."""
    if not apaar_str:
        return "•••• •••• ••••"
    digits = re.sub(r"\D", "", str(apaar_str))
    if len(digits) < 4:
        return "•••• •••• ••••"
    return f"•••• •••• {digits[-4:]}"


def hash_apaar(apaar_str: str, salt: str = "sih26263_apaar_salt_") -> str:
    """Deterministic hash of clean 12-digit APAAR for duplicate detection without leaking plaintext."""
    digits = re.sub(r"\D", "", str(apaar_str))
    return hashlib.sha256(f"{salt}{digits}".encode("utf-8")).hexdigest()


def sanitize_csv_cell(value: object) -> str:
    """
    Sanitize cell value to prevent CSV Formula Injection (CWE-1236).
    Prepends a single quote if string begins with =, +, -, @, \\t, \\r.
    """
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{text}"
    return text
