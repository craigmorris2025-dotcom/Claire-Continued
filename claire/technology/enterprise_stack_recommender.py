"""
Recommends enterprise technology stacks
=======================================
ACS2-Claire / Syntalion

Module: src.claire.technology.enterprise_stack_recommender
Role: Recommends enterprise technology stacks
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EnterpriseStackRecommender:
    """
    Recommends enterprise technology stacks

    Writes recommendations to data/technology/stack_recommendations/..
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")

    def recommend_stack(requirements):
        """Returns StackRecommendation."""
        raise NotImplementedError

    def evaluate_stack_fit(stack:
        """Returns Any."""
        raise NotImplementedError

    def requirements):
        """Returns FitScore."""
        raise NotImplementedError

    def compare_stacks(stack_a:
        """Returns Any."""
        raise NotImplementedError

    def stack_b):
        """Returns StackComparison."""
        raise NotImplementedError

    def assess_migration_path(current:
        """Returns Any."""
        raise NotImplementedError

    def target):
        """Returns MigrationPlan."""
        raise NotImplementedError

    def compute_tco(stack:
        """Returns Any."""
        raise NotImplementedError

    def horizon_years):
        """Returns TCOEstimate."""
        raise NotImplementedError

    def export_recommendation(rec):
        """Returns dict."""
        raise NotImplementedError

