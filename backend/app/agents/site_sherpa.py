# Import necessary components for agent implementation
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage

# Import the base agent class
from .base import BaseAgent

class SiteSherpa(BaseAgent):
    """
    SiteSherpa agent specializes in gathering travel information and preferences from users.
    This agent acts as the first point of contact, collecting necessary details for trip planning.
    """
    
    def __init__(self, llm: BaseChatModel, tools: List[Any]):
        """
        Initialize the SiteSherpa agent with its specialized system prompt.
        
        Args:
            llm: The language model instance
            tools: List of tools the agent can use
        """
        # Define the system prompt that guides the agent's behavior
        system_prompt = """You are SiteSherpa, a friendly and knowledgeable travel assistant specializing in gathering 
        information about users' travel preferences and requirements. Your goal is to:
        1. Understand the user's travel needs and preferences
        2. Gather necessary information about destinations, dates, and requirements
        3. Ask relevant follow-up questions to ensure you have all needed information
        4. Maintain a friendly and professional tone
        5. Be thorough but concise in your questions
        
        Remember to:
        - Ask about budget constraints
        - Inquire about travel dates and duration
        - Understand accommodation preferences
        - Ask about any special requirements or preferences
        - Gather information about activities and interests
        """
        
        # Initialize the base agent with the specialized prompt
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=system_prompt,
            name="SiteSherpa"
        )
        
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the chat prompt template for the SiteSherpa agent.
        This template includes the system message, chat history, and input message.
        """
        return ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),  # System instructions
            MessagesPlaceholder(variable_name="chat_history"),  # Conversation history
            HumanMessage(content="{input}"),  # User's input
            MessagesPlaceholder(variable_name="agent_scratchpad"),  # Agent's thinking process
        ])
        
    def _create_agent(self) -> AgentExecutor:
        """
        Create the agent executor with OpenAI functions agent.
        This combines the language model, tools, and prompt template.
        """
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_prompt()
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True  # Enable verbose output for debugging
        )
        
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: The user's message to process
            context: Optional additional context (not used in this implementation)
            
        Returns:
            The agent's response as a string
        """
        # Create a new agent instance for this interaction
        agent = self._create_agent()
        
        # Process the message with the agent
        response = await agent.ainvoke({
            "input": message,
            "chat_history": self.memory
        })
        
        # Store the interaction in memory
        self.add_to_memory("user", message)
        self.add_to_memory("assistant", response["output"])
        
        return response["output"]
