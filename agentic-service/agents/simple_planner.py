"""
Simplified travel planner without LangGraph dependencies.
Uses direct OpenAI calls for itinerary generation + Amadeus for real travel data.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import json

import openai

from config import settings
from services.amadeus_service import amadeus_service

logger = logging.getLogger(__name__)


class SimplePlanner:
    """
    Simplified travel planner using direct LLM calls.
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key
        )
    
    async def generate_itinerary(
        self,
        city: str,
        country: str,
        days: int,
        budget: Optional[float] = None,
        preferences: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a travel itinerary using a single LLM call.
        """
        run_id = str(uuid.uuid4())
        logger.info(f"[{run_id}] Generating itinerary for {days}-day trip to {city}, {country}")
        
        # Get real travel data from Amadeus if available
        flight_data = None
        hotel_data = None
        
        if amadeus_service.is_available():
            try:
                # Get airport codes
                origin_code = "LAX"  # Default, could be user's location
                dest_code = amadeus_service.get_airport_code(city)
                
                if dest_code:
                    # Search for flights
                    departure_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                    return_date = (datetime.now() + timedelta(days=30+days)).strftime('%Y-%m-%d')
                    
                    logger.info(f"[{run_id}] Fetching real flight data...")
                    flight_data = amadeus_service.search_flights(
                        origin=origin_code,
                        destination=dest_code,
                        departure_date=departure_date,
                        return_date=return_date,
                        adults=1,
                        max_results=3
                    )
                
                # Search for hotels
                # Get city code (first 3 letters uppercase)
                city_code = city[:3].upper()
                logger.info(f"[{run_id}] Fetching real hotel data...")
                hotel_data = amadeus_service.search_hotels(
                    city_code=city_code,
                    max_results=5
                )
            except Exception as e:
                logger.warning(f"[{run_id}] Could not fetch Amadeus data: {e}")
        
        try:
            # Build preferences string
            pref_list = [k for k, v in (preferences or {}).items() if v]
            pref_str = ", ".join(pref_list) if pref_list else "balanced mix of activities"
            
            # Build budget string
            budget_str = f"${budget:.2f}" if budget else "flexible budget"
            
            # Build real travel data context
            travel_data_context = ""
            if flight_data and flight_data.get("flights"):
                cheapest_flight = min(flight_data["flights"], key=lambda x: float(x["price"]["total"]))
                travel_data_context += f"\n\nReal Flight Data Available:"
                travel_data_context += f"\n- Cheapest flight: {cheapest_flight['price']['currency']} {cheapest_flight['price']['total']}"
                travel_data_context += f"\n- {len(flight_data['flights'])} flight options found"
            
            if hotel_data and hotel_data.get("hotels"):
                travel_data_context += f"\n\nReal Hotel Data Available:"
                travel_data_context += f"\n- {len(hotel_data['hotels'])} hotels found"
                for hotel in hotel_data["hotels"][:3]:
                    travel_data_context += f"\n  • {hotel['name']}"
            
            # Create the prompt
            system_prompt = """You are an expert travel planner AI. Generate detailed, realistic travel itineraries.

CRITICAL REQUIREMENTS FOR LOCATIONS:
- Every location MUST be a specific place name (museum, restaurant, store, park, building)
- NEVER use just neighborhood/district names (e.g., NOT "Shibuya", but "Shibuya Crossing" or "Tokyu Hands Shibuya")
- NEVER repeat the same location twice in the entire itinerary
- Format locations as: "Place Name, City" (e.g., "Senso-ji Temple, Tokyo" or "AIN SOPH Journey, Shinjuku")
- Keep locations concise: just the place/store/museum name and the city/district
- Do NOT include full street addresses, postal codes, or country names
- Each activity should have a unique, identifiable location

Your itineraries should include:
- Day-by-day breakdown of activities with SPECIFIC locations
- Named attractions, restaurants with actual names, specific stores/museums
- Practical logistics and timing
- Local insights and tips
- Safety and compliance information

Return your response as a structured JSON object with this format:
{
  "title": "Trip title",
  "description": "Brief overview",
  "daily_schedule": [
    {
      "day": 1,
      "theme": "Day theme",
      "activities": [
        {"time": "9:00 AM", "activity": "Activity name", "location": "Place Name, City/District", "notes": "Details"}
      ]
    }
  ],
  "daily_plans": [
    {
      "day": 1,
      "date": "Day 1",
      "theme": "Day theme",
      "plan": [
        {"time": "7:00 AM", "activity": "Wake up and breakfast", "location": "Hotel/Cafe Name, City", "duration": "1 hour", "notes": "Start your day"},
        {"time": "8:00 AM", "activity": "Morning activity", "location": "Place Name, City", "duration": "2 hours", "notes": "Details"},
        {"time": "12:00 PM", "activity": "Lunch", "location": "Restaurant Name, City", "duration": "1.5 hours", "notes": "Try local cuisine"},
        {"time": "2:00 PM", "activity": "Afternoon activity", "location": "Place Name, City", "duration": "2 hours", "notes": "Details"},
        {"time": "6:00 PM", "activity": "Dinner", "location": "Restaurant Name, City", "duration": "2 hours", "notes": "Evening meal"}
      ],
      "total_activities": 5,
      "estimated_walking": "5 km",
      "tips": "Wear comfortable shoes"
    }
  ],
  "highlights": ["Specific attraction 1", "Specific attraction 2"],
  "local_tips": ["Tip 1", "Tip 2"],
  "compliance": {
    "visa_required": false,
    "safety_level": "safe",
    "vaccinations": []
  },
  "estimated_costs": {
    "accommodation": 0,
    "food": 0,
    "activities": 0,
    "transport": 0,
    "total": 0
  }
}"""
            
            user_prompt = f"""Plan a {days}-day trip to {city}, {country}.

Travel Preferences: {pref_str}
Budget: {budget_str}{travel_data_context}

Please create a comprehensive itinerary that:
1. Makes the most of {days} days in {city}
2. Includes activities matching the preferences: {pref_str}
3. Stays within or around the budget: {budget_str}
4. Includes practical details like timing and logistics
5. Provides local insights and safety information
6. Uses ONLY specific location names formatted as "Place Name, City" (e.g., "Senso-ji Temple, Tokyo" not "Asakusa")
7. NEVER repeats the same location twice in the itinerary
8. Keep locations concise - NO full street addresses, postal codes, or detailed address info
9. Each location must be a specific, named place (museum, restaurant, store, landmark)

IMPORTANT: Create a detailed "daily_plans" section for EACH day with:
- Hour-by-hour schedule from 7:00 AM to 8:00 PM
- Include breakfast (7-8 AM), lunch (12-1:30 PM), dinner (6-8 PM)
- Morning activities (8 AM - 12 PM), afternoon activities (2 PM - 6 PM)
- Each activity should have: time, activity name, specific location, duration, and helpful notes
- Include estimated walking distances and practical tips for each day
- Make sure every time slot is filled with something meaningful

Return the itinerary as JSON following the specified format."""
            
            # Call the OpenAI API directly
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            try:
                itinerary_data = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                itinerary_data = {
                    "title": f"{days}-Day {city} Adventure",
                    "description": content[:500],
                    "daily_schedule": [],
                    "highlights": [],
                    "local_tips": [],
                    "compliance": {
                        "visa_required": False,
                        "safety_level": "check official sources",
                        "vaccinations": []
                    },
                    "estimated_costs": {
                        "total": budget if budget else 0
                    }
                }
            
            # Convert to expected format - collect unique stops only
            stops = []
            seen_locations = set()
            for day in itinerary_data.get("daily_schedule", []):
                for activity in day.get("activities", []):
                    location = activity.get("location", activity.get("activity", "Activity"))
                    # Only add if we haven't seen this location before
                    if location and location.lower() not in seen_locations:
                        stops.append(location)
                        seen_locations.add(location.lower())
            
            # Add highlights as stops if we don't have many (also checking for duplicates)
            if len(stops) < 5:
                for highlight in itinerary_data.get("highlights", [])[:5]:
                    if highlight and highlight.lower() not in seen_locations:
                        stops.append(highlight)
                        seen_locations.add(highlight.lower())
            
            tour = {
                "city": city,
                "country": country,
                "title": itinerary_data.get("title", f"{days}-Day {city} Adventure"),
                "description": itinerary_data.get("description", f"An amazing {days}-day journey through {city}"),
                "image": "https://source.unsplash.com/800x600/?travel," + city.lower().replace(" ", "-"),
                "stops": stops[:10],  # Limit to 10 stops for display
                "daily_schedule": itinerary_data.get("daily_schedule", []),
                "daily_plans": itinerary_data.get("daily_plans", []),  # NEW: Detailed hour-by-hour plans
                "compliance": itinerary_data.get("compliance", {}),
                "research": {
                    "highlights": itinerary_data.get("highlights", []),
                    "local_tips": itinerary_data.get("local_tips", []),
                    "estimated_costs": itinerary_data.get("estimated_costs", {})
                },
                "real_data": {
                    "flights": flight_data.get("flights", []) if flight_data else [],
                    "hotels": hotel_data.get("hotels", []) if hotel_data else [],
                    "has_real_data": bool(flight_data or hotel_data)
                }
            }
            
            result = {
                "run_id": run_id,
                "tour": tour,
                "cost": {
                    "llm_tokens": 2000,  # Approximate
                    "api_calls": 1,
                    "total_usd": 0.02
                },
                "citations": ["Generated by AI based on travel knowledge"],
                "status": "completed"
            }
            
            logger.info(f"[{run_id}] Itinerary generated successfully")
            return result
        
        except Exception as exc:
            logger.error(f"[{run_id}] Generation failed: {str(exc)}", exc_info=True)
            return {
                "run_id": run_id,
                "tour": {},
                "cost": {},
                "citations": [],
                "status": "failed",
                "error": str(exc)
            }

