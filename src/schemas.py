import uuid
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "PENDING"
    started = "STARTED"
    retry = "RETRY"
    failure = "FAILURE"
    success = "SUCCESS"


class ModerationRequestResponse(BaseModel):
    task_id: str
    created_at: str


class DataItem(BaseModel):
    label: str
    score: float


class TaskResult(BaseModel):
    data: List[DataItem]
    summary: str
    updated_at: datetime


class ModerationResultResponse(BaseModel):
    task_id: str
    task_status: TaskStatus
    task_result: TaskResult


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
