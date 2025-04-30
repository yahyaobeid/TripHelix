# Import necessary components for agent implementation
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

class BaseAgent:
    """
    Base class for AI agents in the TripHelix system.
    This class provides common functionality for both SiteSherpa and Concierge agents.
    """
    
    def __init__(
        self,
        llm: BaseChatModel,  # The language model to use (e.g., GPT-4)
        tools: List[Any],  # List of tools the agent can use
        system_prompt: str,  # The system prompt defining the agent's behavior
        name: str  # The name of the agent
    ):
        """
        Initialize the base agent with necessary components.
        
        Args:
            llm: The language model instance
            tools: List of tools the agent can use
            system_prompt: The system prompt defining agent behavior
            name: The name of the agent
        """
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.name = name
        self.memory: List[Dict[str, str]] = []  # Store conversation history
        
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the chat prompt template for the agent.
        This method must be implemented by child classes.
        """
        raise NotImplementedError
        
    def _create_agent(self) -> AgentExecutor:
        """
        Create the agent executor with the appropriate tools and prompt.
        This method must be implemented by child classes.
        """
        raise NotImplementedError
        
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a message and return the agent's response.
        This method must be implemented by child classes.
        
        Args:
            message: The user's message to process
            context: Optional additional context for the agent
            
        Returns:
            The agent's response as a string
        """
        raise NotImplementedError
        
    def add_to_memory(self, role: str, content: str) -> None:
        """
        Add a message to the agent's conversation memory.
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The content of the message
        """
        self.memory.append({"role": role, "content": content})
        
    def get_memory(self) -> List[Dict[str, str]]:
        """
        Get the agent's conversation memory.
        
        Returns:
            List of message dictionaries with role and content
        """
        return self.memory 