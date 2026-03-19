"""
Intent Recognition Agent
Understands what the user wants to do with a leave form
"""
from crewai import Agent, Task
from textwrap import dedent


class IntentAgent:
    """Agent responsible for understanding user intent"""

    @staticmethod
    def create_agent(llm) -> Agent:
        """Create the intent recognition agent"""
        return Agent(
            role="Intent Recognition Specialist",
            goal="Understand user's intent regarding leave form submission and guide them through the process",
            backstory=dedent("""
                You are an expert at understanding employee intentions regarding leave requests.
                You can identify what type of leave the user is trying to apply for, whether they're
                submitting a new form, updating an existing one, or checking on a previous request.
                You're empathetic and guide the conversation naturally.
            """),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def create_intent_recognition_task(agent: Agent) -> Task:
        """Create task to recognize user intent"""
        return Task(
            description=dedent("""
                Analyze the user's input and determine their intent regarding the leave form.
                
                Possible intents:
                1. NEW_SUBMISSION - User wants to submit a new leave request
                2. CLARIFICATION - User needs help understanding what information is needed
                3. UPDATE - User wants to update an existing form
                4. STATUS_CHECK - User wants to check on a previous request
                5. CANCEL - User wants to cancel a request
                
                Provide:
                - The identified intent
                - Confidence level (high/medium/low)
                - Key indicators that led to this conclusion
                - Next steps to take based on the intent
            """),
            expected_output="JSON with identified intent, confidence level, and next steps",
            agent=agent,
        )

    @staticmethod
    def create_user_guidance_task(agent: Agent) -> Task:
        """Create task to guide user through the process"""
        return Task(
            description=dedent("""
                Based on the identified intent, provide clear guidance to the user about what
                information will be needed for the leave form submission.
                
                Include:
                1. A warm greeting
                2. Confirmation of their intent
                3. List of required fields (Employee ID, Name, Department, Leave Type, Dates, Reason, etc.)
                4. Optional fields
                5. Timeline expectations
                6. Assurance that the process is simple and can be done step by step
            """),
            expected_output="Friendly and clear guidance message for the user",
            agent=agent,
        )
