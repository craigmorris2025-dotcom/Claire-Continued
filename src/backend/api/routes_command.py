from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CommandRequest(BaseModel):
    query: str

@router.post("/command")
async def command_endpoint(payload: CommandRequest):
    query = payload.query.strip()

    if query.lower().startswith("check updates"):
        return {"action": "check_updates", "status": "routed"}

    if query.lower().startswith("install update"):
        return {"action": "install_update", "status": "routed"}

    return {
        "action": "analyze",
        "query": query,
        "status": "received"
    }
