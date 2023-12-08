from pydantic import BaseModel, Field


class BookingPropertyData(BaseModel):
    id: int
    property_global_id: str

    def __repr__(self):
        return f"\n\t\t\tBooking: id={self.id}, property_global_id={self.property_global_id}"


class PropertyDecodedData(BaseModel):
    global_id: str
    type: str
    is_correct_type: bool
    bookings: list[BookingPropertyData] = Field(default=[])

    def __repr__(self):
        return (
            f"\n\t\tProperty: global_id={self.global_id}, type={self.type=}, "
            f"is_correct_type={self.is_correct_type}, bookings={self.bookings}"
        )


class PropertyIdData(BaseModel, frozen=True):
    id: int

    def __repr__(self):
        return f"\n\tProfit: id={self.id}"
