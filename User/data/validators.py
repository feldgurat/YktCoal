import re


def normalize_phone(raw: str) -> str:
    """
    Приводит телефон к каноническому виду +7XXXXXXXXXX.
    """
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    if not digits.startswith("7") or len(digits) != 11:
        raise ValueError("Некорректный номер телефона")
    return f"+{digits}"