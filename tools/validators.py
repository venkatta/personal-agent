"""Validation tools for the reduced leave form."""
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple


class LeaveFormValidator:
    """Validator for leave form inputs."""

    MAX_LEAVE_DAYS = 60
    APPROVAL_THRESHOLD_DAYS = 30
    VALID_LEAVE_TYPES = {
        "annual",
        "child_care",
        "compassionate",
        "exam",
        "family_care",
        "hospitalisation",
        "medical",
        "national_service",
        "maternity",
        "extended_maternity",
        "shared_parental",
        "paternity",
        "adoption_4_weeks",
        "adoption_8_weeks",
        "sick_leave_no_medical_certificate",
        "special",
        "time_off",
        "unpaid_infant_care",
        "unpaid_medical",
        "unpaid_maternity",
        "marriage",
        "unpaid_leave",
        "unpaid_hours",
    }

    @staticmethod
    def _coerce_date(value: Any) -> Optional[date]:
        """Convert incoming value to a date when possible."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _coerce_time(value: Any) -> Optional[time]:
        """Convert incoming value to a time when possible."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.time()
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            normalized = " ".join(value.strip().upper().split())
            for fmt in ("%H:%M", "%I:%M %p", "%I %p"):
                try:
                    return datetime.strptime(normalized, fmt).time()
                except ValueError:
                    continue
        return None

    @staticmethod
    def validate_leave_type(leave_type: Any) -> Tuple[bool, str]:
        """Validate leave type."""
        if not leave_type:
            return False, "Leave type is required"
        if str(leave_type) not in LeaveFormValidator.VALID_LEAVE_TYPES:
            return False, "Leave type must be one of the configured leave types"
        return True, ""

    @staticmethod
    def validate_date(date_value: Any, label: str) -> Tuple[bool, str, Optional[date]]:
        """Validate a date field."""
        parsed = LeaveFormValidator._coerce_date(date_value)
        if parsed is None:
            return False, f"{label} must be a valid date", None
        return True, "", parsed

    @staticmethod
    def validate_time(time_value: Any, label: str) -> Tuple[bool, str, Optional[time]]:
        """Validate a time field."""
        parsed = LeaveFormValidator._coerce_time(time_value)
        if parsed is None:
            return False, f"{label} must be a valid time", None
        return True, "", parsed

    @staticmethod
    def validate_schedule(start_date: date, start_time: time, end_date: date, end_time: time) -> Tuple[bool, List[str], List[str]]:
        """Validate the requested leave window."""
        errors = []
        warnings = []

        start_at = datetime.combine(start_date, start_time)
        end_at = datetime.combine(end_date, end_time)

        if start_at <= datetime.now():
            errors.append("Start date and time must be in the future")
            return False, errors, warnings

        if end_at <= start_at:
            errors.append("End date and time must be after start date and time")
            return False, errors, warnings

        days = (end_at - start_at).total_seconds() / 86400
        if days > LeaveFormValidator.MAX_LEAVE_DAYS:
            errors.append(f"Leave period cannot exceed {LeaveFormValidator.MAX_LEAVE_DAYS} days")
            return False, errors, warnings

        if days > LeaveFormValidator.APPROVAL_THRESHOLD_DAYS:
            warnings.append("Warning: Leave period exceeds 30 days. Additional approval may be required.")

        return True, errors, warnings

    @staticmethod
    def validate_all_fields(form_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate all active form fields and return errors and warnings."""
        errors = []
        warnings = []

        is_valid, error = LeaveFormValidator.validate_leave_type(form_data.get('leave_type'))
        if not is_valid:
            errors.append(error)

        is_valid, error, start_date = LeaveFormValidator.validate_date(form_data.get('start_date'), 'Start date')
        if not is_valid:
            errors.append(error)

        is_valid, error, start_time = LeaveFormValidator.validate_time(form_data.get('start_time'), 'Start time')
        if not is_valid:
            errors.append(error)

        is_valid, error, end_date = LeaveFormValidator.validate_date(form_data.get('end_date'), 'End date')
        if not is_valid:
            errors.append(error)

        is_valid, error, end_time = LeaveFormValidator.validate_time(form_data.get('end_time'), 'End time')
        if not is_valid:
            errors.append(error)

        if not errors and all(value is not None for value in (start_date, start_time, end_date, end_time)):
            is_valid, schedule_errors, schedule_warnings = LeaveFormValidator.validate_schedule(
                start_date, start_time, end_date, end_time
            )
            if not is_valid:
                errors.extend(schedule_errors)
            warnings.extend(schedule_warnings)

        # FullDayLeave and HalfDayLeave are mutually exclusive
        if form_data.get('full_day_leave') and form_data.get('half_day_leave'):
            errors.append("FullDayLeave and HalfDayLeave cannot both be selected")

        return len(errors) == 0, errors, warnings
