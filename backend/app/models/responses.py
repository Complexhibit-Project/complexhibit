from typing import Any, Dict, Optional

from pydantic import BaseModel


class StandardResponseModel(BaseModel):
    success: str = "True"
    data: Dict[str, Any]
    message: str


class ErrorResponseModel(BaseModel):
    success: str = "False"
    error_code: str
    error_message: str
    error_details: Dict[str, Any]
