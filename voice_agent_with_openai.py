import os
import json
import time
from datetime import datetime, timedelta
import random
from openai_integration import OpenAIIntegration

class RealEstateVoiceAgent:
    def __init__(self, voice_type="female-professional", speaking_rate=1.0, openai_api_key=None):
        self.voice_type = voice_type
        self.speaking_rate = speaking_rate
        self.properties = self._load_properties()
        self.scripts = self._load_scripts()
        self.crm = CRMIntegration()
        
        # Initialize OpenAI integration
        try:
            self.openai = OpenAIIntegration(api_key=openai_api_key)
            self.use_openai = True
            print("OpenAI integration enabled")
        except Exception as e:
            print(f"Warning: OpenAI integration failed: {e}")
            print("Falling back to template responses")
            self.use_openai = False
        
        # In a real implementation, you would set API keys for voice synthesis:
        # set_api_key("YOUR_ELEVENLABS_API_KEY")
        
        print(f"Real Estate Voice Agent initialized with {voice_type} voice")
        
    def _load_properties(self):
        """Load property data from a database or file"""
        # In a real implementation, this would connect to a database
        properties = [
            {
                "id": "prop001",
                "name": "Lakeside Villa",
                "type": "Residential",
                "price": 1250000,
                "address": "123 Lake Dr, Waterfront, CA",
                "features": "4 bed, 3 bath, 3,200 sq ft",
                "description": "Luxurious lakefront property with panoramic water views"
            },
            {
                "id": "prop002",
                "name": "Downtown Condo",
                "type": "Residential",
                "price": 650000,
                "address": "456 Main St #302, Downtown, CA",
                "features": "2 bed, 2 bath, 1,100 sq ft",
                "description": "Modern condo in the heart of downtown with city views"
            },
            {
                "id": "prop003",
                "name": "Commercial Office",
                "type": "Commercial",
                "price": 2800000,
                "address": "789 Business Ave, Commerce, CA",
                "features": "12,000 sq ft, 3 floors",
                "description": "Prime commercial space in the business district"
            },
            {
                "id": "prop004",
                "name": "Suburban House",
                "type": "Residential",
                "price": 875000,
                "address": "321 Oak St, Suburbia, CA",
                "features": "3 bed, 2.5 bath, 2,400 sq ft",
                "description": "Family home in a quiet suburban neighborhood"
            }
        ]
        
        # If OpenAI is available, generate better descriptions for properties
        if hasattr(self, 'openai') and self.use_openai:
            for property in properties:
                try:
                    property["description"] = self.openai.generate_property_description(property)
                except:
                    # Keep the original description if generation fails
                    pass
                
        print(f"Loaded {len(properties)} properties")
        return properties
    
    def _load_scripts(self):
        """Load call scripts for different scenarios"""
        # In a real implementation, this would load from a database
        scripts = {
            "initial_contact": """
                Hello {client_name}, this is {agent_name} from Premier Real Estate.
                
                I'm reaching out because I noticed you recently expressed interest in {property_type} properties in the {location} area.
                
                We have several new listings that match your criteria. Would you be interested in hearing more about them or perhaps scheduling a viewing?
                
                [If yes] Great! Let me tell you about a few properties that might interest you...
                
                [If no] I understand. Would it be alright if I follow up with you in the future when we have new listings that match your preferences?
            """,
            "property_details": """
                The {property_name} is a beautiful {property_type} located at {address}. 
                
                It features {features} and is priced at ${price:,}.
                
                {description}
                
                Would you be interested in scheduling a viewing of this property?
            """,
            "appointment_scheduling": """
                Great! I'd be happy to schedule a viewing for you. 
                
                We have availability on {date_option_1} at {time_option_1} or {date_option_2} at {time_option_2}.
                
                Which of these would work better for you?
                
                [After selection] Perfect! I've scheduled your viewing for {selected_date} at {selected_time}. 
                
                You'll receive a confirmation email shortly with all the details.
            """
        }
        print(f"Loaded {len(scripts)} script templates")
        return scripts
    
    def make_call(self, client_info, property_id=None):
        """Initiate a call to a potential client"""
        print(f"Initiating call to {client_info['name']} at {client_info['phone']}")
        
        # In a real implementation, this would use Twilio or similar:
        # client = twilio.rest.Client(account_sid, auth_token)
        # call = client.calls.create(
        #     url='https://your-webhook-url.com/voice',
        #     to=client_info['phone'],
        #     from_=your_twilio_number
        # )
        
        # Simulate call connection
        time.sleep(2)
        print("Call connected")
        
        # Log call in CRM
        call_id = self.crm.log_call_start(client_info)
        
        # Initialize conversation history for OpenAI
        conversation_history = []
        
        # Process the call based on the scenario
        if property_id:
            property_info = next((p for p in self.properties if p["id"] == property_id), None)
            if property_info:
                self._handle_property_inquiry(client_info, property_info, call_id, conversation_history)
            else:
                self._handle_general_inquiry(client_info, call_id, conversation_history)
        else:
            self._handle_general_inquiry(client_info, call_id, conversation_history)
            
        # End call
        print("Call completed")
        self.crm.log_call_end(call_id)
        
        return call_id
    
    def _handle_general_inquiry(self, client_info, call_id, conversation_history=None):
        """Handle a general inquiry call"""
        if conversation_history is None:
            conversation_history = []
            
        # Prepare initial script with client info
        if self.use_openai:
            # Generate a personalized greeting using OpenAI
            initial_context = f"You are making an initial call to {client_info['name']} who has expressed interest in {client_info.get('interest', 'residential')} properties in the {client_info.get('location', 'downtown')} area."
            script = self.openai.generate_response(
                client_message="Generate an initial greeting for a cold call to a potential real estate client.",
                agent_context=initial_context
            )
        else:
            # Use template script
            script = self.scripts["initial_contact"].format(
                client_name=client_info["name"],
                agent_name="Sarah",
                property_type=client_info.get("interest", "residential"),
                location=client_info.get("location", "downtown")
            )
        
        # In a real implementation, this would use text-to-speech:
        # audio = generate(
        #     text=script,
        #     voice=self.voice_type,
        #     model="eleven_monolingual_v1"
        # )
        # play(audio)
        
        print("\nAI Agent: " + script.strip())
        
        # Add to conversation history
        conversation_history.append({"role": "assistant", "content": script.strip()})
        
        # Simulate client response (in a real implementation, this would use speech recognition)
        client_responses = [
            "Yes, I'd like to hear more about the properties you have.",
            "I'm not sure if I'm ready to view properties just yet.",
            "What kind of properties do you have in that area?",
            "I'm specifically looking for something with a garage."
        ]
        client_response = random.choice(client_responses)
        print("\nClient: " + client_response)
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": client_response})
        
        # Generate AI response
        if self.use_openai:
            # Use OpenAI to generate a contextual response
            ai_response = self.openai.generate_response(
                client_message=client_response,
                conversation_history=conversation_history
            )
        else:
            # Use predefined responses
            ai_responses = {
                "Yes, I'd like to hear more about the properties you have.": 
                    "Great! We have several properties that might interest you. One of our most popular listings is a modern two-bedroom condo in the heart of downtown. It features an open floor plan, high ceilings, and a private balcony with city views. It's priced at $650,000.",
                
                "I'm not sure if I'm ready to view properties just yet.": 
                    "I completely understand. Would you like me to tell you a bit more about the properties we have available in the downtown area? This might help you decide if you'd like to schedule a viewing.",
                
                "What kind of properties do you have in that area?": 
                    "In the downtown area, we have a mix of modern condos, luxury apartments, and a few townhouses. Our most popular listing is a two-bedroom condo with an open floor plan and city views, priced at $650,000. We also have a three-bedroom townhouse with a rooftop terrace for $875,000.",
                
                "I'm specifically looking for something with a garage.": 
                    "We do have several properties with garage parking. Our downtown condo comes with one dedicated parking space in the secure underground garage. We also have a townhouse in the suburban area with a two-car garage, priced at $875,000. Would either of these interest you?"
            }
            
            ai_response = ai_responses.get(client_response, "I understand. Let me find some properties that would match your needs.")
        
        print("\nAI Agent: " + ai_response)
        
        # Add to conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Log conversation in CRM
        self.crm.update_call_notes(call_id, f"Client: {client_response}\nAgent: {ai_response}")
        
        # If using OpenAI, analyze client sentiment
        if self.use_openai:
            try:
                sentiment = self.openai.analyze_client_sentiment(client_response)
                self.crm.update_client_sentiment(call_id, sentiment)
                
                # Determine call outcome based on sentiment analysis
                if sentiment["interest_level"] == "high":
                    outcome = "appointment_scheduled"
                elif sentiment["interest_level"] == "medium":
                    outcome = "information_provided"
                else:
                    outcome = "follow_up_required"
            except:
                # Fall back to random outcome if sentiment analysis fails
                outcomes = ["appointment_scheduled", "information_provided", "follow_up_required", "not_interested"]
                weights = [0.25, 0.4, 0.2, 0.15]  # Probability weights
                outcome = random.choices(outcomes, weights=weights, k=1)[0]
        else:
            # Random outcome if not using OpenAI
            outcomes = ["appointment_scheduled", "information_provided", "follow_up_required", "not_interested"]
            weights = [0.25, 0.4, 0.2, 0.15]  # Probability weights
            outcome = random.choices(outcomes, weights=weights, k=1)[0]
        
        if outcome == "appointment_scheduled":
            # Schedule appointment
            available_dates = [
                datetime.now().strftime("%A, %B %d"),
                (datetime.now().replace(day=datetime.now().day + 1)).strftime("%A, %B %d"),
                (datetime.now().replace(day=datetime.now().day + 2)).strftime("%A, %B %d")
            ]
            available_times = ["10:00 AM", "1:00 PM", "3:30 PM", "5:00 PM"]
            
            date_option_1 = random.choice(available_dates)
            time_option_1 = random.choice(available_times)
            
            date_option_2 = random.choice([d for d in available_dates if d != date_option_1])
            time_option_2 = random.choice([t for t in available_times if t != time_option_1])
            
            if self.use_openai:
                # Generate appointment scheduling message with OpenAI
                scheduling_context = f"You need to schedule a viewing appointment. Offer these options: {date_option_1} at {time_option_1} or {date_option_2} at {time_option_2}."
                appointment_script = self.openai.generate_response(
                    client_message="I'd like to schedule a viewing.",
                    conversation_history=conversation_history,
                    agent_context=scheduling_context
                )
            else:
                # Use template script
                appointment_script = self.scripts["appointment_scheduling"].format(
                    date_option_1=date_option_1,
                    time_option_1=time_option_1,
                    date_option_2=date_option_2,
                    time_option_2=time_option_2,
                    selected_date=date_option_1,  # Assume first option for simulation
                    selected_time=time_option_1
                )
            
            print("\nAI Agent: " + appointment_script.strip())
            self.crm.schedule_appointment(client_info, date_option_1, time_option_1)
            self.crm.update_call_outcome(call_id, "Appointment scheduled")
        else:
            self.crm.update_call_outcome(call_id, outcome.replace("_", " ").title())
    
    def _handle_property_inquiry(self, client_info, property_info, call_id, conversation_history=None):
        """Handle a specific property inquiry"""
        if conversation_history is None:
            conversation_history = []
            
        # Prepare property details script
        if self.use_openai:
            # Generate property description using OpenAI
            property_context = f"You are discussing the {property_info['name']} property with a potential client. This is a {property_info['type'].lower()} property priced at ${property_info['price']:,}, located at {property_info['address']}. It features {property_info['features']}."
            script = self.openai.generate_response(
                client_message="Tell me about this property.",
                agent_context=property_context,
                property_info=property_info
            )
        else:
            # Use template script
            script = self.scripts["property_details"].format(
                property_name=property_info["name"],
                property_type=property_info["type"].lower(),
                address=property_info["address"],
                features=property_info["features"],
                price=property_info["price"],
                description=property_info["description"]
            )
        
        print("\nAI Agent: " + script.strip())
        
        # Add to conversation history
        conversation_history.append({"role": "assistant", "content": script.strip()})
        
        # Simulate client response
        client_responses = [
            "That sounds interesting. Is parking included?",
            "What are the HOA fees?",
            "Is it close to public transportation?",
            "I'd like to schedule a viewing."
        ]
        client_response = random.choice(client_responses)
        print("\nClient: " + client_response)
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": client_response})
        
        # Generate AI response
        if self.use_openai:
            # Use OpenAI to generate a contextual response
            ai_response = self.openai.generate_response(
                client_message=client_response,
                conversation_history=conversation_history,
                property_info=property_info
            )
        else:
            # Use predefined responses
            ai_responses = {
                "That sounds interesting. Is parking included?": 
                    f"Yes, the {property_info['name']} comes with dedicated parking. For this specific property, you get {'one assigned space in the underground garage' if property_info['type'] == 'Residential' else 'multiple parking spaces in the private lot'}.",
                
                "What are the HOA fees?": 
                    f"The HOA fees for {property_info['name']} are {'$450 per month' if property_info['type'] == 'Residential' else 'not applicable as this is a commercial property with a different fee structure'}. This includes {'building maintenance, security, and access to amenities like the gym and pool' if property_info['type'] == 'Residential' else 'common area maintenance and security'}.",
                
                "Is it close to public transportation?": 
                    f"Yes, {property_info['name']} is very conveniently located. There's a {'subway station just two blocks away' if 'Downtown' in property_info['address'] else 'bus stop within walking distance'}, and several bus lines run nearby.",
                
                "I'd like to schedule a viewing.": 
                    "That's great! I'd be happy to arrange that for you. We have availability tomorrow at 2:00 PM or Friday at 10:00 AM. Which would work better for your schedule?"
            }
            
            ai_response = ai_responses.get(client_response, f"Thank you for your interest in {property_info['name']}. I'll make a note of your question and have our property specialist get back to you with more details.")
        
        print("\nAI Agent: " + ai_response)
        
        # Add to conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Log conversation in CRM
        self.crm.update_call_notes(call_id, f"Client: {client_response}\nAgent: {ai_response}")
        
        # Determine if appointment is scheduled
        if client_response == "I'd like to schedule a viewing.":
            from datetime import timedelta

            today = datetime.now()
            available_dates = [
                today.strftime("%A, %B %d"),
                (today + timedelta(days=1)).strftime("%A, %B %d"),
                (today + timedelta(days=2)).strftime("%A, %B %d")
            ]
            available_times = ["10:00 AM", "2:00 PM"]
            
            selected_date = available_dates[0]
            selected_time = available_times[1]
            
            print(f"\nClient: I'll take the {selected_date} at {selected_time} slot.")
            
            if self.use_openai:
                # Generate confirmation message with OpenAI
                confirmation_context = f"The client has selected to view the property on {selected_date} at {selected_time}. Confirm the appointment and provide next steps."
                confirmation = self.openai.generate_response(
                    client_message=f"I'll take the {selected_date} at {selected_time} slot.",
                    conversation_history=conversation_history,
                    property_info=property_info,
                    agent_context=confirmation_context
                )
                print(f"\nAI Agent: {confirmation}")
            else:
                print(f"\nAI Agent: Perfect! I've scheduled your viewing for {selected_date} at {selected_time}. You'll receive a confirmation email shortly with all the details.")
            
            self.crm.schedule_appointment(client_info, selected_date, selected_time, property_id=property_info["id"])
            self.crm.update_call_outcome(call_id, "Appointment scheduled")
        else:
            self.crm.update_call_outcome(call_id, "Information provided")


