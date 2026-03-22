"""Content extraction tools for the reduced leave form."""
from datetime import date, datetime, time
import re
from typing import Any, Dict, List, Optional


class ContentExtractor:
    """Extract and parse form field values from user input."""

    @staticmethod
    def _parse_date_token(token: str) -> Optional[date]:
        """Parse a date token using supported formats."""
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(token, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_time_token(token: str) -> Optional[time]:
        """Parse a time token using supported formats."""
        normalized = re.sub(r'\s+', ' ', token.strip().upper())
        formats = ["%H:%M", "%I:%M %p", "%I %p"]
        for fmt in formats:
            try:
                return datetime.strptime(normalized, fmt).time()
            except ValueError:
                continue
        return None

    @staticmethod
    def extract_dates(text: str) -> List[date]:
        """Extract all date values from text in order."""
        matches = re.findall(r'\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b', text)
        parsed_dates: List[date] = []
        for token in matches:
            parsed = ContentExtractor._parse_date_token(token)
            if parsed:
                parsed_dates.append(parsed)
        return parsed_dates

    @staticmethod
    def extract_times(text: str) -> List[time]:
        """Extract all time values from text in order."""
        matches = re.findall(r'\b(?:[01]?\d|2[0-3]):[0-5]\d\s?(?:AM|PM)?\b|\b(?:1[0-2]|[1-9])\s?(?:AM|PM)\b', text, re.IGNORECASE)
        parsed_times: List[time] = []
        for token in matches:
            parsed = ContentExtractor._parse_time_token(token)
            if parsed:
                parsed_times.append(parsed)
        return parsed_times

    @staticmethod
    def extract_date(text: str) -> Optional[date]:
        """Extract the first date from text."""
        dates = ContentExtractor.extract_dates(text)
        return dates[0] if dates else None

    @staticmethod
    def extract_time(text: str) -> Optional[time]:
        """Extract the first time from text."""
        times = ContentExtractor.extract_times(text)
        return times[0] if times else None

    @staticmethod
    def extract_leave_type(text: str) -> Optional[str]:
        """Extract leave type from text."""
        # Ordered most-specific first to avoid partial matches
        leave_types = {
            'extended_maternity': r'\b(extended\s+maternity\s+leave)\b',
            'adoption_8_weeks': r'\b(adoption\s+leave\s+8\s*weeks?|8[\s-]?week\s+adoption)\b',
            'adoption_4_weeks': r'\b(adoption\s+leave\s+4\s*weeks?|4[\s-]?week\s+adoption)\b',
            'sick_leave_no_medical_certificate': r'\b(sick\s+leave\s+no\s+(?:medical\s+)?cert(?:ificate)?|sick\s+no\s+mc)\b',
            'unpaid_infant_care': r'\b(unpaid\s+infant\s+care\s+leave|uicl)\b',
            'unpaid_medical': r'\b(unpaid\s+medical\s+leave)\b',
            'unpaid_maternity': r'\b(unpaid\s+maternity\s+leave)\b',
            'unpaid_leave': r'\b(unpaid\s+leave|leave\s+without\s+pay)\b',
            'unpaid_hours': r'\b(unpaid\s+hours?)\b',
            'shared_parental': r'\b(shared\s+parental\s+leave|spl)\b',
            'national_service': r'\b(national\s+service\s+leave|ns\s+leave)\b',
            'hospitalisation': r'\b(hospitalisation\s+leave|hospitalization\s+leave)\b',
            'family_care': r'\b(family[\s_-]?care\s+leave)\b',
            'child_care': r'\b(child[\s_-]?care\s+leave)\b',
            'compassionate': r'\b(compassionate\s+leave|bereavement\s+leave)\b',
            'annual': r'\b(annual\s+leave|yearly\s+leave)\b',
            'exam': r'\b(exam\s+leave|examination\s+leave|study\s+leave)\b',
            'medical': r'\b(medical\s+leave|sick\s+leave)\b',
            'maternity': r'\b(maternity\s+leave)\b',
            'paternity': r'\b(paternity\s+leave)\b',
            'marriage': r'\b(marriage\s+leave|wedding\s+leave)\b',
            'special': r'\b(special\s+leave)\b',
            'time_off': r'\b(time[\s_-]?off)\b',
        }

        for leave_type, pattern in leave_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return leave_type
        return None

    @staticmethod
    def extract_full_day_leave(text: str) -> Optional[bool]:
        """Detect if the user specified full-day leave."""
        if re.search(r'\b(full[\s_-]?day\s+leave|full[\s_-]?day)\b', text, re.IGNORECASE):
            return True
        return None

    @staticmethod
    def extract_half_day_leave(text: str) -> Optional[bool]:
        """Detect if the user specified half-day leave."""
        if re.search(r'\b(half[\s_-]?day\s+leave|half[\s_-]?day)\b', text, re.IGNORECASE):
            return True
        return None

    @staticmethod
    def parse_form_text(text: str) -> Dict[str, Any]:
        """Parse the reduced form fields from user input."""
        extracted = {}
        extracted['leave_type'] = ContentExtractor.extract_leave_type(text)

        dates = ContentExtractor.extract_dates(text)
        if dates:
            extracted['start_date'] = dates[0]
        if len(dates) >= 2:
            extracted['end_date'] = dates[1]

        times = ContentExtractor.extract_times(text)
        if times:
            extracted['start_time'] = times[0]
        if len(times) >= 2:
            extracted['end_time'] = times[1]

        extracted['full_day_leave'] = ContentExtractor.extract_full_day_leave(text)
        extracted['half_day_leave'] = ContentExtractor.extract_half_day_leave(text)

        return {k: v for k, v in extracted.items() if v is not None}
