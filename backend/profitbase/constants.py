from properties.constants import PropertyStatus, PropertyType

CONVERT_STATUS_MAP = {
    "UNAVAILABLE": PropertyStatus.UNAVAILABLE,
    "AVAILABLE": PropertyStatus.FREE,
    "BOOKED": PropertyStatus.BOOKED,
    "EXECUTION": PropertyStatus.SOLD,
    "SOLD": PropertyStatus.SOLD,
}

CONVERT_TYPE_MAP = {
    "property": PropertyType.FLAT,
    "apartment": PropertyType.COMMERCIAL_APARTMENT,
    "parking": PropertyType.PARKING,
    "office": PropertyType.COMMERCIAL,
    "pantry": PropertyType.PANTRY,
    "storage": PropertyType.PANTRY,
    "commercial_premises": PropertyType.COMMERCIAL,
    "free_destination": PropertyType.FLAT,
}

NEGATIVE_VALUES = {"нет", None}
POSITIVE_VALUES = {"Да", "да"}
