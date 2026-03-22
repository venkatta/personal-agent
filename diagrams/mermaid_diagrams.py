"""
Architecture and Flow Diagrams for Leave Form Assistant
"""

ARCHITECTURE_DIAGRAM = """
graph TB
    subgraph "User Interface Layer"
        UI["Chat Interface / API"]
    end

    subgraph "Application Layer"
        MAIN["Main Application<br/>LeaveFormAssistant"]
        CREW["Crew Orchestrator<br/>LeaveFormCrew"]
    end

    subgraph "Agent Layer"
        INTENT["Intent Agent<br/>Understand user intent"]
        EXTRACT["Extraction Agent<br/>Parse form fields"]
        VALIDATE["Validation Agent<br/>Check inputs"]
        RESPONSE["Response Agent<br/>Communicate issues"]
        CONFIRM["Confirmation Agent<br/>Review & confirm"]
    end

    subgraph "Tools & Models Layer"
        EXTRACTOR["Content Extractor<br/>Regex patterns"]
        VALIDATOR["Form Validator<br/>Business rules"]
        MODELS["Data Models<br/>Pydantic schemas"]
    end

    subgraph "Data Storage"
        FORMDATA["Form Data<br/>In-memory cache"]
        HISTORY["Conversation History<br/>Audit trail"]
    end

    subgraph "LLM Integration"
        LLM["Language Model<br/>GPT-4 / Claude"]
    end

    UI -->|User Input| MAIN
    MAIN -->|Process| CREW
    
    CREW -->|Task 1| INTENT
    CREW -->|Task 2| EXTRACT
    CREW -->|Task 3| VALIDATE
    CREW -->|Task 4| RESPONSE
    CREW -->|Task 5| CONFIRM
    
    INTENT -->|Uses| LLM
    RESPONSE -->|Uses| LLM
    CONFIRM -->|Uses| LLM
    
    EXTRACT -->|Uses| EXTRACTOR
    VALIDATE -->|Uses| VALIDATOR
    EXTRACT -->|Uses| MODELS
    VALIDATE -->|Uses| MODELS
    
    CREW -->|Read/Write| FORMDATA
    CREW -->|Append| HISTORY
    
    CREW -->|Response| MAIN
    MAIN -->|Display| UI
"""

FLOW_DIAGRAM = """
flowchart TD
    Start([User Starts Form]) --> Greeting["🎯 Display Welcome<br/>Message & Instructions"]
    
    Greeting --> Input["⌨️ User Provides<br/>Information"]
    
    Input --> Intent{"🔍 Recognize<br/>Intent"}
    
    Intent -->|New Submission| Extract["📝 Extract Form<br/>Fields from Input"]
    Intent -->|Help/Clarification| Help["❓ Provide<br/>Guidance"]
    Intent -->|Other| Other["↩️ Route to<br/>Appropriate Path"]
    
    Help --> Input
    Other --> Input
    
    Extract --> UpdateForm["💾 Update Form<br/>Data Object"]
    
    UpdateForm --> CalcCompletion["📊 Calculate<br/>Completion %"]
    
    CalcCompletion --> ShouldValidate{"Enough Data<br/>to Validate?"}
    
    ShouldValidate -->|No| NeedMore["❓ Ask for Missing<br/>Required Fields"]
    ShouldValidate -->|Yes| Validate["✓ Validate All<br/>Form Fields"]
    
    NeedMore --> Input
    
    Validate --> HasErrors{"❌ Validation<br/>Errors?"}
    
    HasErrors -->|Yes| ErrorResponse["⚠️ Display Error<br/>Messages & Solutions"]
    HasErrors -->|No| HasWarnings{"⚠️ Validation<br/>Warnings?"}
    
    ErrorResponse --> Input
    
    HasWarnings -->|Yes| WarningResponse["⚡ Display Warnings<br/>& Ask to Proceed"]
    HasWarnings -->|No| IsComplete{"✓ All Required<br/>Fields Complete?"}
    
    WarningResponse --> ProceedChoice{"User Wants<br/>to Proceed?"}
    ProceedChoice -->|Edit| Input
    ProceedChoice -->|Proceed| IsComplete
    
    IsComplete -->|No| NeedMore
    IsComplete -->|Yes| FormSummary["📋 Generate Form<br/>Summary"]
    
    FormSummary --> DisplaySummary["📺 Display Complete<br/>Form to User"]
    
    DisplaySummary --> ConfirmIntent{"User Action<br/>?"}
    
    ConfirmIntent -->|Confirm| Submit["📤 Submit Form<br/>& Generate Reference ID"]
    ConfirmIntent -->|Edit| EditField["✏️ Allow User to<br/>Edit Specific Field"]
    ConfirmIntent -->|Cancel| Cancel["❌ Cancel Form<br/>& Clear Data"]
    
    EditField --> UpdateForm
    
    Cancel --> CancelMsg["Goodbye Message<br/>& Option to Restart"]
    CancelMsg --> Start
    
    Submit --> SubmitSuccess["✅ Display Success<br/>Message with<br/>Reference ID"]
    
    SubmitSuccess --> NextSteps["📌 Show Next Steps<br/>& Support Info"]
    
    NextSteps --> End([End Session])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Submit fill:#87CEEB
    style Cancel fill:#FFD700
    style ErrorResponse fill:#FF6B6B
    style WarningResponse fill:#FFA500
    style FormSummary fill:#DDA0DD
    style SubmitSuccess fill:#90EE90
"""

