"""
Validation Tools for Leave Form
"""
from datetime import datetime
from typing import Tuple, List, Dict, Any
from email_validator import validate_email, EmailNotValidError
import re


class LeaveFormValidator:
    """Validator for leave form inputs"""

    MAX_LEAVE_DAYS = 60
    MIN_REASON_LENGTH = 5
    MAX_REASON_LENGTH = 500

    @staticmethod
    def validate_employee_id(employee_id: str) -> Tuple[bool, str]:
        """Validate employee ID format"""
        if not employee_id or len(employee_id.strip()) == 0:
            return False, "Employee ID cannot be empty"
        if len(employee_id) > 20:
            return False, "Employee ID must be maximum 20 characters"
        if not re.match(r'^[A-Z0-9\-]{2,}$', employee_id.strip()):
            return False, "Employee ID format invalid (use uppercase letters, numbers, or hyphens)"
        return True, ""

    @staticmethod
    def validate_employee_name(name: str) -> Tuple[bool, str]:
        """Validate employee name"""
        if not name or len(name.strip()) < 2:
            return False, "Employee name must be at least 2 characters"
        if len(name) > 100:
            return False, "Employee name must be maximum 100 characters"
        if not re.match(r'^[a-zA-Z\s\-\'\.]{2,}$', name.strip()):
            return False, "Employee name contains invalid characters"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email or len(email.strip()) == 0:
            return False, "Email cannot be empty"
        try:
            validate_email(email.strip())
            return True, ""
        except EmailNotValidError as e:
            return False, f"Invalid email format: {str(e)}"

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        if not phone or len(phone.strip()) == 0:
            return True, ""  # Phone is optional
        phone = phone.strip()
        if not re.match(r'^\+?1?\d{9,15}$', phone.replace('-', '').replace(' ', '')):
            return False, "Phone number format invalid (expected format: +1234567890)"
        return True, ""

    @staticmethod
    def validate_dates(start_date: datetime, end_date: datetime) -> Tuple[bool, List[str]]:
        """Validate date range"""
        errors = []

        if start_date >= end_date:
            errors.append("End date must be after start date")
            return False, errors

        if start_date < datetime.now():
            errors.append("Start date must be in the future")
            return False, errors

        # Calculate days
        days = (end_date - start_date).days + 1
        if days > LeaveFormValidator.MAX_LEAVE_DAYS:
            errors.append(f"Leave period cannot exceed {LeaveFormValidator.MAX_LEAVE_DAYS} days")
            return False, errors

        if days > 30:
            errors.append("⚠️ Warning: Leave period exceeds 30 days. Manager approval required.")

        return True, errors

    @staticmethod
    def validate_reason(reason: str) -> Tuple[bool, str]:
        """Validate leave reason"""
        if not reason or len(reason.strip()) < LeaveFormValidator.MIN_REASON_LENGTH:
            return False, f"Reason must be at least {LeaveFormValidator.MIN_REASON_LENGTH} characters"
        if len(reason) > LeaveFormValidator.MAX_REASON_LENGTH:
            return False, f"Reason must be maximum {LeaveFormValidator.MAX_REASON_LENGTH} characters"
        return True, ""

    @staticmethod
    def validate_manager_name(name: str) -> Tuple[bool, str]:
        """Validate manager name"""
        if not name or len(name.strip()) < 2:
            return False, "Manager name must be at least 2 characters"
        if len(name) > 100:
            return False, "Manager name must be maximum 100 characters"
        if not re.match(r'^[a-zA-Z\s\-\'\.]{2,}$', name.strip()):
            return False, "Manager name contains invalid characters"
        return True, ""

    @staticmethod
    def validate_department(department: str) -> Tuple[bool, str]:
        """Validate department"""
        valid_departments = ["Engineering", "Sales", "HR", "Finance", "Marketing", "Operations", "Other"]
        if not department or department.strip() not in valid_departments:
            return False, f"Invalid department. Choose from: {', '.join(valid_departments)}"
        return True, ""

    @staticmethod
    def validate_all_fields(form_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate all form fields and return errors and warnings"""
        errors = []
        warnings = []

        # Validate employee ID
        is_valid, error = LeaveFormValidator.validate_employee_id(form_data.get('employee_id', ''))
        if not is_valid:
            errors.append(error)

        # Validate employee name
        is_valid, error = LeaveFormValidator.validate_employee_name(form_data.get('employee_name', ''))
        if not is_valid:
            errors.append(error)

        # Validate department
        is_valid, error = LeaveFormValidator.validate_department(form_data.get('department', ''))
        if not is_valid:
            errors.append(error)

        # Validate email
        is_valid, error = LeaveFormValidator.validate_email(form_data.get('contact_email', ''))
        if not is_valid:
            errors.append(error)

        # Validate phone if provided
        if form_data.get('contact_phone'):
            is_valid, error = LeaveFormValidator.validate_phone(form_data.get('contact_phone', ''))
            if not is_valid:
                errors.append(error)

        # Validate reason
        is_valid, error = LeaveFormValidator.validate_reason(form_data.get('reason', ''))
        if not is_valid:
            errors.append(error)

        # Validate manager name
        is_valid, error = LeaveFormValidator.validate_manager_name(form_data.get('manager_name', ''))
        if not is_valid:
            errors.append(error)

        # Validate dates
        if 'start_date' in form_data and 'end_date' in form_data:
            is_valid, date_errors = LeaveFormValidator.validate_dates(
                form_data['start_date'], form_data['end_date']
            )
            if not is_valid:
                errors.extend(date_errors)
            else:
                # Warnings are part of date errors
                warnings.extend([e for e in date_errors if "Warning" in e])

        return len(errors) == 0, errors, warnings
