from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    data: DataT


class ErrorDetail(BaseModel):
    field: str
    message: str
    type: str


class ApiError(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    error: ApiError
    request_id: str
