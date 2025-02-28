import os
import openai
import json
from typing import Dict, Any, List, Optional

class OpenAIIntegration:
    """
    Handles integration with OpenAI for generating natural responses
    for the real estate voice calling agent.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI integration.
        
        Args:
            api_key: OpenAI API key. If None, will try to use environment variable.
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        
        # Set the API key for the OpenAI client
        openai.api_key = self.api_key
        print("OpenAI integration initialized")
    
    def generate_response(self, 
                         client_message: str, 
                         conversation_history: List[Dict[str, str]] = None,
                         property_info: Dict[str, Any] = None,
                         agent_name: str = "Sarah",
                         agent_context: str = None) -> str:
        """
        Generate a response to a client message using OpenAI.
        
        Args:
            client_message: The message from the client
            conversation_history: Previous messages in the conversation
            property_info: Information about the property being discussed
            agent_name: Name of the AI agent
            agent_context: Additional context for the agent
            
        Returns:
            Generated response text
        """
        # Create a system message that guides the AI to respond as a real estate agent
        system_message = f"""You are an experienced real estate agent named {agent_name}. 
        You are professional, knowledgeable, and friendly. Your goal is to help potential clients 
        find properties that match their needs and schedule viewings when appropriate.
        
        Keep your responses concise but informative. Focus on providing value to the potential client.
        """
        
        # Add property information if available
        if property_info:
            property_details = f"""
            You are currently discussing this property:
            - Name: {property_info.get('name', 'N/A')}
            - Type: {property_info.get('type', 'N/A')}
            - Price: ${property_info.get('price', 0):,}
            - Address: {property_info.get('address', 'N/A')}
            - Features: {property_info.get('features', 'N/A')}
            - Description: {property_info.get('description', 'N/A')}
            """
            system_message += property_details
        
        # Add agent context if available
        if agent_context:
            system_message += f"\n\nAdditional context: {agent_context}"
        
        # Prepare the messages for the API call
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history if available
        if conversation_history:
            for message in conversation_history:
                messages.append({
                    "role": message["role"],  # "user" or "assistant"
                    "content": message["content"]
                })
        
        # Add the current client message
        messages.append({"role": "user", "content": client_message})
        
        try:
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # You can change this to other models like "gpt-3.5-turbo" if needed
                messages=messages,
                temperature=0.7,  # Controls randomness: lower is more deterministic
                max_tokens=300,   # Limit response length
                top_p=0.9,        # Controls diversity
                frequency_penalty=0.0,
                presence_penalty=0.6  # Penalizes repetition
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            # Return a fallback response in case of error
            return "I apologize, but I'm having trouble generating a response right now. Let me connect you with a human agent who can assist you further."
    
    def generate_property_description(self, property_info: Dict[str, Any]) -> str:
        """
        Generate an engaging property description based on property information.
        
        Args:
            property_info: Dictionary containing property details
            
        Returns:
            Generated property description
        """
        prompt = f"""
        Create an engaging and persuasive description for this property:
        
        Property Type: {property_info.get('type', 'N/A')}
        Price: ${property_info.get('price', 0):,}
        Location: {property_info.get('address', 'N/A')}
        Features: {property_info.get('features', 'N/A')}
        
        The description should highlight the property's best features and appeal to potential buyers.
        Keep it concise (100-150 words) but compelling.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert real estate copywriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating property description: {e}")
            return "Property description not available at this time."
    
    def analyze_client_sentiment(self, client_message: str) -> Dict[str, Any]:
        """
        Analyze client message to determine sentiment and interest level.
        
        Args:
            client_message: The message from the client
            
        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = f"""
        Analyze this message from a potential real estate client:
        
        "{client_message}"
        
        Provide a JSON response with the following fields:
        - sentiment: (positive, neutral, or negative)
        - interest_level: (high, medium, or low)
        - key_concerns: (list of any concerns mentioned)
        - preferences: (list of any preferences mentioned)
        - next_action: (what the agent should focus on next)
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that analyzes client messages for real estate agents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing client sentiment: {e}")
            return {
                "sentiment": "neutral",
                "interest_level": "medium",
                "key_concerns": [],
                "preferences": [],
                "next_action": "ask_follow_up_questions"
            }

# Example usage
if __name__ == "__main__":
    # Initialize the OpenAI integration
    # In a real implementation, you would set the API key in an environment variable
    openai_integration = OpenAIIntegration(api_key="your_openai_api_key")
    
    # Example property
    property_info = {
        "name": "Lakeside Villa",
        "type": "Residential",
        "price": 1250000,
        "address": "123 Lake Dr, Waterfront, CA",
        "features": "4 bed, 3 bath, 3,200 sq ft",
        "description": "Luxurious lakefront property with panoramic water views"
    }
    
    # Example conversation history
    conversation_history = [
        {"role": "assistant", "content": "Hello John, this is Sarah from Premier Real Estate. I noticed you were interested in properties in the downtown area. Would you like to schedule a viewing of our latest listings?"},
        {"role": "user", "content": "Hi Sarah, yes I am interested, but I'm not sure if I'm ready to view properties just yet."}
    ]
    
    # Generate a response
    response = openai_integration.generate_response(
        client_message="What kind of properties do you have in the downtown area?",
        conversation_history=conversation_history,
        property_info=property_info
    )
    
    print("Generated response:")
    print(response)
    
    # Generate a property description
    description = openai_integration.generate_property_description(property_info)
    
    print("\nGenerated property description:")
    print(description)
    
    # Analyze client sentiment
    sentiment = openai_integration.analyze_client_sentiment(
        "I'm looking for a house with at least 3 bedrooms, but I'm concerned about the high prices in that neighborhood."
    )
    
    print("\nClient sentiment analysis:")
    print(json.dumps(sentiment, indent=2))

