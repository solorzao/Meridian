import uuid


def get_current_user_id() -> uuid.UUID:
    """Hardcoded user ID for development. Replace with real auth later."""
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


def get_current_user_id_string() -> str:
    return "00000000-0000-0000-0000-000000000001"
