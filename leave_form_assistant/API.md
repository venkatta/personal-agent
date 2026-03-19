# Leave Form Assistant - API Documentation

## Overview

The Leave Form Assistant exposes a clean API through the `LeaveFormAssistant` class. All interactions flow through this application interface.

## LeaveFormAssistant Class

### Initialization

```python
from leave_form_assistant.main import LeaveFormAssistant

# Create instance (LLM is optional - can be added later)
assistant = LeaveFormAssistant(llm=None)
```

**Parameters:**
- `llm` (optional): Language model instance (OpenAI, Claude, etc.)

**Attributes:**
- `crew`: `LeaveFormCrew` instance handling form processing
- `session_active`: Boolean indicating if session is open
- `submission_status`: Status of form submission (None, SUBMITTED, CANCELLED)

---

## Core API Methods

### 1. `start_conversation() -> str`

Starts the conversation with the user.

**Returns:**
- `str`: Welcome message

**Example:**
```python
greeting = assistant.start_conversation()
print(greeting)
# Output: "🎯 Welcome to the Leave Form Assistant!..."
```

**Use Case:** Call once at the beginning of each session to greet the user.

---

### 2. `process_message(user_message: str) -> Dict[str, Any]`

Processes a user message through the complete workflow.

**Parameters:**
- `user_message` (str): User's input text

**Returns:**
```python
{
    "response": str,                      # Assistant's response
    "form_data": Dict[str, Any],          # Current form state
    "completion_percentage": int,          # 0-100 completion
    "is_form_complete": bool,             # All fields filled?
    "errors": List[str],                  # Validation errors
    "warnings": List[str],                # Policy warnings
    "next_action": str                    # PROVIDE_CORRECTIONS | 
                                          # CONFIRM_SUBMISSION | 
                                          # ACKNOWLEDGE_WARNINGS |
                                          # PROVIDE_MORE_INFORMATION
}
```

**Example:**
```python
# First message
result = assistant.process_message(
    "Hi, I need casual leave for 3 days next week"
)
print(result['response'])
# Output: "Great! I have 20% of your information. Just need a few more details..."
print(f"Completion: {result['completion_percentage']}%")
```

**Workflow:**
1. Recognizes intent
2. Extracts form fields
3. Updates form state
4. Calculates completion
5. Validates if ready
6. Generates response

---

### 3. `confirm_and_submit(confirmation: str) -> Dict[str, Any]`

Handles user confirmation or rejection of the form.

**Parameters:**
- `confirmation` (str): User's action
  - Accept: "yes", "confirm", "submit", "proceed", "✅"
  - Reject: "no", "cancel", "reject", "back", "❌"
  - Unclear: Any other input

**Returns:**
```python
{
    "response": str,                  # Assistant response
    "status": str,                    # SUBMITTED | CANCELLED | PENDING
    "form_data": Optional[Dict],      # Only if SUBMITTED
    "submission_status": str          # Current session status
}
```

**Example:**
```python
# After form is complete
if result['is_form_complete']:
    confirmation = assistant.confirm_and_submit("confirm")
    print(confirmation['response'])
    # Output: "✅ SUCCESS! Your leave request has been submitted..."
    print(f"Status: {confirmation['status']}")
    # Output: "Status: SUBMITTED"
```

**Behavior:**
- On confirm: Submit form, end session, return success
- On reject: Cancel form, clear data, offer restart
- On unclear: Ask for clarification

---

### 4. `edit_form_field(field_name: str, new_value: Any) -> Dict[str, Any]`

Allows user to edit a specific form field.

**Parameters:**
- `field_name` (str): Field to edit (e.g., "start_date")
- `new_value` (Any): New value for the field

**Returns:**
```python
{
    "response": str,                  # Acknowledgment message
    "field_edited": str,              # Field that was updated
    "validation_errors": List[str],   # Errors after edit
    "form_data": Dict                 # Updated form summary
}
```

**Example:**
```python
# User wants to change the start date
result = assistant.edit_form_field("start_date", "2026-03-25")
print(result['response'])
# Output: "✏️ Updated: Start Date..."

# Check if there are new validation errors
if result['validation_errors']:
    print("Please correct:", result['validation_errors'])
```