class CRMIntegration:
    def __init__(self, crm_type="salesforce"):
        self.crm_type = crm_type
        self.calls = {}
        self.appointments = []
        print(f"CRM Integration initialized for {crm_type}")
    
    def log_call_start(self, client_info):
        """Log the start of a call in the CRM"""
        call_id = f"call_{int(time.time())}_{random.randint(1000, 9999)}"
        self.calls[call_id] = {
            "client": client_info,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "in-progress",
            "notes": [],
            "outcome": None,
            "sentiment": None  # Added for OpenAI sentiment analysis
        }
        print(f"Call logged in CRM with ID: {call_id}")
        return call_id
    
    def update_call_notes(self, call_id, note):
        """Add notes to a call record"""
        if call_id in self.calls:
            self.calls[call_id]["notes"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": note
            })
            print(f"Notes added to call {call_id}")
    
    def update_client_sentiment(self, call_id, sentiment):
        """Update client sentiment analysis data"""
        if call_id in self.calls:
            self.calls[call_id]["sentiment"] = sentiment
            print(f"Sentiment analysis added to call {call_id}")
    
    def update_call_outcome(self, call_id, outcome):
        """Update the outcome of a call"""
        if call_id in self.calls:
            self.calls[call_id]["outcome"] = outcome
            print(f"Call {call_id} outcome updated to: {outcome}")
    
    def log_call_end(self, call_id):
        """Log the end of a call"""
        if call_id in self.calls:
            self.calls[call_id]["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.calls[call_id]["status"] = "completed"
            
            # Calculate duration
            start = datetime.strptime(self.calls[call_id]["start_time"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(self.calls[call_id]["end_time"], "%Y-%m-%d %H:%M:%S")
            duration = (end - start).total_seconds()
            self.calls[call_id]["duration"] = f"{int(duration // 60)}:{int(duration % 60):02d}"
            
            print(f"Call {call_id} completed. Duration: {self.calls[call_id]['duration']}")
    
    def schedule_appointment(self, client_info, date, time, property_id=None):
        """Schedule a property viewing appointment"""
        appointment_id = f"apt_{int(time.time())}_{random.randint(1000, 9999)}"
        appointment = {
            "id": appointment_id,
            "client": client_info,
            "date": date,
            "time": time,
            "property_id": property_id,
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.appointments.append(appointment)
        print(f"Appointment scheduled: {date} at {time} for {client_info['name']}")
        return appointment_id
    
    def get_call_history(self, client_id=None):
        """Get call history, optionally filtered by client"""
        if client_id:
            return [call for call_id, call in self.calls.items() 
                   if call["client"].get("id") == client_id]
        return self.calls
    
    def get_appointments(self, client_id=None):
        """Get appointments, optionally filtered by client"""
        if client_id:
            return [apt for apt in self.appointments 
                   if apt["client"].get("id") == client_id]
        return self.appointments


# Example usage
if __name__ == "__main__":
    # Initialize the voice agent with OpenAI integration
    # In a real implementation, you would set the API key in an environment variable
    agent = RealEstateVoiceAgent(
        voice_type="female-professional",
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Client information
    client = {
        "id": "client123",
        "name": "John Smith",
        "phone": "(555) 123-4567",
        "email": "john.smith@example.com",
        "interest": "residential",
        "location": "downtown",
        "budget": 700000
    }
    
    # Make a general inquiry call
    print("\n=== GENERAL INQUIRY CALL ===")
    call_id1 = agent.make_call(client)
    
    # Make a specific property inquiry call
    print("\n=== SPECIFIC PROPERTY INQUIRY CALL ===")
    call_id2 = agent.make_call(client, property_id="prop002")
    
    # Print call history from CRM
    print("\n=== CALL HISTORY ===")
    for call_id, call_data in agent.crm.calls.items():
        print(f"Call ID: {call_id}")
        print(f"Client: {call_data['client']['name']}")
        print(f"Start Time: {call_data['start_time']}")
        print(f"End Time: {call_data.get('end_time', 'N/A')}")
        print(f"Duration: {call_data.get('duration', 'N/A')}")
        print(f"Outcome: {call_data.get('outcome', 'N/A')}")
        print(f"Notes: {len(call_data['notes'])} entries")
        if call_data.get("sentiment"):
            print(f"Sentiment: {call_data['sentiment']['sentiment']}")
            print(f"Interest Level: {call_data['sentiment']['interest_level']}")
        print()
    
    # Print appointments
    print("\n=== APPOINTMENTS ===")
    for apt in agent.crm.appointments:
        property_name = "General inquiry"
        if apt["property_id"]:
            property_info = next((p for p in agent.properties if p["id"] == apt["property_id"]), None)
            if property_info:
                property_name = property_info["name"]
        
        print(f"Appointment ID: {apt['id']}")
        print(f"Client: {apt['client']['name']}")
        print(f"Date/Time: {apt['date']} at {apt['time']}")
        print(f"Property: {property_name}")
        print(f"Status: {apt['status']}")
        print()

