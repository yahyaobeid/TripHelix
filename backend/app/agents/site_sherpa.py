# Import necessary components for agent implementation
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Import the base agent class and AI config
from .base import BaseAgent
from app.core.ai_config import ai_config

class TravelPreferences(BaseModel):
    """Structured data model for travel preferences"""
    destination: str = Field(..., description="Main travel destination")
    start_date: datetime = Field(..., description="Travel start date")
    end_date: datetime = Field(..., description="Travel end date")
    budget: float = Field(..., description="Total budget for the trip")
    accommodation_type: str = Field(..., description="Preferred type of accommodation")
    travel_style: str = Field(..., description="Travel style (e.g., luxury, budget, adventure)")
    interests: List[str] = Field(..., description="List of interests and activities")
    special_requirements: List[str] = Field(default_factory=list, description="Any special requirements")
    group_size: int = Field(..., description="Number of people traveling")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Any dietary restrictions")

class SiteSherpa(BaseAgent):
    """
    SiteSherpa agent specializes in gathering travel information and preferences from users.
    This agent acts as the first point of contact, collecting necessary details for trip planning.
    """
    
    def __init__(self, tools: List[Any]):
        """
        Initialize the SiteSherpa agent with its specialized system prompt.
        
        Args:
            tools: List of tools the agent can use
        """
        # Initialize OpenAI chat model
        llm = ChatOpenAI(
            model=ai_config.OPENAI_MODEL,
            temperature=ai_config.OPENAI_TEMPERATURE,
            max_tokens=ai_config.OPENAI_MAX_TOKENS,
            api_key=ai_config.OPENAI_API_KEY
        )
        
        # Define the system prompt that guides the agent's behavior
        system_prompt = """You are SiteSherpa, a friendly and knowledgeable travel assistant specializing in gathering 
        information about users' travel preferences and requirements. Your goal is to:
        1. Understand the user's travel needs and preferences
        2. Gather necessary information about destinations, dates, and requirements
        3. Ask relevant follow-up questions to ensure you have all needed information
        4. Maintain a friendly and professional tone
        5. Be thorough but concise in your questions
        6. Generate a detailed itinerary based on collected information
        7. Create a structured JSON schema for the next agent
        
        Required Information to Collect:
        - Destination(s)
        - Travel dates (start and end)
        - Budget constraints
        - Accommodation preferences
        - Travel style (luxury, budget, adventure, etc.)
        - Interests and activities
        - Special requirements
        - Group size
        - Dietary restrictions
        
        Once all information is collected, generate:
        1. A detailed day-by-day itinerary
        2. A structured JSON schema for the next agent
        """
        
        # Initialize the base agent with the specialized prompt
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=system_prompt,
            name="SiteSherpa"
        )
        self.travel_preferences = None
        
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
        
    def _generate_itinerary(self) -> str:
        """Generate a detailed itinerary based on collected preferences"""
        if not self.travel_preferences:
            return "Please provide all necessary travel information first."
            
        # Use the LLM to generate a detailed itinerary
        itinerary_prompt = f"""Based on the following travel preferences, create a detailed day-by-day itinerary:
        Destination: {self.travel_preferences.destination}
        Dates: {self.travel_preferences.start_date} to {self.travel_preferences.end_date}
        Budget: ${self.travel_preferences.budget}
        Style: {self.travel_preferences.travel_style}
        Interests: {', '.join(self.travel_preferences.interests)}
        Group Size: {self.travel_preferences.group_size}
        Special Requirements: {', '.join(self.travel_preferences.special_requirements)}
        
        Please provide a detailed day-by-day itinerary including:
        1. Daily activities and attractions
        2. Recommended restaurants
        3. Transportation options
        4. Estimated costs
        5. Time allocations
        """
        
        return self.llm.predict(itinerary_prompt)
        
    def _generate_booking_schema(self) -> Dict[str, Any]:
        """Generate a structured JSON schema for the next agent"""
        if not self.travel_preferences:
            return {}
            
        return {
            "booking_requirements": {
                "flights": {
                    "origin": "To be determined",
                    "destination": self.travel_preferences.destination,
                    "dates": {
                        "departure": self.travel_preferences.start_date.isoformat(),
                        "return": self.travel_preferences.end_date.isoformat()
                    },
                    "passengers": self.travel_preferences.group_size
                },
                "accommodation": {
                    "type": self.travel_preferences.accommodation_type,
                    "location": self.travel_preferences.destination,
                    "check_in": self.travel_preferences.start_date.isoformat(),
                    "check_out": self.travel_preferences.end_date.isoformat(),
                    "guests": self.travel_preferences.group_size,
                    "special_requirements": self.travel_preferences.special_requirements
                },
                "activities": {
                    "interests": self.travel_preferences.interests,
                    "dietary_restrictions": self.travel_preferences.dietary_restrictions
                },
                "budget": {
                    "total": self.travel_preferences.budget,
                    "style": self.travel_preferences.travel_style
                }
            }
        }
        
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: The user's message to process
            context: Optional additional context
            
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
        
        # Check if we have all necessary information
        if "all information collected" in response["output"].lower():
            # Generate itinerary and booking schema
            itinerary = self._generate_itinerary()
            booking_schema = self._generate_booking_schema()
            
            # Combine the response with itinerary and schema
            final_response = f"{response['output']}\n\nHere's your detailed itinerary:\n{itinerary}\n\nBooking schema has been prepared for the next agent."
            return final_response
            
        return response["output"]
