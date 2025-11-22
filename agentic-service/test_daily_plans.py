#!/usr/bin/env python3
"""
Test script to verify daily plans generation.
"""
import asyncio
import json
import logging
from agents.simple_planner import SimplePlanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_daily_plans():
    """Test daily plans generation."""
    try:
        planner = SimplePlanner()
        logger.info("Testing daily plans generation for Barcelona...")
        
        result = await planner.generate_itinerary(
            city="Barcelona",
            country="Spain", 
            days=3,
            budget=1500.0,
            preferences={"culture": True, "food": True, "beach": True},
            user_id="test_user"
        )
        
        logger.info("Generation completed")
        
        # Check if daily_plans exists
        daily_plans = result.get("tour", {}).get("daily_plans", [])
        
        print(f"\n{'='*80}")
        print(f"DAILY PLANS GENERATED: {len(daily_plans)} days")
        print(f"{'='*80}\n")
        
        if not daily_plans:
            print("⚠️  WARNING: No daily_plans found in response!")
            print("\nAvailable keys in tour:")
            print(list(result.get("tour", {}).keys()))
        else:
            for day_plan in daily_plans:
                print(f"\n📅 DAY {day_plan.get('day')}: {day_plan.get('theme', 'N/A')}")
                print(f"{'─'*80}")
                
                plan = day_plan.get('plan', [])
                print(f"Total activities: {len(plan)}")
                
                if plan:
                    print("\nSchedule:")
                    for activity in plan:
                        time = activity.get('time', 'N/A')
                        act = activity.get('activity', 'N/A')
                        loc = activity.get('location', 'N/A')
                        dur = activity.get('duration', 'N/A')
                        print(f"  {time:10} | {act:30} | {loc:40} | {dur}")
                
                if day_plan.get('estimated_walking'):
                    print(f"\n🚶 Walking: {day_plan['estimated_walking']}")
                if day_plan.get('tips'):
                    print(f"💡 Tip: {day_plan['tips']}")
        
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_daily_plans())

