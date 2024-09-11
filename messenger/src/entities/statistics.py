from pydantic import BaseModel


class TicketStatistics(BaseModel):
    solved_tickets_count: int
    returned_tickets_count: int
    avg_time_to_first_response: int
    avg_time_to_solve: int
