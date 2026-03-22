"""
Leave Form Assistant - Project Configuration
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Configuration
CONFIG = {
    "project_name": "Leave Form Assistant",
    "version": "1.0.0",
    "description": "CrewAI-based leave form fulfillment assistant",
    
    # Leave configuration
    "leave_types": [
        "Sick Leave",
        "Casual Leave",
        "Earned Leave",
        "Maternity Leave",
        "Paternity Leave",
        "Unpaid Leave",
        "Bereavement Leave"
    ],
    
    # Validation rules
    "validation": {
        "max_leave_days": 60,
        "approval_threshold_days": 30,  # Days beyond which manager approval required
    },
    
    # Form fields
    "required_fields": [
        "leave_type",
        "start_date",
        "start_time",
        "end_date",
        "end_time"
    ],
    
    "optional_fields": [
        "validation_errors"
    ],
    
    # LLM Configuration
    "llm": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048
    }
}

# Get configuration value
def get_config(key, default=None):
    """Get configuration value by key"""
    keys = key.split('.')
    value = CONFIG
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default
