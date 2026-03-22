"""
Validation Agent
Validates all form inputs and provides error/warning feedback
"""
from crewai import Agent, Task
from textwrap import dedent


class ValidationAgent:
    """Agent responsible for validating form inputs"""

    @staticmethod
    def create_agent(llm) -> Agent:
        """Create the validation agent"""
        return Agent(
            role="Form Validation Specialist",
            goal="Validate all form inputs against business rules and provide clear feedback on any issues",
            backstory=dedent("""
                You are an expert at data validation and business rule enforcement.
                You understand leave policies, date constraints, employee management rules,
                and communication standards. You provide constructive feedback to help users
                correct their inputs and ensure compliance with organizational policies.
            """),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def create_validation_task(agent: Agent) -> Task:
        """Create task to validate all form fields"""
        return Task(
            description=dedent("""
                Validate all form fields against the following rules:
                
                Leave Details:
                - Leave Type: Must be valid (annual, medical, maternity, paternity, child_care, compassionate, exam, family_care, hospitalisation, national_service, extended_maternity, shared_parental, adoption_4_weeks, adoption_8_weeks, sick_leave_no_medical_certificate, special, time_off, unpaid_infant_care, unpaid_medical, unpaid_maternity, marriage, unpaid_leave, unpaid_hours)
                - Start Date and Start Time: Combined start must be in the future
                - End Date and End Time: Combined end must be after the combined start
                - Leave Duration: Cannot exceed 60 days
                - WARNING if duration > 30 days: Requires manager approval
                
                For each violation, provide:
                - Field name
                - Validation rule
                - Current value
                - Error message
                - Suggestion for correction
            """),
            expected_output="Detailed validation report with errors and warnings",
            agent=agent,
        )

    @staticmethod
    def create_error_response_task(agent: Agent, errors: list) -> Task:
        """Create task to provide error feedback to user"""
        return Task(
            description=dedent(f"""
                The following validation errors were found: {errors}
                
                Create a friendly and helpful error message that:
                1. Acknowledges the issue
                2. Clearly explains what went wrong
                3. Provides specific guidance on how to fix it
                4. Maintains a positive tone
                5. Encourages the user to continue
                
                Be empathetic but also clear about requirements.
            """),
            expected_output="User-friendly error message with correction guidance",
            agent=agent,
        )

    @staticmethod
    def create_warning_notification_task(agent: Agent, warnings: list) -> Task:
        """Create task to notify user of warnings"""
        return Task(
            description=dedent(f"""
                Inform the user about these warnings: {warnings}
                
                Create a message that:
                1. Explains the warning (e.g., "Leave exceeds 30 days")
                2. States the business implication (e.g., "Manager approval required")
                3. Asks if they want to proceed or make changes
                4. Provides next steps based on their decision
                
                Keep the tone informative but not alarming.
            """),
            expected_output="Clear warning notification with options",
            agent=agent,
        )

    @staticmethod
    def create_summary_task(agent: Agent) -> Task:
        """Create task to provide validation summary"""
        return Task(
            description=dedent("""
                Provide a comprehensive validation summary showing:
                
                1. Validation Status: ✓ PASSED / ✗ FAILED
                2. Fields Checked: List all fields validated
                3. Errors Found: Count and list (if any)
                4. Warnings Found: Count and list (if any)
                5. Action Items: What needs to be done next
                6. Leave Window: Show the validated start and end schedule
                
                Format it in a clear, scannable way.
            """),
            expected_output="Validation summary report",
            agent=agent,
        )
