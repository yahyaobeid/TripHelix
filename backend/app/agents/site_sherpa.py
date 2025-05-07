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
        system_prompt = """You are SiteSherpa, a friendly and knowledgeable travel assistant. Your goal is to have a natural conversation with the user to gather all necessary information for creating their perfect travel itinerary.

        Follow this conversation flow:
        1. Start with a warm greeting and ask if they have a specific destination in mind.
        2. If they have a destination, ask about their travel dates. If not, help them explore options based on their interests.
        3. Once you have the destination and dates, ask about:
           - Their travel style (luxury, budget, adventure, etc.)
           - Accommodation preferences
           - Interests and activities they enjoy
           - Group size and composition
           - Any special requirements or dietary restrictions
           - Their budget range
        4. After gathering all information, generate a detailed itinerary and offer to save it.

        Important rules:
        - Ask ONE question at a time
        - Wait for the user's response before asking the next question
        - Be conversational and friendly
        - Provide helpful suggestions when needed
        - Confirm information before moving to the next topic
        - When all information is gathered, generate a detailed itinerary

        When generating the itinerary, include:
        - Day-by-day breakdown
        - Morning, afternoon, and evening activities
        - Recommended restaurants and dining options
        - Transportation details
        - Estimated costs
        - Booking links where applicable
        - Special notes or recommendations
        """
        
        # Initialize the base agent with the specialized prompt
        super().__init__(
            llm=llm,
            tools=tools,
            system_prompt=system_prompt,
            name="SiteSherpa"
        )
        self.travel_preferences = None
        self.conversation_state = {
            "has_destination": False,
            "has_dates": False,
            "has_preferences": False,
            "has_budget": False,
            "has_special_requirements": False,
            "all_info_collected": False
        }
        
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
        itinerary_prompt = f"""Based on the following travel preferences, create a detailed day-by-day itinerary in HTML format:
        Destination: {self.travel_preferences.destination}
        Dates: {self.travel_preferences.start_date} to {self.travel_preferences.end_date}
        Budget: ${self.travel_preferences.budget}
        Style: {self.travel_preferences.travel_style}
        Interests: {', '.join(self.travel_preferences.interests)}
        Group Size: {self.travel_preferences.group_size}
        Special Requirements: {', '.join(self.travel_preferences.special_requirements)}
        
        Please provide a detailed day-by-day itinerary in HTML format with the following structure:
        <div class="itinerary-day">
          <h3>Day X: [Date]</h3>
          <div class="itinerary-time">Morning</div>
          <div class="itinerary-activity">[Activity]</div>
          <div class="itinerary-time">Afternoon</div>
          <div class="itinerary-activity">[Activity]</div>
          <div class="itinerary-time">Evening</div>
          <div class="itinerary-activity">[Activity]</div>
          <div class="itinerary-note">[Notes/Recommendations]</div>
        </div>
        
        Include:
        1. Daily activities and attractions
        2. Recommended restaurants
        3. Transportation options
        4. Estimated costs
        5. Time allocations
        6. Booking links where applicable
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
            # Generate itinerary
            itinerary = self._generate_itinerary()
            
            # Combine the response with itinerary
            final_response = f"{response['output']}\n\nHere's your detailed itinerary:\n{itinerary}\n\nWould you like to save this itinerary or make any adjustments?"
            return final_response
            
        return response["output"]
