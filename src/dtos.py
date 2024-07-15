from pydantic import BaseModel


class ModerationResponse(BaseModel):
    task_id: str
    created_at: str
