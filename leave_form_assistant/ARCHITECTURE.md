# Leave Form Assistant - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Agent Responsibilities](#agent-responsibilities)
6. [Design Patterns](#design-patterns)

## System Overview

The Leave Form Assistant is an intelligent, multi-agent system built on CrewAI that automates the leave request form submission process. It uses five specialized agents working in concert to understand user intent, extract form data, validate inputs, communicate with users, and manage form confirmation.

### Key Features
- **Conversational Interface**: Natural language interaction
- **Multi-Agent Architecture**: Separation of concerns
- **Robust Validation**: Business rule enforcement
- **Smart Extraction**: Intelligent field parsing
- **Progress Tracking**: Real-time completion metrics
- **Error Handling**: User-friendly error messages

---

## Architecture Layers

### 1. **User Interface Layer**
```
┌──────────────────────────┐
│   Chat Interface / API   │
│  (Flask/FastAPI/Slack)   │
└────────────┬─────────────┘
```
- Accepts user messages
- Returns assistant responses
- Manages session state
- Handles API requests/responses

### 2. **Application Layer**
```
┌──────────────────────────────────────────┐
│      LeaveFormAssistant (main.py)        │
│  - Entry point for all interactions      │
│  - Session management                    │
│  - Form submission coordination          │
└────────────┬─────────────────────────────┘
             │
┌────────────▼─────────────────────────────┐
│      LeaveFormCrew (crew.py)             │
│  - Orchestrates agent tasks              │
│  - Manages form state                    │
│  - Coordinates validation & response     │
└──────────────────────────────────────────┘
```

### 3. **Agent Layer** (5 Specialized Agents)
```
┌─────────────────────────────────────────────────────────┐
│                  Agent Layer (CrewAI)                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Intent Agent │  │Extraction    │  │ Validation   │   │
│  │              │  │ Agent        │  │ Agent        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │ Response     │  │ Confirmation │                      │
│  │ Agent        │  │ Agent        │                      │
│  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

**Agents:**
- **Intent Agent**: Recognizes user's intent
- **Extraction Agent**: Parses form fields
- **Validation Agent**: Enforces business rules
- **Response Agent**: Creates user messages
- **Confirmation Agent**: Manages form review

### 4. **Tools & Models Layer**
```
┌──────────────────────────────────────────┐
│         Tools & Models Layer              │
├──────────────────────────────────────────┤
│  ┌────────────────────────────────────┐  │
│  │   ContentExtractor (tools)         │  │
│  │   - Regex patterns                 │  │
│  │   - NLP field parsing              │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │   LeaveFormValidator (tools)       │  │
│  │   - Format validation              │  │
│  │   - Business rule checks           │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │   Pydantic Models (models)         │  │
│  │   - LeaveRequest                   │  │
│  │   - ValidationResult               │  │
│  │   - FormResponse                   │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

### 5. **Data Storage & LLM Layer**
```
┌──────────────────────────────────────────┐
│         Data Storage & LLM                │
├──────────────────────────────────────────┤
│  Form Data (In-memory Cache)             │
│  - Current form fields                   │
│  - Completion percentage                 │
│  - Validation state                      │
├──────────────────────────────────────────┤
│  Conversation History                    │
│  - User messages                         │
│  - Agent responses                       │
│  - Timestamps                            │
├──────────────────────────────────────────┤
│  LLM Integration (OpenAI/Claude)         │
│  - Natural language understanding        │
│  - Response generation                   │
└──────────────────────────────────────────┘
```

---

## Component Details

### Models (`models/leave_request.py`)

#### LeaveRequest
Main data model for the leave form:
```python
class LeaveRequest(BaseModel):
    employee_id: str          # Required: EMP-001
    employee_name: str        # Required: Full name
    department: str           # Required: From list
    leave_type: LeaveType     # Required: Enum
    start_date: datetime      # Required: Future date
    end_date: datetime        # Required: After start
    reason: str              # Required: 5-500 chars
    contact_email: str       # Required: Valid email
    contact_phone: str       # Optional
    manager_name: str        # Required
    cover_details: str       # Optional
    status: LeaveStatus      # Default: PENDING
    created_at: datetime     # Auto-generated
```

**Validators:**
- `validate_start_date()`: Ensures future date
- `validate_end_date()`: Ensures end > start
- `validate_employee_id()`: Format check
- `validate_employee_name()`: Length/format check

#### LeaveType (Enum)
Acceptable leave types:
- SICK: Sick Leave
- CASUAL: Casual Leave
- EARNED: Earned Leave
- MATERNITY: Maternity Leave
- PATERNITY: Paternity Leave
- UNPAID: Unpaid Leave
- BEREAVEMENT: Bereavement Leave

#### LeaveStatus (Enum)
Request status values:
- PENDING: Initial state
- APPROVED: Manager approved
- REJECTED: Manager rejected
- CANCELLED: User cancelled

#### ValidationResult
```python
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    processed_at: datetime
```

#### FormResponse
API response format:
```python
class FormResponse(BaseModel):
    leave_request: Optional[LeaveRequest]
    validation_result: ValidationResult
    completion_percentage: float
    next_step: str
    user_message: str
```

### Tools (`tools/`)

#### ContentExtractor (`extractors.py`)
Intelligent text parsing for form fields:

**Methods:**
- `extract_employee_id()`: Pattern-based ID extraction
- `extract_name()`: Capitalization-based name detection
- `extract_email()`: RFC-compliant email extraction
- `extract_phone()`: Phone number in multiple formats
- `extract_date()`: Multiple date format support
- `extract_leave_type()`: Leave type from keywords
- `extract_department()`: Department name matching
- `extract_reason()`: Sentence/reason extraction
- `parse_form_text()`: Comprehensive form parsing

**Features:**
- Handles multiple date formats (YYYY-MM-DD, DD-MM-YYYY, "15 Jan 2024")
- Recognizes leave types from natural language
- Extracts names from capitalized words
- Validates email format
- Phone number support (domestic and international)

#### LeaveFormValidator (`validators.py`)
Comprehensive field and business rule validation:

**Field Validators:**
- `validate_employee_id()`: 2-20 chars, uppercase/numbers/hyphens
- `validate_employee_name()`: 2-100 chars, letters/spaces/hyphens
- `validate_email()`: RFC-compliant email validation
- `validate_phone()`: International phone format
- `validate_dates()`: Future dates, end > start, max 60 days
- `validate_reason()`: 5-500 characters length
- `validate_manager_name()`: 2-100 chars, valid characters
- `validate_department()`: From predefined list

**Business Logic:**
- Invalid date ranges detection
- Duration calculation and limits
- Manager approval requirement warnings (>30 days)
- Comprehensive field-level validation

**Method:**
```python
validate_all_fields(form_data: Dict[str, Any]) 
  -> Tuple[bool, List[str], List[str]]
```
Returns: (is_valid, errors, warnings)

### Agents (`agents/`)

#### IntentAgent (`intent_agent.py`)
**Purpose:** Understand user's intent
**Role:** Intent Recognition Specialist

**Methods:**
- `create_agent()`: Create the agent instance
- `create_intent_recognition_task()`: Identify intent
- `create_user_guidance_task()`: Guide user

**Intent Types:**
- NEW_SUBMISSION: User wants to submit form
- CLARIFICATION: User needs help
- UPDATE: User wants to modify existing form
- STATUS_CHECK: User checking request status
- CANCEL: User cancelling request

#### ExtractionAgent (`extraction_agent.py`)
**Purpose:** Extract form fields from user input
**Role:** Form Data Extraction Specialist

**Methods:**
- `create_agent()`: Create the agent instance
- `create_field_extraction_task()`: Extract all fields
- `create_clarification_task()`: Ask for missing fields
- `create_field_summary_task()`: Summarize extracted data

**Extracted Fields:**
All required and optional fields with confidence levels

#### ValidationAgent (`validation_agent.py`)
**Purpose:** Validate all form inputs
**Role:** Form Validation Specialist

**Methods:**
- `create_agent()`: Create the agent instance
- `create_validation_task()`: Validate all fields
- `create_error_response_task()`: Respond to errors
- `create_warning_notification_task()`: Notify warnings
- `create_summary_task()`: Provide validation summary

#### ResponseAgent (`response_agent.py`)
**Purpose:** Communicate with user
**Role:** User Communication Specialist

**Methods:**
- `create_agent()`: Create the agent instance
- `create_validation_error_response_task()`: Handle errors
- `create_clarification_request_task()`: Request missing info
- `create_progress_update_task()`: Show progress
- `create_correction_acknowledgment_task()`: Acknowledge updates
- `create_generic_help_task()`: Provide help

#### ConfirmationAgent (`confirmation_agent.py`)
**Purpose:** Manage form review and confirmation
**Role:** Form Review and Confirmation Specialist

**Methods:**
- `create_agent()`: Create the agent instance
- `create_form_summary_task()`: Generate summary
- `create_confirmation_request_task()`: Request confirmation
- `create_confirmation_acknowledgment_task()`: Acknowledge success
- `create_edit_field_task()`: Handle field edits
- `create_rejection_handling_task()`: Handle cancellation

### Orchestrator (`crew.py`)

#### LeaveFormCrew
Coordinates all agents and form processing:

**State Management:**
```python
- form_data: Dict[str, Any]        # Current form fields
- validation_errors: List[str]     # Collected errors
- validation_warnings: List[str]   # Policy warnings
- completion_percentage: int        # 0-100
- conversation_history: List       # Full audit trail
```

**Core Methods:**
- `process_user_input()`: Main processing pipeline
- `confirm_submission()`: Handle user confirmation
- `edit_field()`: Allow field modifications
- `get_form_summary()`: Return current form state

**Processing Pipeline:**
1. Intent Recognition
2. Content Extraction
3. Form Data Update
4. Completion Calculation
5. Conditional Validation
6. Error/Warning Response Generation
7. State Management

### Application (`main.py`)

#### LeaveFormAssistant
Main application interface:

**Methods:**
- `start_conversation()`: Send greeting
- `process_message()`: Process user input
- `confirm_and_submit()`: Handle confirmation
- `edit_form_field()`: Modify field value
- `get_form_status()`: Get current progress
- `get_conversation_history()`: Get full history
- `export_form_data()`: Export as JSON/CSV

**Session Management:**
- Tracks submission status
- Maintains conversation history
- Manages form state
- Provides progress tracking

---

## Data Flow

### User Message Processing Flow

```
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
    ┌────▼─────────────────────┐
    │ Intent Recognition       │
    │ (Identify user's intent) │
    └────┬─────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Content Extraction        │
    │ (Parse form fields)       │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Update Form Data          │
    │ & Calculate Completion    │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Should Validate? (Enough  │
    │ data collected?)          │
    └────┬──────────────────────┘
         │
    ┌────┴───────────┬─────────────────┐
    │ Yes            │ No              │
    ▼                ▼                 ▼
┌─────────────┐  ┌──────────────────────────┐
│ Validation  │  │ Ask for Missing Fields   │
└────┬────────┘  └──────────────────────────┘
     │                   │
     │          ┌────────┘
     │          │
     ▼          ▼
┌──────────────────────────────────┐
│ Has Errors?                      │
└────┬───────────────────┬─────────┘
     │ Yes               │ No
     ▼                   ▼
┌─────────────┐   ┌──────────────────────┐
│ Error       │   │ Has Warnings?        │
│ Response    │   └────┬─────────┬───────┘
└────┬────────┘        │ Yes     │ No
     │          ┌──────▼─────┐   │
     │          │ Warning    │   │
     │          │ Message    │   │
     │          └──────┬─────┘   │
     │                 │         │
     │          ┌──────┘         │
     │          │                │
     │          ▼                ▼
     │   ┌────────────────────────────┐
     │   │ Form Complete?             │
     │   └────┬──────────────────┬────┘
     │        │ Yes              │ No
     │        ▼                  ▼
     │   ┌──────────────┐   ┌──────────────┐
     │   │ Ask for      │   │ More Clarif. │
     │   │ Confirmation │   │ Needed       │
     │   └──────┬───────┘   └──────┬───────┘
     │          │                  │
     └──────────┼──────────────────┘
                │
                ▼
        ┌────────────────────┐
        │ Send Response      │
        │ to User            │
        └────────────────────┘
```

### Validation Flow

```
Input Data
    │
    ├─→ Validate Employee ID
    │       ├─→ Not empty?
    │       ├─→ 2-20 chars?
    │       └─→ Format valid?
    │
    ├─→ Validate Name Fields
    │       ├─→ Length check
    │       └─→ Character check
    │
    ├─→ Validate Email/Phone
    │       ├─→ Format check
    │       └─→ Pattern match
    │
    ├─→ Validate Department
    │       └─→ In allowed list?
    │
    ├─→ Validate Dates
    │       ├─→ Future dates?
    │       ├─→ End > Start?
    │       └─→ Duration ≤ 60 days?
    │
    └─→ Validate Reason
            └─→ 5-500 chars?

Result: Errors + Warnings + Validity Status
```

---

## Agent Responsibilities

### Intent Agent
- **Input**: Raw user message
- **Processing**: Keyword analysis, intent matching
- **Output**: Intent type (NEW_SUBMISSION, CLARIFICATION, etc.)
- **Triggers**: Every user interaction

### Extraction Agent
- **Input**: User message
- **Processing**: Regex patterns, NLP parsing
- **Output**: Extracted field values with confidence
- **Triggers**: After intent confirmation

### Validation Agent
- **Input**: Form data dictionary
- **Processing**: Field validation, business rule checking
- **Output**: Errors list, warnings list, validity boolean
- **Triggers**: When sufficient form data collected

### Response Agent
- **Input**: Validation errors, missing fields, warnings
- **Processing**: Empathetic message generation
- **Output**: User-friendly guidance messages
- **Triggers**: When errors or clarification needed

### Confirmation Agent
- **Input**: Complete form data
- **Processing**: Summary formatting, confirmation UI
- **Output**: Formatted summary + confirmation options
- **Triggers**: When all required fields complete

---

## Design Patterns

### 1. **Orchestrator Pattern**
`LeaveFormCrew` orchestrates agent tasks and manages state.

### 2. **Strategy Pattern**
Different validation strategies for different field types.

### 3. **Chain of Responsibility**
Multiple validators check form sequentially.

### 4. **State Machine Pattern**
Form progresses through defined states:
- INITIAL → COLLECTING → COMPLETED → CONFIRMING → SUBMITTED

### 5. **Factory Pattern**
Agent creation via static factory methods.

### 6. **Data Transfer Object (DTO)**
`FormResponse` and `ValidationResult` act as DTOs.

### 7. **Pydantic Validation Pattern**
Built-in validators on model fields for automatic validation.

### 8. **Separation of Concerns**
- Extraction logic separate from validation
- Validation separate from communication
- Communication separate from confirmation

---

## Configuration (`config.py`)

Project-wide configuration:

```python
CONFIG = {
    "project_name": "Leave Form Assistant",
    "version": "1.0.0",
    "leave_types": [...],
    "departments": [...],
    "validation": {
        "max_leave_days": 60,
        "min_reason_length": 5,
        "approval_threshold_days": 30,
    },
    "required_fields": [...],
    "optional_fields": [...],
}
```

**Customization:** Edit config values to adjust business rules, allowed leave types, and departments.

---

## Dependencies

- **CrewAI**: Agent orchestration framework
- **Pydantic**: Data validation and parsing
- **email-validator**: Email format validation
- **Python 3.10+**: Core language requirement

---

## Extensibility

### Adding New Validation Rules
1. Add method to `LeaveFormValidator`
2. Call from `validate_all_fields()`
3. Return (is_valid, error_message)

### Adding New Leave Types
1. Update `LeaveType` enum in models
2. Update config `leave_types` list
3. Update extraction patterns if needed

### Adding New Departments
1. Update config `departments` list
2. Update extraction patterns
3. Update validation allowed values

### Adding New Agent
1. Create new agent class in `agents/`
2. Implement `create_agent()` and `create_*_task()` methods
3. Integrate into `LeaveFormCrew.process_user_input()`
4. Update conversation flow as needed

---

## Performance Considerations

- **In-Memory Storage**: Form data cached in memory during session
- **Regex Efficiency**: Compiled patterns for faster extraction
- **LLM Calls**: Minimized through local validation
- **Conversation History**: Stored for audit/debugging

---

## Security Considerations

- **Input Validation**: All user inputs validated
- **Email Validation**: RFC-compliant email checking
- **No Sensitive Data**: Passwords/SSNs not stored
- **GDPR Ready**: Audit trail maintained with timestamps

---

## Future Enhancements

1. **Database Persistence**: Persist forms to database
2. **Multi-Language Support**: I18n for different languages
3. **Approval Workflows**: Manager approval integration
4. **Notification System**: Email/SMS notifications
5. **Analytics Dashboard**: Form submission metrics
6. **Advanced NLP**: ML-based field extraction
7. **Attachment Support**: Resume/certificate uploads
8. **Calendar Integration**: Automatic leave calendar blocking
