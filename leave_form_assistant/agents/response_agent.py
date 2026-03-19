"""
Response Agent
Manages communication with the user and guides them through validation issues
"""
from crewai import Agent, Task
from textwrap import dedent


class ResponseAgent:
    """Agent responsible for responding to user input"""

    @staticmethod
    def create_agent(llm) -> Agent:
        """Create the response agent"""
        return Agent(
            role="User Communication Specialist",
            goal="Provide clear, empathetic, and constructive communication to guide users through the leave form process",
            backstory=dedent("""
                You are an excellent communicator with a talent for explaining complex requirements
                in simple, friendly terms. You're patient, professional, and skilled at helping
                users understand what's needed and how to provide it correctly. You celebrate
                progress and encourage users throughout the process.
            """),
            llm=llm,
            verbose=True,
        )

    @staticmethod
    def create_validation_error_response_task(agent: Agent) -> Task:
        """Create task to respond to validation errors"""
        return Task(
            description=dedent("""
                When validation errors occur, provide a response that:
                
                1. Starts with empathy ("I found a couple of things we need to clarify...")
                2. Lists each error in plain language
                3. Explains why it's important
                4. Shows the expected format with examples
                5. Asks for the corrected information
                6. Offers to help if they're unsure
                
                Structure:
                - Error Overview
                - Error Details (one by one)
                - What's Needed (specific examples)
                - Call to Action (how to provide the correction)
            """),
            expected_output="Empathetic and helpful error response message",
            agent=agent,
        )

    @staticmethod
    def create_clarification_request_task(agent: Agent) -> Task:
        """Create task to request clarification on fields"""
        return Task(
            description=dedent("""
                Create a conversational request for missing or unclear information.
                
                Guidelines:
                1. Keep it natural and conversational
                2. Ask 1-2 fields at a time maximum
                3. Show examples for complex fields
                4. For dates, explain the format expected
                5. For text fields, give character limits if relevant
                6. For selections, list available options
                7. Make it clear what's optional vs required
                
                Example tone:
                "I have your basic info! Just need a couple more details...
                Could you tell me your department? (We have: Engineering, Sales, HR, Finance, Marketing, Operations, or Other)"
            """),
            expected_output="Conversational clarification request",
            agent=agent,
        )

    @staticmethod
    def create_progress_update_task(agent: Agent, completed_fields: int, total_fields: int) -> Task:
        """Create task to provide progress feedback"""
        return Task(
            description=dedent(f"""
                Create a progress update showing that {completed_fields} out of {total_fields} fields are complete.
                
                Include:
                1. Percentage complete ({int((completed_fields/total_fields)*100)}%)
                2. Completed fields (checkmarks and summary)
                3. Remaining fields to complete
                4. Encouragement
                5. Next step
                
                Make the user feel their progress is being recognized.
            """),
            expected_output="Progress update message with percentage and next steps",
            agent=agent,
        )

    @staticmethod
    def create_correction_acknowledgment_task(agent: Agent) -> Task:
        """Create task to acknowledge field corrections"""
        return Task(
            description=dedent("""
                When the user provides corrections or additional information, acknowledge it positively.
                
                Message should:
                1. Thank them for the information
                2. Confirm what was updated
                3. Show current completion status
                4. Ask for next missing piece (if any)
                5. Keep the momentum positive
                
                Example: "Perfect! I've updated your manager information. 
                Now just need your preferred contact email..."
            """),
            expected_output="Positive acknowledgment with next steps",
            agent=agent,
        )

    @staticmethod
    def create_generic_help_task(agent: Agent) -> Task:
        """Create task to provide general help"""
        return Task(
            description=dedent("""
                Create a helpful response for when the user asks for help or is confused about what to do.
                
                Include:
                1. Brief explanation of the leave form process (3-4 steps)
                2. Assurance that the system will guide them through it
                3. Offer of specific help (explain any field, restart, check status, etc.)
                4. Tone should be supportive and encouraging
                
                Remember: Our goal is to make this as easy as possible for them.
            """),
            expected_output="Helpful guidance message",
            agent=agent,
        )
