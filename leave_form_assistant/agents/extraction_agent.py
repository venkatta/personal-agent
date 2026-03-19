"""
Content Extraction Agent
Extracts and parses leave form information from user input
"""
from crewai import Agent, Task
from textwrap import dedent


class ExtractionAgent:
    """Agent responsible for extracting form field values"""

    @staticmethod
    def create_agent(llm) -> Agent:
        """Create the content extraction agent"""
        return Agent(
            role="Form Data Extraction Specialist",
            goal="Extract and organize all required information from user input for the leave form",
            backstory=dedent("""
                You are an expert at parsing and extracting information from unstructured user input.
                You can identify employee details, dates, reasons, and other information from casual
                conversation or semi-structured text. You maintain accuracy while being flexible
                with different formats and writing styles.
            """),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def create_field_extraction_task(agent: Agent) -> Task:
        """Create task to extract form fields"""
        return Task(
            description=dedent("""
                Extract all relevant information from the user's input to populate the leave form fields:
                
                Required fields to extract:
                1. employee_id - Employee ID (e.g., EMP001, E-123)
                2. employee_name - Full name of the employee
                3. department - Department (Engineering, Sales, HR, Finance, Marketing, Operations, Other)
                4. leave_type - Type of leave (Sick Leave, Casual Leave, Earned Leave, etc.)
                5. start_date - Start date of leave
                6. end_date - End date of leave
                7. reason - Reason for the leave
                8. contact_email - Email address for contact during leave
                9. contact_phone - Phone number (optional)
                10. manager_name - Name of the reporting manager
                11. cover_details - Coverage or backup arrangements (optional)
                
                For each field, provide:
                - Extracted value
                - Confidence level (high/medium/low)
                - Original source text
                - If missing, suggestions on how to ask the user for it
            """),
            expected_output="JSON with all extracted fields, confidence levels, and source information",
            agent=agent,
        )

    @staticmethod
    def create_clarification_task(agent: Agent, missing_fields: list) -> Task:
        """Create task to ask for missing information"""
        return Task(
            description=dedent(f"""
                The following fields are missing or unclear from the user input: {missing_fields}
                
                Create a friendly and conversational message to ask the user for these specific fields.
                
                Tips:
                - Ask one or two questions at a time
                - Provide examples of expected format
                - Be encouraging and patient
                - Make it feel like a natural conversation, not an interrogation
            """),
            expected_output="Friendly clarification questions for missing fields",
            agent=agent,
        )

    @staticmethod
    def create_field_summary_task(agent: Agent) -> Task:
        """Create task to summarize extracted fields"""
        return Task(
            description=dedent("""
                Provide a clear summary of all extracted and entered form fields in a structured format.
                
                Present the information in a readable format:
                - Employee Information (ID, Name, Department, Manager)
                - Leave Details (Type, Start Date, End Date, Duration)
                - Contact Information (Email, Phone)
                - Leave Reason
                - Coverage Arrangements
                
                Highlight any fields that need attention or clarification.
            """),
            expected_output="Structured summary of all form fields",
            agent=agent,
        )
