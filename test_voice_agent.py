import os
from voice_agent_with_openai import RealEstateVoiceAgent

def test_voice_agent():
    # Initialize the agent
    agent = RealEstateVoiceAgent(
        voice_type="female-professional",
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

    # Test client information
    client = {
        "id": "test_client_001",
        "name": "Jane Doe",
        "phone": "(555) 987-6543",
        "email": "jane.doe@example.com",
        "interest": "residential",
        "location": "suburbs",
        "budget": 600000
    }

    # Test general inquiry call
    print("\n=== Testing General Inquiry Call ===")
    call_id1 = agent.make_call(client)

    # Test specific property inquiry call
    print("\n=== Testing Specific Property Inquiry Call ===")
    call_id2 = agent.make_call(client, property_id="prop001")

    # Print call history
    print("\n=== Call History ===")
    for call_id, call_data in agent.crm.calls.items():
        print(f"Call ID: {call_id}")
        print(f"Client: {call_data['client']['name']}")
        print(f"Outcome: {call_data.get('outcome', 'N/A')}")
        print(f"Notes: {len(call_data['notes'])} entries")
        if call_data.get("sentiment"):
            print(f"Sentiment: {call_data['sentiment']['sentiment']}")
            print(f"Interest Level: {call_data['sentiment']['interest_level']}")
        print()

    # Print appointments
    print("\n=== Appointments ===")
    for apt in agent.crm.appointments:
        print(f"Appointment ID: {apt['id']}")
        print(f"Client: {apt['client']['name']}")
        print(f"Date/Time: {apt['date']} at {apt['time']}")
        print(f"Property: {apt.get('property_id', 'General inquiry')}")
        print(f"Status: {apt['status']}")
        print()

if __name__ == "__main__":
    test_voice_agent()

