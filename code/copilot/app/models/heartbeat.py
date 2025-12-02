from pydantic import BaseModel


class HeartbeatResult(BaseModel):
    isAlive: bool
