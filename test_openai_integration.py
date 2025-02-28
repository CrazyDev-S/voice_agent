import os
from openai_integration import OpenAIIntegration

def test_openai_integration():
    openai_integration = OpenAIIntegration(api_key="")

    # Test generate_response
    response = openai_integration.generate_response(
        client_message="Tell me about properties in downtown.",
        agent_context="You are a real estate agent specializing in downtown properties."
    )
    print("Generated response:", response)

    # Test generate_property_description
    property_info = {
        "name": "Skyline Apartments",
        "type": "Residential",
        "price": 500000,
        "address": "123 Main St, Downtown",
        "features": "2 bed, 2 bath, 1000 sq ft",
    }
    description = openai_integration.generate_property_description(property_info)
    print("\nGenerated property description:", description)

    # Test analyze_client_sentiment
    sentiment = openai_integration.analyze_client_sentiment(
        "I'm interested in the property, but I'm concerned about the price."
    )
    print("\nClient sentiment analysis:", sentiment)

if __name__ == "__main__":
    test_openai_integration()