UI_FLOW_DIAGRAM = """
flowchart LR
    subgraph "User Journey"
        A["👤 User"]
        B["💬 Chat Message"]
        C["🤖 Assistant Response"]
    end
    
    subgraph "Form State Machine"
        S1["State: INITIAL"]
        S2["State: COLLECTING"]
        S3["State: COMPLETED"]
        S4["State: CONFIRMING"]
        S5["State: SUBMITTED"]
        S6["State: ERROR"]
    end
    
    subgraph "Data Flow"
        D1["Raw User Input"]
        D2["Extracted Fields"]
        D3["Validated Data"]
        D4["Form Summary"]
    end
    
    A -->|Type| B
    B -->|Process| D1
    D1 -->|Extract| D2
    D2 -->|Validate| D3
    D3 -->|Summarize| D4
    D4 -->|Generate| C
    C -->|Display| A
    
    S1 -->|Form Started| S2
    S2 -->|Extracting Data| S2
    S2 -->|All Data Collected| S3
    S3 -->|Display Summary| S4
    S4 -->|User Confirms| S5
    S4 -->|Validation Fails| S6
    S6 -->|Correct & Retry| S2
    S5 -->|Complete| End([✅ Done])
    
    style A fill:#E8F4F8
    style S5 fill:#90EE90
    style S6 fill:#FF6B6B
"""

AGENT_INTERACTION_DIAGRAM = """
sequenceDiagram
    participant User as 👤 User
    participant Main as 🎯 Main App
    participant Crew as 🚀 Crew
    participant Intent as 🔍 Intent Agent
    participant Extract as 📝 Extract Agent
    participant Validate as ✓ Validate Agent
    participant Response as 💬 Response Agent
    participant Confirm as ✅ Confirm Agent

    User->>Main: Send Message
    Main->>Crew: process_user_input()
    
    Crew->>Intent: recognize_intent()
    Intent-->>Crew: intent result
    
    Crew->>Extract: extract_content()
    Extract-->>Crew: extracted fields
    
    Crew->>Crew: update form_data
    Crew->>Crew: calculate_completion
    
    alt Has content to validate
        Crew->>Validate: validate_form()
        Validate-->>Crew: validation result
        
        alt Has errors
            Crew->>Response: generate_error_response()
            Response-->>Crew: error message
        else Form complete
            Crew->>Confirm: generate_confirmation_prompt()
            Confirm-->>Crew: confirmation UI
        else Missing fields
            Crew->>Response: generate_clarification_request()
            Response-->>Crew: clarification message
        end
    end
    
    Crew-->>Main: response + form_state
    Main-->>User: Display Response
    
    alt User confirms
        User->>Main: Confirm submission
        Main->>Crew: confirm_submission()
        Crew->>Confirm: generate_confirmation_success()
        Confirm-->>Crew: success message
        Crew-->>Main: submission status
        Main-->>User: Success + Reference ID
    end
"""

VALIDATION_FLOW_DIAGRAM = """
graph TD
    Input["📥 Form Input<br/>Data"] --> Val1{"Employee ID<br/>Valid?"}
    
    Val1 -->|No| Err1["❌ Error:<br/>Invalid Format"]
    Val1 -->|Yes| Val2{"Name<br/>Valid?"}
    
    Err1 --> Errors["🔴 Collect<br/>Errors"]
    
    Val2 -->|No| Err2["❌ Error:<br/>Too Short"]
    Val2 -->|Yes| Val3{"Email<br/>Valid?"}
    
    Err2 --> Errors
    
    Val3 -->|No| Err3["❌ Error:<br/>Invalid Format"]
    Val3 -->|Yes| Val4{"Department<br/>Valid?"}
    
    Err3 --> Errors
    
    Val4 -->|No| Err4["❌ Error:<br/>Not in List"]
    Val4 -->|Yes| Val5{"Dates<br/>Valid?"}
    
    Err4 --> Errors
    
    Val5 -->|No| Err5["❌ Error:<br/>Date Issues"]
    Val5 -->|Yes| Warn1{"Duration<br/>> 30 Days?"}
    
    Err5 --> Errors
    
    Warn1 -->|Yes| Warn["🟡 Warning:<br/>Manager Approval<br/>Required"]
    Warn1 -->|No| Val6{"Reason<br/>Valid?"}
    
    Val6 -->|No| Err6["❌ Error:<br/>Reason Too Short"]
    Val6 -->|Yes| Success["✅ All Valid"]
    
    Err6 --> Errors
    
    Warn --> Warnings["🟡 Collect<br/>Warnings"]
    Warnings --> Success
    
    Errors --> Result["📊 Validation<br/>Result"]
    Success --> Result
    
    Result --> Decision{"Has<br/>Errors?"}
    
    Decision -->|Yes| Reject["❌ Reject Form<br/>Ask for Corrections"]
    Decision -->|No| Accept["✅ Accept Form<br/>Proceed to<br/>Confirmation"]
    
    Reject --> Input
    Accept --> Confirm["Confirm with User"]
    
    style Success fill:#90EE90
    style Reject fill:#FF6B6B
    style Warn fill:#FFA500
"""

if __name__ == "__main__":
    print("Architecture Diagram:")
    print(ARCHITECTURE_DIAGRAM)
    print("\n" + "="*80 + "\n")
    
    print("Main Flow Diagram:")
    print(FLOW_DIAGRAM)
    print("\n" + "="*80 + "\n")
    
    print("UI Flow Diagram:")
    print(UI_FLOW_DIAGRAM)
    print("\n" + "="*80 + "\n")
    
    print("Agent Interaction Diagram:")
    print(AGENT_INTERACTION_DIAGRAM)
    print("\n" + "="*80 + "\n")
    
    print("Validation Flow Diagram:")
    print(VALIDATION_FLOW_DIAGRAM)
