"""
Tasks module for Leave Form Assistant
"""

# To be used with CrewAI for defining task workflows
# Import agent classes as needed

from leave_form_assistant.agents import (
    IntentAgent,
    ExtractionAgent,
    ValidationAgent,
    ResponseAgent,
    ConfirmationAgent
)

__all__ = [
    'IntentAgent',
    'ExtractionAgent',
    'ValidationAgent',
    'ResponseAgent',
    'ConfirmationAgent'
]
