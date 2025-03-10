"""
Agent for performing diagnoses, validated against Monarch KG - DEPRECATED

This module is maintained for backward compatibility.
Please use aurelian.agents.diagnosis.diagnosis_agent instead.
"""

from aurelian.agents.diagnosis.diagnosis_agent import diagnosis_agent
from aurelian.agents.diagnosis.diagnosis_config import DiagnosisDependencies, get_config
from aurelian.agents.diagnosis.diagnosis_gradio import chat
from aurelian.agents.diagnosis.diagnosis_tools import (
    find_disease_id,
    find_disease_phenotypes,
    search_web,
    retrieve_web_page,
    get_mondo_adapter,
)

__all__ = [
    "diagnosis_agent",
    "DiagnosisDependencies",
    "chat",
    "find_disease_id",
    "find_disease_phenotypes",
    "search_web",
    "retrieve_web_page",
    "get_mondo_adapter",
]