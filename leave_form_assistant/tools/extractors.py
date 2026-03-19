"""
Content Extraction Tools for Leave Form
"""
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import re


class ContentExtractor:
    """Extract and parse form field values from user input"""

    @staticmethod
    def extract_employee_id(text: str) -> Optional[str]:
        """Extract employee ID from text"""
        patterns = [
            r'EMP-?\d{4,6}',  # EMP1234 or EMP-1234
            r'ID[:\s]+([A-Z0-9\-]+)',  # ID: EMP123
            r'employee\s+(?:id|number)[:\s]+([A-Z0-9\-]+)',  # employee id: EMP123
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if '(' in pattern else match.group(0)
        return None

    @staticmethod
    def extract_name(text: str) -> Optional[str]:
        """Extract person name from text"""
        # Simple name extraction - looks for capitalized words
        words = text.split()
        names = []
        for word in words:
            if word and word[0].isupper() and len(word) > 1:
                names.append(word)
            elif names:
                break
        return ' '.join(names) if names else None

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number from text"""
        patterns = [
            r'\+?1?\s?[-.]?\(?(\d{3})\)?[-.]?(\d{3})[-.]?(\d{4})',  # (123) 456-7890 or +1 123-456-7890
            r'\+\d{1,3}\s?\d{9,14}',  # International format
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        """Extract date from text"""
        date_patterns = [
            (r'(\d{4})[/-](\d{2})[/-](\d{2})', '%Y-%m-%d'),  # YYYY-MM-DD
            (r'(\d{2})[/-](\d{2})[/-](\d{4})', '%d-%m-%Y'),  # DD-MM-YYYY or MM-DD-YYYY
            (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', '%d %b %Y'),  # 15 Jan 2024
            (r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,]?\s+(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*', '%A %d %b'),  # Monday 15 Jan
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return datetime.strptime(match.group(0), fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def extract_leave_type(text: str) -> Optional[str]:
        """Extract leave type from text"""
        leave_types = {
            'sick': r'\b(sick\s+leave|medical\s+leave|health)\b',
            'casual': r'\b(casual\s+leave|casual|personal)\b',
            'earned': r'\b(earned\s+leave|annual\s+leave|vacation)\b',
            'maternity': r'\b(maternity\s+leave|maternity)\b',
            'paternity': r'\b(paternity\s+leave|paternity)\b',
            'unpaid': r'\b(unpaid\s+leave|leave\s+without\s+pay)\b',
            'bereavement': r'\b(bereavement\s+leave|compassionate\s+leave)\b',
        }

        for leave_type, pattern in leave_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                return leave_type.title()
        return None

    @staticmethod
    def extract_department(text: str) -> Optional[str]:
        """Extract department from text"""
        departments = ["Engineering", "Sales", "HR", "Finance", "Marketing", "Operations"]
        for dept in departments:
            if dept.lower() in text.lower():
                return dept
        return None

    @staticmethod
    def extract_reason(text: str, min_length: int = 10) -> Optional[str]:
        """Extract reason for leave from text"""
        # Look for text after common keywords
        keywords = ['reason', 'because', 'due to', 'for', 'purpose']
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]+([^.!?\n]{{10,}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                reason = match.group(1).strip()
                if len(reason) >= min_length:
                    return reason

        # If no keyword found, return first reasonable sentence
        sentences = re.split(r'[.!?\n]', text)
        for sentence in sentences:
            if len(sentence.strip()) >= min_length:
                return sentence.strip()
        return None

    @staticmethod
    def parse_form_text(text: str) -> Dict[str, Any]:
        """Parse complete form from user input text"""
        extracted = {}

        extracted['employee_id'] = ContentExtractor.extract_employee_id(text)
        extracted['employee_name'] = ContentExtractor.extract_name(text)
        extracted['contact_email'] = ContentExtractor.extract_email(text)
        extracted['contact_phone'] = ContentExtractor.extract_phone(text)
        extracted['leave_type'] = ContentExtractor.extract_leave_type(text)
        extracted['department'] = ContentExtractor.extract_department(text)
        extracted['reason'] = ContentExtractor.extract_reason(text)

        # Try to extract dates
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text)
        if len(dates) >= 2:
            extracted['start_date'] = ContentExtractor.extract_date(dates[0])
            extracted['end_date'] = ContentExtractor.extract_date(dates[1])
        else:
            extracted['start_date'] = ContentExtractor.extract_date(text)
            extracted['end_date'] = None

        return {k: v for k, v in extracted.items() if v is not None}
