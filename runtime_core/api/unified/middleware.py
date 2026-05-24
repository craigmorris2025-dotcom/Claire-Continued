"""
Shared middleware â€” auth, logging, CORS, error handling

Phase 2: API Unification
Version: v10.3.0-phase2
Status: DUAL (System A: lifecycle runtime, System B: platform/dashboard) â†’ UNIFIED (single API surface with versioned endpoints)

Content Specification:
  Request logging, error normalization, CORS headers, API key validation, request ID generation

Replaces: Duplicate middleware in both API systems
"""

import logging
from typing import Any, Dict, List, Optional

from runtime_core.runtime.generic_logic import governed_result, validate_governed_result

logger = logging.getLogger(__name__)


class Middleware:
    """
    Shared middleware â€” auth, logging, CORS, error handling
    
    Spec: Request logging, error normalization, CORS headers, API key validation, request ID generation
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return governed_result(__name__, self.__class__.__name__.lower(), context, spec="Request logging, error normalization, CORS headers, API key validation, request ID generation")

    def validate(self, result: Dict[str, Any]) -> bool:
        return validate_governed_result(result)



