"""Leave request data models."""
from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class LeaveType(str, Enum):
    """Types of leave available."""
    annual = "annual"
    child_care = "child_care"
    compassionate = "compassionate"
    exam = "exam"
    family_care = "family_care"
    hospitalisation = "hospitalisation"
    medical = "medical"
    national_service = "national_service"
    maternity = "maternity"
    extended_maternity = "extended_maternity"
    shared_parental = "shared_parental"
    paternity = "paternity"
    adoption_4_weeks = "adoption_4_weeks"
    adoption_8_weeks = "adoption_8_weeks"
    sick_leave_no_medical_certificate = "sick_leave_no_medical_certificate"
    special = "special"
    time_off = "time_off"
    unpaid_infant_care = "unpaid_infant_care"
    unpaid_medical = "unpaid_medical"
    unpaid_maternity = "unpaid_maternity"
    marriage = "marriage"
    unpaid_leave = "unpaid_leave"
    unpaid_hours = "unpaid_hours"


class LeaveStatus(str, Enum):
    """Status of leave request"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class LeaveRequest(BaseModel):
    """Minimal leave request form model."""
    leave_type: LeaveType = Field(..., description="Type of leave")
    start_date: date = Field(..., description="Start date of leave")
    start_time: time = Field(..., description="Start time of leave")
    end_date: date = Field(..., description="End date of leave")
    end_time: time = Field(..., description="End time of leave")
    full_day_leave: Optional[bool] = Field(None, description="True if the leave covers full days")
    half_day_leave: Optional[bool] = Field(None, description="True if the leave covers only a half day")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING, description="Status of request")
    created_at: datetime = Field(default_factory=datetime.now)
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors if any")

    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate start date is not in the past."""
        if v < datetime.now().date():
            raise ValueError("Start date cannot be in the past")
        return v

    @validator('end_time')
    def validate_date_time_range(cls, v, values):
        """Validate end date/time is after start date/time."""
        start_date = values.get('start_date')
        start_time = values.get('start_time')
        end_date = values.get('end_date')

        if start_date and start_time and end_date:
            start_at = datetime.combine(start_date, start_time)
            end_at = datetime.combine(end_date, v)
            if start_at <= datetime.now():
                raise ValueError("Start date and time must be in the future")
            if end_at <= start_at:
                raise ValueError("End date and time must be after start date and time")
        return v

    @validator('half_day_leave')
    def validate_day_leave_exclusive(cls, v, values):
        """Ensure FullDayLeave and HalfDayLeave are not both True."""
        if v and values.get('full_day_leave'):
            raise ValueError("FullDayLeave and HalfDayLeave cannot both be True")
        return v


class ValidationResult(BaseModel):
    """Result of validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processed_at: datetime = Field(default_factory=datetime.now)


class FormResponse(BaseModel):
    """Response containing form data and status"""
    leave_request: Optional[LeaveRequest] = None
    validation_result: ValidationResult
    completion_percentage: float = Field(default=0.0)
    next_step: str = Field(default="")
    user_message: str = Field(default="")
