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
                
                Employee Information:
                - Employee ID: 2-20 characters, uppercase letters, numbers, or hyphens
                - Employee Name: 2-100 characters, letters/spaces/hyphens/apostrophes
                - Manager Name: 2-100 characters, letters/spaces/hyphens/apostrophes
                - Department: Must be from (Engineering, Sales, HR, Finance, Marketing, Operations, Other)
                
                Contact Information:
                - Email: Valid email format
                - Phone (optional): If provided, valid phone format
                
                Leave Details:
                - Leave Type: Must be valid (Sick Left, Casual, Earned, Maternity, Paternity, Unpaid, Bereavement)
                - Start Date: Must be in the future (not past)
                - End Date: Must be after start date
                - Leave Duration: Cannot exceed 60 days
                - WARNING if duration > 30 days: Requires manager approval
                
                Reason:
                - Reason: 5-500 characters
                
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
                6. Approval Requirements: Any special approvals needed
                
                Format it in a clear, scannable way.
            """),
            expected_output="Validation summary report",
            agent=agent,
        )
