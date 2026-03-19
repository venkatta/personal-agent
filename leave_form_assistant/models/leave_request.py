"""
Leave Request Data Models
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LeaveType(str, Enum):
    """Types of leave available"""
    SICK = "Sick Leave"
    CASUAL = "Casual Leave"
    EARNED = "Earned Leave"
    MATERNITY = "Maternity Leave"
    PATERNITY = "Paternity Leave"
    UNPAID = "Unpaid Leave"
    BEREAVEMENT = "Bereavement Leave"


class LeaveStatus(str, Enum):
    """Status of leave request"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class LeaveRequest(BaseModel):
    """Leave Request Form Model"""
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Employee Full Name")
    department: str = Field(..., description="Department")
    leave_type: LeaveType = Field(..., description="Type of leave")
    start_date: datetime = Field(..., description="Start date of leave")
    end_date: datetime = Field(..., description="End date of leave")
    reason: str = Field(..., description="Reason for leave")
    contact_email: str = Field(..., description="Contact email during leave")
    contact_phone: Optional[str] = Field(None, description="Contact phone during leave")
    manager_name: str = Field(..., description="Reporting Manager Name")
    cover_details: Optional[str] = Field(None, description="Coverage details during absence")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING, description="Status of request")
    created_at: datetime = Field(default_factory=datetime.now)
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors if any")

    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate start date is in future"""
        if v < datetime.now():
            raise ValueError("Start date must be in the future")
        return v

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v

    @validator('employee_id')
    def validate_employee_id(cls, v):
        """Validate employee ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Employee ID cannot be empty")
        return v.strip()

    @validator('employee_name')
    def validate_employee_name(cls, v):
        """Validate employee name"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Employee name must be at least 2 characters")
        return v.strip()

    @validator('reason')
    def validate_reason(cls, v):
        """Validate reason for leave"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Reason must be at least 5 characters")
        return v.strip()


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
