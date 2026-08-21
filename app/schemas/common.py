from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    status_code: int
    status: bool
    message: str
    data: T
