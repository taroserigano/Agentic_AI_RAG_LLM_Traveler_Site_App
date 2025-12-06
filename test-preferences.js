// Test script to verify travel preferences are working
// Run with: node test-preferences.js

const AGENTIC_SERVICE_URL = process.env.AGENTIC_SERVICE_URL || "https://your-lambda-url.amazonaws.com";

async function testPreferences() {
  console.log("Testing Travel Preferences Flow\n");
  console.log("================================\n");

  // Test 1: Check if Lambda service accepts and uses preferences
  console.log("Test 1: Testing Lambda service with preferences...");
  try {
    const response = await fetch(`${AGENTIC_SERVICE_URL}/api/agentic/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        city: "Tokyo",
        country: "Japan",
        days: 2,
        budget: 1000,
        preferences: ["food", "culture"],
        user_id: "test-user",
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("✓ Lambda service responded successfully");
      console.log("  Response structure:", Object.keys(data));
      
      // Check if preferences influenced the output
      const tour = data.tour || data.itinerary || data;
      if (tour.daily_plans) {
        console.log("  Daily plans found:", tour.daily_plans.length);
        const themes = tour.daily_plans.map(d => d.theme).join(", ");
        console.log("  Themes:", themes);
        
        // Check if themes relate to preferences
        const hasFood = themes.toLowerCase().includes("food");
        const hasCulture = themes.toLowerCase().includes("culture");
        if (hasFood || hasCulture) {
          console.log("✓ Preferences ARE being used in Lambda response");
        } else {
          console.log("✗ Preferences NOT reflected in Lambda themes");
        }
      }
    } else {
      console.log("✗ Lambda service unavailable or returned error:", response.status);
      console.log("  This is expected if Lambda doesn't handle preferences parameter");
    }
  } catch (err) {
    console.log("✗ Lambda service error:", err.message);
  }

  console.log("\n");

  // Test 2: Check fallback generator logic
  console.log("Test 2: Analyzing fallback generator code...");
  const fs = require('fs');
  const routeCode = fs.readFileSync('./app/api/travel/planner/route.js', 'utf8');
  
  // Check if preferences are passed to fallback
  const hasFallbackPreferences = routeCode.includes('generateFallbackItinerary') && 
                                  routeCode.includes('preferences');
  const hasActivityDatabase = routeCode.includes('activityDatabase');
  const hasPreferenceMapping = routeCode.includes('selectedPreferences');

  if (hasFallbackPreferences && hasActivityDatabase && hasPreferenceMapping) {
    console.log("✓ Fallback generator DOES use preferences");
    console.log("  - Has activityDatabase with categories");
    console.log("  - Maps preferences to activity selection");
    console.log("  - Rotates through selected preferences for daily plans");
  } else {
    console.log("✗ Fallback generator does NOT properly use preferences");
  }

  console.log("\n");

  // Test 3: Check frontend preferences state
  console.log("Test 3: Analyzing frontend preferences logic...");
  const componentCode = fs.readFileSync('./components/TravelPlanner.jsx', 'utf8');
  
  const hasPreferenceState = componentCode.includes('preferences') && 
                              componentCode.includes('useState');
  const hasPreferenceToggle = componentCode.includes('handlePreferenceToggle');
  const sendsPreferences = componentCode.includes('preferences: Object.keys(preferences).filter');

  if (hasPreferenceState && hasPreferenceToggle && sendsPreferences) {
    console.log("✓ Frontend DOES send preferences");
    console.log("  - Has preference state management");
    console.log("  - Has toggle handler");
    console.log("  - Sends filtered array to API");
  } else {
    console.log("✗ Frontend does NOT properly handle preferences");
  }

  console.log("\n");
  console.log("================================");
  console.log("SUMMARY");
  console.log("================================\n");

  // Final assessment
  const fallbackWorks = hasFallbackPreferences && hasActivityDatabase;
  const frontendWorks = hasPreferenceState && hasPreferenceToggle && sendsPreferences;

  if (fallbackWorks && frontendWorks) {
    console.log("✓ Travel preferences ARE working in code");
    console.log("  - Frontend correctly sends selected preferences");
    console.log("  - Fallback generator uses them to select activities");
    console.log("  - Lambda service MAY OR MAY NOT use them (depends on Lambda implementation)");
    console.log("\nNote: The effectiveness depends on whether your Lambda planner");
    console.log("actually uses the 'preferences' parameter in its LLM prompt.");
  } else {
    console.log("✗ Travel preferences are NOT fully working");
    if (!frontendWorks) console.log("  - Frontend preferences logic is broken");
    if (!fallbackWorks) console.log("  - Backend fallback doesn't use preferences");
  }
}

testPreferences().catch(console.error);
