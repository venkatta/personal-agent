"""
Main Crew Orchestrator for Leave Form Assistant
Coordinates all agents and their tasks
"""
from crewai import Crew, Agent, Task
from typing import Optional, Dict, Any
import json
from datetime import datetime


class LeaveFormCrew:
    """Orchestrates the leave form submission process"""

    def __init__(self, llm):
        """Initialize the crew with all agents and tasks"""
        self.llm = llm
        self.form_data: Dict[str, Any] = {}
        self.validation_errors: list = []
        self.validation_warnings: list = []
        self.completion_percentage = 0
        self.conversation_history: list = []

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the entire workflow
        
        Flow:
        1. Intent Recognition - Understand what user wants
        2. Content Extraction - Parse form fields
        3. Validation - Check for errors
        4. Response - Communicate issues or ask for more info
        5. Confirmation - Get user approval
        """
        
        # Log user input
        self.conversation_history.append({
            "type": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        # Step 1: Recognize Intent
        intent_result = self._recognize_intent(user_input)
        
        # Step 2: Extract Content
        extraction_result = self._extract_content(user_input)
        self.form_data.update(extraction_result)

        # Calculate completion
        self._calculate_completion()

        # Step 3: Validate
        if self._should_validate():
            validation_result = self._validate_form()
            self.validation_errors = validation_result.get('errors', [])
            self.validation_warnings = validation_result.get('warnings', [])

        # Step 4: Generate Response
        if self.validation_errors:
            response = self._generate_error_response()
        elif self._is_form_complete():
            response = self._generate_confirmation_prompt()
        else:
            response = self._generate_clarification_request()

        # Log agent response
        self.conversation_history.append({
            "type": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "intent": intent_result,
            "extracted_data": extraction_result,
            "form_data": self.form_data,
            "completion_percentage": self.completion_percentage,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "response": response,
            "is_form_complete": self._is_form_complete(),
            "conversation_history": self.conversation_history[-2:]  # Last message pair
        }

    def confirm_submission(self, confirmation: str) -> Dict[str, Any]:
        """Handle user confirmation or rejection of form"""
        
        self.conversation_history.append({
            "type": "user",
            "content": confirmation,
            "timestamp": datetime.now().isoformat()
        })

        if confirmation.lower() in ['yes', 'confirm', 'submit', 'proceed', '✅']:
            response = self._generate_confirmation_success()
            status = "SUBMITTED"
        elif confirmation.lower() in ['no', 'cancel', 'reject', 'back', '❌']:
            response = self._generate_cancellation_message()
            status = "CANCELLED"
            self._reset_form()
        else:
            response = self._generate_clarification_about_confirmation()
            status = "PENDING"

        self.conversation_history.append({
            "type": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "status": status,
            "response": response,
            "form_data": self.form_data if status == "SUBMITTED" else None,
            "conversation_history": self.conversation_history
        }

    def edit_field(self, field_name: str, new_value: Any) -> Dict[str, Any]:
        """Allow user to edit a specific field"""
        
        self.conversation_history.append({
            "type": "user",
            "content": f"Edit {field_name}: {new_value}",
            "timestamp": datetime.now().isoformat()
        })

        old_value = self.form_data.get(field_name)
        self.form_data[field_name] = new_value
        self._calculate_completion()

        # Re-validate after edit
        if self._should_validate():
            validation_result = self._validate_form()
            self.validation_errors = validation_result.get('errors', [])
            self.validation_warnings = validation_result.get('warnings', [])

        response = self._generate_field_edit_acknowledgment(field_name, old_value, new_value)

        self.conversation_history.append({
            "type": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "field_edited": field_name,
            "old_value": old_value,
            "new_value": new_value,
            "response": response,
            "validation_errors": self.validation_errors
        }

    def get_form_summary(self) -> Dict[str, Any]:
        """Return the current form state as a summary"""
        return {
            "employee_id": self.form_data.get('employee_id', ''),
            "employee_name": self.form_data.get('employee_name', ''),
            "department": self.form_data.get('department', ''),
            "leave_type": self.form_data.get('leave_type', ''),
            "start_date": self.form_data.get('start_date', ''),
            "end_date": self.form_data.get('end_date', ''),
            "reason": self.form_data.get('reason', ''),
            "contact_email": self.form_data.get('contact_email', ''),
            "contact_phone": self.form_data.get('contact_phone', ''),
            "manager_name": self.form_data.get('manager_name', ''),
            "cover_details": self.form_data.get('cover_details', ''),
            "completion_percentage": self.completion_percentage,
            "missing_fields": self._get_missing_required_fields()
        }

    # Private helper methods

    def _recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """Step 1: Recognize user intent"""
        # Simplified intent recognition - in production would use LLM
        intent_keywords = {
            "new_submission": ["apply", "submit", "request", "leave", "request leave", "need leave"],
            "clarification": ["explain", "what", "help", "don't understand", "confused", "how"],
            "update": ["change", "update", "edit", "modify", "different"],
            "status_check": ["status", "check", "track", "progress", "where"],
            "cancel": ["cancel", "reject", "withdraw", "remove"]
        }

        intent = "new_submission"  # default
        for possible_intent, keywords in intent_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                intent = possible_intent
                break

        return {
            "intent": intent,
            "confidence": "high" if intent != "new_submission" else "medium",
            "indicators": "User input contains keywords matching detected intent"
        }

    def _extract_content(self, user_input: str) -> Dict[str, Any]:
        """Step 2: Extract form fields from user input"""
        from leave_form_assistant.tools import ContentExtractor

        return ContentExtractor.parse_form_text(user_input)

    def _validate_form(self) -> Dict[str, Any]:
        """Step 3: Validate all form data"""
        from leave_form_assistant.tools import LeaveFormValidator

        is_valid, errors, warnings = LeaveFormValidator.validate_all_fields(self.form_data)

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }

    def _should_validate(self) -> bool:
        """Check if form has enough data to validate"""
        required_fields = ['employee_id', 'employee_name', 'contact_email']
        return all(field in self.form_data for field in required_fields)

    def _is_form_complete(self) -> bool:
        """Check if all required fields are filled"""
        required_fields = [
            'employee_id', 'employee_name', 'department', 'leave_type',
            'start_date', 'end_date', 'reason', 'contact_email', 'manager_name'
        ]
        return all(field in self.form_data for field in required_fields)

    def _calculate_completion(self) -> None:
        """Calculate form completion percentage"""
        all_fields = [
            'employee_id', 'employee_name', 'department', 'leave_type',
            'start_date', 'end_date', 'reason', 'contact_email', 'contact_phone',
            'manager_name', 'cover_details'
        ]
        filled_fields = sum(1 for field in all_fields if field in self.form_data)
        self.completion_percentage = round((filled_fields / len(all_fields)) * 100)

    def _get_missing_required_fields(self) -> list:
        """Get list of required fields that are still missing"""
        required_fields = [
            'employee_id', 'employee_name', 'department', 'leave_type',
            'start_date', 'end_date', 'reason', 'contact_email', 'manager_name'
        ]
        return [field for field in required_fields if field not in self.form_data]

    def _generate_error_response(self) -> str:
        """Step 4: Generate response about validation errors"""
        response = "I found some issues that need to be corrected:\n\n"
        for i, error in enumerate(self.validation_errors, 1):
            response += f"{i}. {error}\n"
        response += "\nPlease provide the corrected information."
        return response

    def _generate_clarification_request(self) -> str:
        """Step 4: Generate request for missing fields"""
        missing = self._get_missing_required_fields()
        if not missing:
            return "All required fields are complete!"

        response = f"Great! I have {self.completion_percentage}% of your information. "
        response += f"Just need a few more details:\n\n"
        
        # Ask for first 1-2 missing fields
        for field in missing[:2]:
            field_labels = {
                'employee_id': 'Your Employee ID',
                'employee_name': 'Your Full Name',
                'department': 'Your Department (Engineering, Sales, HR, Finance, Marketing, Operations, Other)',
                'leave_type': 'Type of Leave (Sick, Casual, Earned, Maternity, Paternity, Unpaid, Bereavement)',
                'start_date': 'Leave Start Date (format: DD-MM-YYYY)',
                'end_date': 'Leave End Date (format: DD-MM-YYYY)',
                'reason': 'Reason for your leave (at least 5 characters)',
                'contact_email': 'Your Email Address',
                'manager_name': 'Your Manager\'s Name'
            }
            response += f"• {field_labels.get(field, field.replace('_', ' ').title())}\n"

        return response

    def _generate_confirmation_prompt(self) -> str:
        """Step 5: Generate form summary and confirmation request"""
        summary = self.get_form_summary()
        
        response = """