**Valid Field Names:**
- employee_id
- employee_name
- department
- leave_type
- start_date
- end_date
- reason
- contact_email
- contact_phone
- manager_name
- cover_details

---

### 5. `get_form_status() -> Dict[str, Any]`

Returns the current form state and progress.

**Returns:**
```python
{
    "employee_id": str,              # Current value or ""
    "employee_name": str,
    "department": str,
    "leave_type": str,
    "start_date": str,
    "end_date": str,
    "reason": str,
    "contact_email": str,
    "contact_phone": str,
    "manager_name": str,
    "cover_details": str,
    "completion_percentage": int,    # 0-100
    "missing_fields": List[str]      # Required fields not filled
}
```

**Example:**
```python
status = assistant.get_form_status()
print(f"Form is {status['completion_percentage']}% complete")
print(f"Missing: {status['missing_fields']}")
```

**Use Case:** Get current progress without processing new input.

---

### 6. `get_conversation_history() -> List`

Returns the full conversation history.

**Returns:**
```python
[
    {
        "type": "assistant",        # "assistant" or "user"
        "content": str,             # Message text
        "timestamp": str            # ISO format timestamp
    },
    ...
]
```

**Example:**
```python
history = assistant.get_conversation_history()
for msg in history:
    print(f"[{msg['type'].upper()}] {msg['content'][:50]}...")
```

**Use Case:** Audit trail, debugging, training data, conversation replay.

---

### 7. `export_form_data(format: str = 'json') -> str`

Export current form data in specified format.

**Parameters:**
- `format` (str): Export format
  - 'json': JSON format (default)
  - 'csv': CSV format
  - other: String representation

**Returns:**
- `str`: Form data in specified format

**Example:**
```python
# Export as JSON
json_data = assistant.export_form_data('json')
print(json_data)

# Export as CSV
csv_data = assistant.export_form_data('csv')
with open('form_data.csv', 'w') as f:
    f.write(csv_data)
```

---

## Data Models

### LeaveRequest (models/leave_request.py)

```python
class LeaveRequest(BaseModel):
    employee_id: str              # Employee ID (required)
    employee_name: str            # Full name (required)
    department: str               # Department (required)
    leave_type: LeaveType         # Type of leave (required)
    start_date: datetime          # Start date (required)
    end_date: datetime            # End date (required)
    reason: str                   # Reason (required, 5-500 chars)
    contact_email: str            # Email (required)
    contact_phone: Optional[str]  # Phone (optional)
    manager_name: str             # Manager name (required)
    cover_details: Optional[str]  # Coverage (optional)
    status: LeaveStatus           # Status (default: PENDING)
    created_at: datetime          # Creation time (auto)
    validation_errors: List[str]  # Errors (if any)
```

### LeaveType (Enum)

```python
class LeaveType(str, Enum):
    SICK = "Sick Leave"
    CASUAL = "Casual Leave"
    EARNED = "Earned Leave"
    MATERNITY = "Maternity Leave"
    PATERNITY = "Paternity Leave"
    UNPAID = "Unpaid Leave"
    BEREAVEMENT = "Bereavement Leave"
```

### ValidationResult

```python
class ValidationResult(BaseModel):
    is_valid: bool              # Validation passed?
    errors: List[str]           # Validation errors
    warnings: List[str]         # Policy warnings
    processed_at: datetime      # When validation ran
```

### FormResponse

```python
class FormResponse(BaseModel):
    leave_request: Optional[LeaveRequest]
    validation_result: ValidationResult
    completion_percentage: float
    next_step: str              # What to do next
    user_message: str           # Message for user
```

---

## Tools API

### ContentExtractor (tools/extractors.py)

Static methods for parsing form fields:

```python
from leave_form_assistant.tools import ContentExtractor

# Extract individual fields
employee_id = ContentExtractor.extract_employee_id(text)
name = ContentExtractor.extract_name(text)
email = ContentExtractor.extract_email(text)
phone = ContentExtractor.extract_phone(text)
date = ContentExtractor.extract_date(text)
leave_type = ContentExtractor.extract_leave_type(text)
department = ContentExtractor.extract_department(text)
reason = ContentExtractor.extract_reason(text)

# Extract and parse complete form
all_fields = ContentExtractor.parse_form_text(user_input)
# Returns: {field_name: extracted_value, ...}
```

