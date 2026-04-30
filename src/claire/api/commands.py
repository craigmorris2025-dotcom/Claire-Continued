from fastapi import APIRouter
from ..claire.orchestrator.pipeline import ClairePipeline

router = APIRouter()
pipeline = ClairePipeline()

@router.post("/command")
def command_interface(payload: dict):
    """
    Receives search bar input and routes it into the Claire pipeline.
    """
    user_input = payload.get("query", "")
    return pipeline.run({"command": user_input})

# Update commands
elif command in ["update", "install update", "run update"]:
    return updater.install_update(payload.get("package"))

elif command in ["check updates", "check for updates"]:
    return updater.check_for_updates()
