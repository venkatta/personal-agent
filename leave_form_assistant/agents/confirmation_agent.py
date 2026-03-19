"""
Confirmation Agent
Reviews the complete form and obtains user confirmation before submission
"""
from crewai import Agent, Task
from textwrap import dedent


class ConfirmationAgent:
    """Agent responsible for form review and confirmation"""

    @staticmethod
    def create_agent(llm) -> Agent:
        """Create the confirmation agent"""
        return Agent(
            role="Form Review and Confirmation Specialist",
            goal="Present a complete summary of the leave form and obtain user confirmation before final submission",
            backstory=dedent("""
                You are detail-oriented and thorough. You understand the importance of double-checking
                information before submission. You present information in a clear, organized manner that
                makes it easy for users to review and spot any issues. You're professional but friendly,
                and you make the confirmation process feel like a natural final step.
            """),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def create_form_summary_task(agent: Agent) -> Task:
        """Create task to summarize the complete form"""
        return Task(
            description=dedent("""
                Present a comprehensive summary of all collected information in an easy-to-read format.
                
                Format the summary as:
                
                📋 LEAVE REQUEST FORM SUMMARY
                ══════════════════════════════
                
                👤 EMPLOYEE INFORMATION
                ├─ Employee ID: [ID]
                ├─ Full Name: [Name]
                ├─ Department: [Dept]
                └─ Manager: [Manager Name]
                
                📅 LEAVE DETAILS
                ├─ Leave Type: [Type]
                ├─ Start Date: [Date]
                ├─ End Date: [Date]
                ├─ Total Days: [Days]
                └─ Reason: [Reason]
                
                📞 CONTACT INFORMATION
                ├─ Email: [Email]
                ├─ Phone: [Phone]
                └─ Coverage: [Coverage Details]
                
                ✅ STATUS: All information validated and complete
                
                Include any important notes or warnings.
            """),
            expected_output="Formatted form summary ready for review",
            agent=agent,
        )

    @staticmethod
    def create_confirmation_request_task(agent: Agent) -> Task:
        """Create task to request user confirmation"""
        return Task(
            description=dedent("""
                After presenting the summary, ask for confirmation with clear options.
                
                Message should include:
                1. A request to review the information
                2. Clear yes/no/edit options
                3. Explanation of what happens next after confirmation
                4. Assurance that they can make changes if needed
                
                Phrasing: "Please review the information above. If everything looks correct, 
                you can confirm or select what you'd like to change."
                
                Provide these options:
                - ✅ CONFIRM - Submit the form
                - ✏️ EDIT - Which field would you like to modify?
                - ❌ CANCEL - Start over
            """),
            expected_output="Confirmation request with clear action options",
            agent=agent,
        )

    @staticmethod
    def create_confirmation_acknowledgment_task(agent: Agent) -> Task:
        """Create task to acknowledge confirmation"""
        return Task(
            description=dedent("""
                When user confirms, provide a success message that includes:
                
                1. Confirmation: "Your leave request has been submitted successfully!"
                2. Reference number if generated
                3. What happens next (e.g., "Your manager will receive the request within 24 hours")
                4. Timeline for approval (e.g., "You can expect a response within 3 business days")
                5. How to track status (if available)
                6. Contact info for support if issues arise
                
                Tone should be professional yet warm, celebrating their successful submission.
            """),
            expected_output="Success confirmation message with next steps",
            agent=agent,
        )

    @staticmethod
    def create_edit_field_task(agent: Agent, fields_to_edit: list) -> Task:
        """Create task to handle field edits"""
        return Task(
            description=dedent(f"""
                The user wants to edit these fields: {fields_to_edit}
                
                For each field:
                1. Show the current value
                2. Ask for the new value
                3. Explain what format is needed (if applicable)
                4. Validate the new input before moving to the next field
                
                After all edits are collected, confirm the changes and ask if they want
                to review the updated form or proceed with submission.
            """),
            expected_output="Request for field edits with current values shown",
            agent=agent,
        )

    @staticmethod
    def create_rejection_handling_task(agent: Agent) -> Task:
        """Create task to handle user cancellation"""
        return Task(
            description=dedent("""
                If the user chooses to cancel or reject the form submission:
                
                1. Acknowledge their decision respectfully
                2. Ask if they'd like to save the form as a draft for later
                3. Offer to clarify any concerns if that's why they're canceling
                4. Provide information on how to restart the process
                5. Thank them for the interaction
                
                Message tone: Helpful, not judgmental, understanding that forms can be
                reviewed and submitted at a better time.
            """),
            expected_output="Respectful cancellation acknowledgment with next steps",
            agent=agent,
        )
