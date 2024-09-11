import re

CLEAN_NAME_RE = re.compile(r"^\d+\s*/\s*")


def clean_scout_name(name: str) -> str:
    return re.sub(CLEAN_NAME_RE, "", name)
