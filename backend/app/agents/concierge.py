# Import necessary components for agent implementation
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage

# Import the base agent class
from .base import BaseAgent

class Concierge(BaseAgent):
    """
    Concierge agent specializes in making travel arrangements and bookings.
    This agent handles the actual booking process after SiteSherpa has gathered the necessary information.
    """
    
    def __init__(self, llm: BaseChatModel, tools: List[Any]):
        """
        Initialize the Concierge agent with its specialized system prompt.
        
        Args:
            llm: The language model instance
            tools: List of tools the agent can use
        """
        # Define the system prompt that guides the agent's behavior
        system_prompt = """You are Concierge, a professional travel booking assistant specializing in making 
        travel arrangements and bookings. Your responsibilities include:
        1. Making flight bookings based on user preferences
        2. Booking accommodations that match user requirements
        3. Arranging transportation and transfers
        4. Managing bookings and modifications
        5. Providing booking confirmations and details
        
        Remember to:
        - Verify all booking details before confirming
        - Check for any special requirements or preferences
        - Ensure all bookings are within the specified budget
        - Provide clear booking confirmations and reference numbers
        - Handle any booking modifications or cancellations professionally
        """
        
        # Initialize the base agent with the specialized prompt
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=system_prompt,
            name="Concierge"
        )
        
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the chat prompt template for the Concierge agent.
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
            context: Optional additional context for the booking process
            
        Returns:
            The agent's response as a string
        """
        # Create a new agent instance for this interaction
        agent = self._create_agent()
        
        # Process the message with the agent, including any context
        response = await agent.ainvoke({
            "input": message,
            "chat_history": self.memory,
            "context": context or {}  # Include context if provided
        })
        
        # Store the interaction in memory
        self.add_to_memory("user", message)
        self.add_to_memory("assistant", response["output"])
        
        return response["output"]