📋 LEAVE REQUEST FORM SUMMARY
════════════════════════════════════════

👤 EMPLOYEE INFORMATION
  • Employee ID: {employee_id}
  • Full Name: {employee_name}
  • Department: {department}
  • Manager: {manager_name}

📅 LEAVE DETAILS
  • Leave Type: {leave_type}
  • Start Date: {start_date}
  • End Date: {end_date}
  • Reason: {reason}

📞 CONTACT INFORMATION
  • Email: {contact_email}
  • Phone: {contact_phone}
  • Coverage: {cover_details}

✅ All information validated and complete!

Please review the above and confirm:
✅ CONFIRM - Submit the form
✏️ EDIT - Which field would you like to modify?
❌ CANCEL - Start over
""".format(**summary)
        
        return response

    def _generate_confirmation_success(self) -> str:
        """Generate success message after confirmation"""
        reference_id = f"LR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        response = f"""
✅ SUCCESS! Your leave request has been submitted successfully!

📌 Reference ID: {reference_id}

📋 NEXT STEPS:
1. Your manager will receive the request within 24 hours
2. You can expect an approval/rejection response within 3 business days
3. Check your email for status updates
4. You can track the status using reference ID: {reference_id}

📞 If you have any questions, please contact HR support.

Thank you for using the Leave Form Assistant!
"""
        return response

    def _generate_cancellation_message(self) -> str:
        """Generate message when user cancels"""
        missing_fields = self._get_missing_required_fields()
        
        response = f"""
