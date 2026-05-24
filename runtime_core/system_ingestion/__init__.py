"""
System ingestion package

Version: 7.0.0
Architecture: LOCKED at v5.90.2
"""
from .component_extractor import extract_component_graph
from .intake_graph import build_system_intake_graph

__all__ = ["build_system_intake_graph", "extract_component_graph"]
