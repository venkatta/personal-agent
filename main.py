"""
Leave Form Assistant - Main Application
Entry point for the leave form fulfillment system
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from typing import Optional, Dict, Any
import json
from crew import LeaveFormCrew


class LeaveFormAssistant:
    """Main application interface for the leave form assistant"""

    def __init__(self, llm=None):
        """Initialize the leave form assistant"""
        self.crew = LeaveFormCrew(llm)
        self.session_active = True
        self.submission_status = None

    def start_conversation(self) -> str:
        """Start the conversation with a greeting"""
        greeting = """
🎯 Welcome to the Leave Form Assistant!

I'm here to capture your leave window quickly and accurately.

Please tell me:
• What type of leave you're requesting
• The leave start date and time
• The leave end date and time

Just share the information in your own words, and I'll guide you through the rest!

What would you like to do?
"""
        self.crew.conversation_history.append({
            "type": "assistant",
            "content": greeting,
            "timestamp": None
        })
        return greeting

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message and return response"""
        
        result = self.crew.process_user_input(user_message)
        
        # Extract the response
        response = result.get('response', '')
        
        return {
            "response": response,
            "form_data": result.get('form_data', {}),
            "completion_percentage": result.get('completion_percentage', 0),
            "is_form_complete": result.get('is_form_complete', False),
            "errors": result.get('validation_errors', []),
            "warnings": result.get('validation_warnings', []),
            "next_action": self._determine_next_action(result)
        }

    def confirm_and_submit(self, confirmation: str) -> Dict[str, Any]:
        """Confirm and submit the form"""
        result = self.crew.confirm_submission(confirmation)
        
        if result.get('status') == 'SUBMITTED':
            self.submission_status = 'SUBMITTED'
            self.session_active = False
        elif result.get('status') == 'CANCELLED':
            self.submission_status = 'CANCELLED'
            # Can continue with new form
        
        return {
            "response": result.get('response', ''),
            "status": result.get('status'),
            "form_data": result.get('form_data'),
            "submission_status": self.submission_status
        }

    def edit_form_field(self, field_name: str, new_value: Any) -> Dict[str, Any]:
        """Edit a specific form field"""
        result = self.crew.edit_field(field_name, new_value)
        
        return {
            "response": result.get('response', ''),
            "field_edited": result.get('field_edited'),
            "validation_errors": result.get('validation_errors', []),
            "form_data": self.crew.get_form_summary()
        }

    def get_form_status(self) -> Dict[str, Any]:
        """Get current form status and progress"""
        return self.crew.get_form_summary()

    def get_conversation_history(self) -> list:
        """Get full conversation history"""
        return self.crew.conversation_history

    def _determine_next_action(self, result: Dict[str, Any]) -> str:
        """Determine what the user should do next based on processing result"""
        
        is_complete = result.get('is_form_complete', False)
        has_errors = len(result.get('validation_errors', [])) > 0
        has_warnings = len(result.get('validation_warnings', [])) > 0
        
        if has_errors:
            return "PROVIDE_CORRECTIONS"
        elif is_complete and not has_errors:
            return "CONFIRM_SUBMISSION"
        elif has_warnings:
            return "ACKNOWLEDGE_WARNINGS"
        else:
            return "PROVIDE_MORE_INFORMATION"

    def export_form_data(self, format: str = 'json') -> str:
        """Export form data in specified format"""
        form_summary = self.crew.get_form_summary()
        
        if format == 'json':
            return json.dumps(form_summary, indent=2, default=str)
        elif format == 'csv':
            items = form_summary.items()
            header = ','.join([str(k) for k, v in items])
            values = ','.join([f'"{v}"' if isinstance(v, str) else str(v) for k, v in items])
            return f"{header}\n{values}"
        else:
            return str(form_summary)


# Example usage
if __name__ == "__main__":
    
    # Initialize the assistant (without LLM for this demo)
    assistant = LeaveFormAssistant()
    
    # Start the conversation
    print(assistant.start_conversation())
    print("\n" + "="*60 + "\n")
    
    # Simulate user interactions
    user_inputs = [
        "Hi, I need annual leave from 25-03-2026 09:00 to 26-03-2026 18:00",
    ]
    
    for user_input in user_inputs:
        print(f"User: {user_input}\n")
        result = assistant.process_message(user_input)
        print(f"Assistant: {result['response']}\n")
        print(f"Completion: {result['completion_percentage']}%")
        print(f"Errors: {result['errors']}")
        print(f"Next Action: {result['next_action']}\n")
        print("="*60 + "\n")
        
        if result['is_form_complete']:
            print("Form is complete! Proceeding to confirmation...")
            confirmation_result = assistant.confirm_and_submit("confirm")
            print(f"Assistant: {confirmation_result['response']}\n")
            print(f"Status: {confirmation_result['status']}\n")
            break