**Example:**
```python
user_text = "Hi, I'm John Doe, EMP-001, need casual leave from 20-03-2026 to 24-03-2026"
extracted = ContentExtractor.parse_form_text(user_text)
# Returns: {
#     'employee_id': 'EMP-001',
#     'employee_name': 'John Doe',
#     'leave_type': 'Casual',
#     'start_date': datetime(2026, 3, 20),
#     'end_date': datetime(2026, 3, 24)
# }
```

---

### LeaveFormValidator (tools/validators.py)

Static methods for field validation:

```python
from leave_form_assistant.tools import LeaveFormValidator

# Validate individual fields
is_valid, error_msg = LeaveFormValidator.validate_employee_id(id_str)
is_valid, error_msg = LeaveFormValidator.validate_email(email_str)
is_valid, error_msg = LeaveFormValidator.validate_phone(phone_str)
is_valid, errors = LeaveFormValidator.validate_dates(start, end)

# Validate all fields
is_valid, errors, warnings = LeaveFormValidator.validate_all_fields(form_dict)
```

**Example:**
```python
# Single field validation
is_valid, error = LeaveFormValidator.validate_email("john@example.com")
if not is_valid:
    print(f"Email error: {error}")

# Complete form validation
form = {
    'employee_id': 'EMP-001',
    'employee_name': 'John Doe',
    'department': 'Engineering',
    'leave_type': 'Casual Leave',
    'start_date': datetime(2026, 3, 20),
    'end_date': datetime(2026, 3, 24),
    'reason': 'Family vacation',
    'contact_email': 'john@example.com',
    'manager_name': 'Jane Smith'
}

is_valid, errors, warnings = LeaveFormValidator.validate_all_fields(form)
if not is_valid:
    print("Errors:", errors)
if warnings:
    print("Warnings:", warnings)
```

---

## Typical Conversation Flow

### Example 1: Simple Form Submission

```python
assistant = LeaveFormAssistant()

# Start
print(assistant.start_conversation())

# Message 1: Provide initial info
result = assistant.process_message(
    "I need casual leave for 3 days starting March 20th"
)
print(result['response'])
print(f"Completion: {result['completion_percentage']}%")

# Message 2: Provide more details
result = assistant.process_message(
    "Employee ID is EMP-001, my name is John Doe"
)
print(result['response'])
print(f"Completion: {result['completion_percentage']}%")

# Message 3: Complete remaining fields
result = assistant.process_message(
    "I'm in Engineering, email john@company.com, manager is Jane Smith"
)
print(result['response'])
print(f"Completion: {result['completion_percentage']}%")

# Message 4: Provide reason
if not result['is_form_complete']:
    result = assistant.process_message("Reason: Personal vacation")
    print(result['response'])

# Confirm submission
if result['is_form_complete']:
    confirmation = assistant.confirm_and_submit("yes")
    print(confirmation['response'])
```

### Example 2: Form Editing

```python
# After collecting all information...
status = assistant.get_form_status()
print(f"Employee: {status['employee_name']}")
print(f"Dates: {status['start_date']} to {status['end_date']}")

# User wants to change dates
result = assistant.edit_form_field("start_date", "2026-03-21")
print(result['response'])

result = assistant.edit_form_field("end_date", "2026-03-25")
print(result['response'])

# Review and confirm
confirmation = assistant.confirm_and_submit("confirm")
print(confirmation['response'])
```

### Example 3: Error Handling

```python
# Invalid date
result = assistant.process_message("I need leave from 2025-01-01 to 2025-01-10")
print(result['errors'])  # ["Start date must be in the future"]
print(result['next_action'])  # "PROVIDE_CORRECTIONS"

# User corrects
result = assistant.process_message("Actually, from 2026-04-01 to 2026-04-10")
print(result['is_form_complete'])  # Still might be false if other fields missing
```

---

## Validation Rules Reference

| Field | Rules | Example |
|-------|-------|---------|
| employee_id | 2-20 chars, [A-Z0-9-] | EMP-001 |
| employee_name | 2-100 chars, letters/spaces/hyphens | John Doe |
| department | From predefined list | Engineering |
| leave_type | From predefined list | Casual Leave |
| start_date | Future date, various formats | 2026-03-20 |
| end_date | After start_date, max 60 days | 2026-03-24 |
| reason | 5-500 characters | "Family vacation" |
| contact_email | Valid email format | john@example.com |
| contact_phone | Optional, valid phone format | +1-555-0100 |
| manager_name | 2-100 chars, letters/spaces | Jane Smith |
| cover_details | Optional, any text | "John Smith will cover" |