👋 No problem! Your form has been cancelled.

📊 Your Progress: {self.completion_percentage}% complete

If you'd like to resume later, you can:
1. Start a new form fresh
2. Contact HR support to discuss your needs
3. Return to this form when ready

Is there anything else I can help you with?
"""
        return response

    def _generate_clarification_about_confirmation(self) -> str:
        """Clarify what user should do about confirmation"""
        return """
I need your confirmation to proceed. Please choose one of:

✅ CONFIRM - If everything looks correct, submit the form
✏️ EDIT - If you'd like to change any information
❌ CANCEL - If you want to start over

Which would you like to do?
"""

    def _generate_field_edit_acknowledgment(self, field_name: str, old_value: Any, new_value: Any) -> str:
        """Generate acknowledgment when field is edited"""
        field_labels = {
            'employee_id': 'Employee ID',
            'employee_name': 'Employee Name',
            'department': 'Department',
            'leave_type': 'Leave Type',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'reason': 'Reason',
            'contact_email': 'Email',
            'contact_phone': 'Phone',
            'manager_name': 'Manager Name',
            'cover_details': 'Coverage Details'
        }
        
        response = f"""
✏️ Updated: {field_labels.get(field_name, field_name.replace('_', ' ').title())}
   Old: {old_value}
   New: {new_value}

Progress: {self.completion_percentage}% complete

What would you like to do?
1. Continue with more changes
2. Review the complete form
"""
        return response

    def _reset_form(self) -> None:
        """Reset form data"""
        self.form_data = {}
        self.validation_errors = []
        self.validation_warnings = []
        self.completion_percentage = 0
