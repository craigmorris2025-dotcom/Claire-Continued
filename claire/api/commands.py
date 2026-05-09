from fastapi import APIRouter

from ..claire.orchestrator.pipeline import ClairePipeline

router = APIRouter()
pipeline = ClairePipeline()


@router.post("/command")
def command_interface(payload: dict):
    """
    Receives search bar input and routes it into the Claire pipeline.

    SAFETY:
    - Preserves existing command route behavior.
    - Does not add updater/install behavior here.
    - Updater commands must be added later through a validated route with
      explicit updater dependency wiring.
    """
    user_input = payload.get("query", "")
    return pipeline.run({"command": user_input})