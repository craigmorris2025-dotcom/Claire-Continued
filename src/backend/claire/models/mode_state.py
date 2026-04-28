from dataclasses import dataclass

@dataclass
class ModeState:
    mode: str
    isolation_level: str
    safety_lock: bool