---

## Error Handling

### Common Errors

```python
# Invalid date format
result = assistant.process_message("2026-13-45")  # Invalid date
# errors: ["Invalid date format"]

# Email validation failure
result = assistant.edit_form_field("contact_email", "invalid-email")
# validation_errors: ["Invalid email format: ..."]

# Leave duration exceeded
result = assistant.process_message("90 days of leave")
# warnings: ["Leave period cannot exceed 60 days"]

# Validation succeeds but with warnings
result = assistant.process_message("31 days of leave")
# is_form_complete: True
# warnings: ["⚠️ Warning: Leave period exceeds 30 days. Manager approval required"]
```

### Handling Errors in Code

```python
result = assistant.process_message(user_input)

if result['errors']:
    # Handle validation errors
    for error in result['errors']:
        print(f"❌ {error}")
    # Ask user to correct

if result['warnings']:
    # Inform about warnings but can proceed
    for warning in result['warnings']:
        print(f"⚠️ {warning}")

if result['is_form_complete']:
    confirmation = assistant.confirm_and_submit("confirm")
else:
    print(f"Progress: {result['completion_percentage']}%")
    print(f"Status: {result['next_action']}")
```

---

## Configuration API

Access configuration through `config.py`:

```python
from leave_form_assistant.config import get_config

# Get config values
leave_types = get_config('leave_types')
max_days = get_config('validation.max_leave_days')
required_fields = get_config('required_fields')
```

---

## Session Management

Sessions are automatically managed:
- Each `LeaveFormAssistant` instance = one session
- Session ends on successful submission
- Session can be reset by creating new instance
- Conversation history retained in `get_conversation_history()`

---

## Best Practices

1. **Always start with `start_conversation()`** to greet user
2. **Check `errors` and `next_action`** to determine next step
3. **Show `completion_percentage`** to encourage progress
4. **Use `edit_form_field()`** for targeted corrections
5. **Call `confirm_and_submit()`** only when `is_form_complete` is True
6. **Export forms** for audit purposes
7. **Maintain conversation history** for debugging

---

## API Response Examples

### Successful Message Processing

```python
{
    "response": "Great! I've updated your information. I have 75% of your form complete. I just need...",
    "form_data": {
        "employee_id": "EMP-001",
        "employee_name": "John Doe",
        "department": "Engineering",
        "leave_type": "Casual Leave",
        "start_date": "2026-03-20",
        "end_date": "2026-03-24",
        "reason": "Family vacation",
        "contact_email": "john@example.com",
        "manager_name": "Jane Smith"
    },
    "completion_percentage": 75,
    "is_form_complete": False,
    "errors": [],
    "warnings": [],
    "next_action": "PROVIDE_MORE_INFORMATION"
}
```

### Form Complete and Ready for Confirmation

```python
{
    "response": "📋 LEAVE REQUEST FORM SUMMARY\n[... full summary ...]",
    "form_data": {...all fields...},
    "completion_percentage": 100,
    "is_form_complete": True,
    "errors": [],
    "warnings": [],
    "next_action": "CONFIRM_SUBMISSION"
}
```

### Validation Error

```python
{
    "response": "⚠️ I found some issues that need to be corrected:\n1. Email format invalid...",
    "form_data": {...current fields...},
    "completion_percentage": 80,
    "is_form_complete": False,
    "errors": ["Email format invalid"],
    "warnings": [],
    "next_action": "PROVIDE_CORRECTIONS"
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Form not progressing | Check `completion_percentage` and `missing_fields` |
| Validation keeps failing | Review `errors` and use correct format |
| Message not being processed | Verify user input text and intent |
| Session ended unexpectedly | Check if `confirm_and_submit()` was called |
| Conversation history missing | Call `get_conversation_history()` from same instance |

---

## Rate Limiting & Performance

- Local validation is fast (< 100ms)
- LLM calls may take longer (1-3 seconds)
- Form data cached in memory
- No database overhead in base implementation
- Suitable for production with added persistence layer
