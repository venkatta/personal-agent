# Leave Form Assistant - A CrewAI Agent System

A sophisticated leave form fulfillment assistant built with CrewAI that helps employees submit leave requests through a conversational interface.

## 🎯 Overview

The Leave Form Assistant is a multi-agent system that guides employees through the leave request process with:

- **Intent Recognition** - Understands user's intent regarding leave requests
- **Smart Content Extraction** - Parses natural language to extract form fields
- **Robust Validation** - Validates all inputs against business rules
- **Empathetic Communication** - Provides helpful guidance and error messages
- **Form Confirmation** - Allows users to review and confirm before submission

## 🏗️ Architecture

### System Layers

```
┌─────────────────────────────────┐
│  User Interface Layer           │  Chat Interface / API
├─────────────────────────────────┤
│  Application Layer              │  Main App + Crew Orchestrator
├─────────────────────────────────┤
│  Agent Layer (5 Agents)         │  Intent | Extract | Validate | Respond | Confirm
├─────────────────────────────────┤
│  Tools & Models Layer           │  Validators | Extractors | Data Models
├─────────────────────────────────┤
│  Data Storage                   │  Form Data | Conversation History
├─────────────────────────────────┤
│  LLM Integration                │  GPT-4 / Claude
└─────────────────────────────────┘
```

## 🤖 Five Primary Agents

### 1. Intent Agent
**Role**: Intent Recognition Specialist
- Identifies what user is trying to accomplish
- Understands context and guides accordingly
- Handles: new submission, clarification, status check, cancellation

### 2. Extraction Agent
**Role**: Form Data Extraction Specialist
- Extracts form fields from natural language
- Uses regex patterns and NLP techniques
- Handles multiple date formats and naming variations

### 3. Validation Agent
**Role**: Form Validation Specialist
- Validates all inputs against business rules
- Provides clear error messages and suggestions
- Handles warnings (e.g., duration > 30 days)

### 4. Response Agent
**Role**: User Communication Specialist
- Creates empathetic and helpful responses
- Communicates validation errors and warnings
- Asks for missing information conversationally
- Acknowledges user inputs positively

### 5. Confirmation Agent
**Role**: Form Review and Confirmation Specialist
- Generates form summary for review
- Presents confirmation/edit/cancel options
- Handles successful submission and cancellation

## 📋 Form Fields

**Required Fields (9 total)**:
- Employee ID, Name, Department
- Leave Type, Start Date, End Date
- Reason, Contact Email, Manager Name

**Optional Fields**:
- Contact Phone, Coverage Details

## ✅ Validation Rules

- Employee ID: 2-20 chars (uppercase/numbers/hyphens)
- Names: 2-100 chars (letters/spaces/hyphens/apostrophes)
- Email: Valid email format
- Department: From predefined list
- Leave Type: From predefined list
- Dates: Future dates, end > start
- Duration: Max 60 days
- Reason: 5-500 characters
- Warning: > 30 days requires manager approval

## 📊 Processing Flow

```
User Input → Intent Recognition → Content Extraction 
→ Validation → Error Handling/Clarification 
→ Form Completion Check → Form Summary 
→ User Confirmation → Submission Success
```

## 🛠️ Key Components

### ContentExtractor
Intelligent text parsing for:
- Employee IDs, names, emails, phone numbers
- Multiple date formats
- Leave types from natural language
- Department names
- Leave reasons

### LeaveFormValidator
Comprehensive validation for:
- Field format validation
- Business rule enforcement
- Custom error messages
- Warning detection

### Data Models
Pydantic models for:
- Type safety and validation
- API request/response formats
- Enum types for controlled values

## 📁 Project Structure

```
leave_form_assistant/
├── agents/              # 5 Agent implementations
├── tools/               # Extractors & Validators
├── models/              # Data models (Pydantic)
├── tasks/               # Task definitions
├── diagrams/            # Mermaid diagrams & HTML
├── crew.py              # Crew orchestrator
├── main.py              # Main application
├── config.py            # Configuration
└── requirements.txt     # Dependencies
```

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install -r leave_form_assistant/requirements.txt

# Set environment variable
export OPENAI_API_KEY="your-key"
```

### Usage

```python
from leave_form_assistant.main import LeaveFormAssistant

# Create assistant
assistant = LeaveFormAssistant()

# Start conversation
print(assistant.start_conversation())

# Process messages
result = assistant.process_message("I need casual leave from 20-03-2026 to 24-03-2026")
print(result['response'])

# Submit when complete
if result['is_form_complete']:
    confirmation = assistant.confirm_and_submit("confirm")
    print(confirmation['response'])
```

## 📈 Features

✅ **Multi-Agent Architecture** - Specialized agents for each task
✅ **Conversational UI** - Natural language interaction
✅ **Robust Validation** - Business rules enforcement
✅ **Smart Extraction** - Parse various input formats
✅ **Error Handling** - Helpful error messages
✅ **Progress Tracking** - Real-time completion percentage
✅ **Form Review** - Complete summary before submission
✅ **Audit Trail** - Full conversation history

## 📊 Diagrams

See `diagrams/index.html` for interactive architecture and flow diagrams:
- System Architecture
- Main Processing Flow
- UI State Management
- Agent Interactions
- Validation Flow

## 🔧 Configuration

Edit `config.py` to customize:
- Leave types
- Departments
- Validation rules
- LLM settings
- Field requirements

## 📝 Example Tasks

### Task 1: Intent Recognition
Input: "I need to take leave next week"
Output: Intent=NEW_SUBMISSION, Confidence=HIGH

### Task 2: Content Extraction
Input: "My employee ID is EMP-001, name is John Doe"
Output: {employee_id: "EMP-001", employee_name: "John Doe"}

### Task 3: Validation
Input: All required fields with values
Output: is_valid=true, errors=[], warnings=[list]

### Task 4: Error Response
Input: Validation errors list
Output: Friendly error message with solutions

### Task 5: Confirmation
Input: Complete form data
Output: Summary + confirmation options

## 🎯 Next Steps

1. **Deploy** - Set up with a chat interface (Slack, Teams, etc.)
2. **Persistence** - Add database for form submissions
3. **Integration** - Connect to HR systems
4. **Analytics** - Track form submission metrics
5. **Enhancement** - Add more validation rules

## 📞 Support

For issues or questions, refer to:
- Agent class docstrings
- Task descriptions
- Validation rules in `tools/validators.py`
- Example usage in `main.py`

## 📄 License

MIT License - See LICENSE file for details

---

Built with ❤️ using CrewAI
