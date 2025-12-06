"use client";

import { useState } from "react";
import toast from "react-hot-toast";

const TravelPlanner = ({ userId }) => {
  // Form state
  const [destination, setDestination] = useState("");
  const [country, setCountry] = useState("");
  const [days, setDays] = useState(7);
  const [budget, setBudget] = useState("");
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [preferences, setPreferences] = useState({
    adventure: false,
    relaxation: false,
    culture: false,
    food: false,
    nature: false,
    shopping: false,
  });

  // Data state
  const [isLoading, setIsLoading] = useState(false);
  const [tripData, setTripData] = useState(null);
  const [activeTab, setActiveTab] = useState("itinerary");
  const [error, setError] = useState(null);

  const handlePreferenceToggle = (pref) => {
    setPreferences((prev) => ({
      ...prev,
      [pref]: !prev[pref],
    }));
  };

  const handlePlanTrip = async (e) => {
    e.preventDefault();

    if (!destination.trim()) {
      toast.error("Please enter a destination");
      return;
    }

    if (days < 1 || days > 30) {
      toast.error("Trip duration must be between 1 and 30 days");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/travel/planner", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination,
          country,
          days,
          budget,
          checkIn,
          checkOut,
          preferences: Object.keys(preferences).filter((k) => preferences[k]),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to generate trip plan");
      }

      const data = await response.json();
      setTripData(data);
      toast.success("Trip plan generated!");
    } catch (err) {
      console.error("Error generating trip:", err);
      setError(err.message);
      toast.error(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderItinerary = () => {
    if (!tripData?.itinerary) return null;

    return (
      <div className="space-y-6">
        <div className="bg-base-200 p-6 rounded-lg">
          <h3 className="text-2xl font-bold mb-2">
            {tripData.itinerary.title}
          </h3>
          <p className="text-base-content/70">
            {tripData.itinerary.description}
          </p>
        </div>

        {tripData.itinerary.daily_plans?.map((day, idx) => (
          <div key={idx} className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title text-xl">
                Day {day.day}: {day.title}
              </h3>
              <p className="text-base-content/70 mb-4">{day.theme}</p>

              <div className="space-y-4">
                {day.activities?.map((activity, actIdx) => (
                  <div key={actIdx} className="border-l-4 border-primary pl-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-semibold text-primary">
                          {activity.time}
                        </p>
                        <h4 className="text-lg font-bold mt-1">
                          {activity.name}
                        </h4>
                        <p className="text-sm text-base-content/70 mt-2">
                          {activity.description}
                        </p>

                        {activity.location && (
                          <div className="mt-3 p-3 bg-base-200 rounded-lg">
                            <div className="flex items-start gap-2">
                              <span className="text-base">📍</span>
                              <div className="flex-1">
                                {activity.location.cuisine && (
                                  <p className="font-bold text-base mb-1">
                                    {activity.name}
                                  </p>
                                )}
                                <p className="font-semibold text-sm">
                                  {activity.location.address}
                                </p>
                                {/* Address shown above. Removed type to avoid redundant label. */}
                                {activity.location.cuisine && (
                                  <p className="text-xs text-base-content/60">
                                    Cuisine: {activity.location.cuisine} •{" "}
                                    {activity.location.priceRange}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        <div className="flex gap-3 mt-2">
                          {activity.estimated_duration && (
                            <p className="text-sm text-base-content/70">
                              ⏱️ {activity.estimated_duration}
                            </p>
                          )}
                          {activity.estimated_cost && (
                            <p className="text-sm text-base-content/70">
                              💰 {activity.estimated_cost}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {day.meals && (
                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-semibold mb-3">🍽️ Dining Summary:</h4>
                  <div className="space-y-2">
                    {day.meals.breakfast && (
                      <div className="flex items-start gap-2 text-sm">
                        <span className="font-semibold min-w-[80px]">
                          Breakfast:
                        </span>
                        <div>
                          <p>
                            {typeof day.meals.breakfast === "string"
                              ? day.meals.breakfast
                              : day.meals.breakfast.name}
                          </p>
                          {day.meals.breakfast.address && (
                            <p className="text-xs text-base-content/60">
                              {day.meals.breakfast.address}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                    {day.meals.lunch && (
                      <div className="flex items-start gap-2 text-sm">
                        <span className="font-semibold min-w-[80px]">
                          Lunch:
                        </span>
                        <div>
                          <p>
                            {typeof day.meals.lunch === "string"
                              ? day.meals.lunch
                              : day.meals.lunch.name}
                          </p>
                          {day.meals.lunch.address && (
                            <p className="text-xs text-base-content/60">
                              📍 {day.meals.lunch.address}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                    {day.meals.dinner && (
                      <div className="flex items-start gap-2 text-sm">
                        <span className="font-semibold min-w-[80px]">
                          Dinner:
                        </span>
                        <div>
                          <p>
                            {typeof day.meals.dinner === "string"
                              ? day.meals.dinner
                              : day.meals.dinner.name}
                          </p>
                          {day.meals.dinner.address && (
                            <p className="text-xs text-base-content/60">
                              📍 {day.meals.dinner.address}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderHotels = () => {
    if (!tripData?.hotels?.length) {
      return (
        <div className="text-center py-12">
          <p className="text-base-content/70">
            No hotel recommendations available
          </p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tripData.hotels.map((hotel, idx) => (
          <div key={idx} className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h3 className="card-title">{hotel.name}</h3>

              {hotel.location && (
                <p className="text-sm text-base-content/70">
                  📍 {hotel.location.latitude?.toFixed(4)},{" "}
                  {hotel.location.longitude?.toFixed(4)}
                </p>
              )}

              {hotel.address && (
                <div className="text-sm mt-2">
                  <p>{hotel.address.lines?.join(", ")}</p>
                  <p>
                    {hotel.address.cityName}, {hotel.address.countryCode}
                  </p>
                </div>
              )}

              {hotel.price && (
                <div className="mt-4">
                  <div className="stat-value text-2xl text-primary">
                    {hotel.price.currency} {hotel.price.total}
                  </div>
                  <div className="text-sm text-base-content/70">per night</div>
                </div>
              )}

              {hotel.rating && (
                <div className="flex items-center gap-2 mt-2">
                  <div className="rating rating-sm">
                    {[...Array(5)].map((_, i) => (
                      <input
                        key={i}
                        type="radio"
                        className="mask mask-star-2 bg-orange-400"
                        checked={i < Math.round(hotel.rating)}
                        readOnly
                      />
                    ))}
                  </div>
                  <span className="text-sm">({hotel.rating}/5)</span>
                </div>
              )}

              <div className="card-actions justify-end mt-4">
                <button className="btn btn-primary btn-sm">View Details</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderFlights = () => {
    if (!tripData?.flights?.length) {
      return (
        <div className="text-center py-12">
          <p className="text-base-content/70">No flight options available</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {tripData.flights.map((flight, idx) => (
          <div key={idx} className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {flight.itineraries?.map((itinerary, itinIdx) => (
                    <div key={itinIdx} className="mb-6 last:mb-0">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="badge badge-primary">
                          {itinIdx === 0 ? "Outbound" : "Return"}
                        </div>
                        <span className="text-sm text-base-content/70">
                          Duration: {itinerary.duration}
                        </span>
                      </div>

                      {itinerary.segments?.map((segment, segIdx) => (
                        <div
                          key={segIdx}
                          className="flex items-center gap-4 py-4 border-b last:border-b-0"
                        >
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <p className="text-2xl font-bold">
                                  {segment.departure?.airport}
                                </p>
                                <p className="text-sm text-base-content/70">
                                  {new Date(
                                    segment.departure?.time
                                  ).toLocaleString()}
                                </p>
                              </div>

                              <div className="text-center px-4">
                                <div className="flex items-center gap-2">
                                  <div className="w-16 h-px bg-base-content/30"></div>
                                  <span className="text-sm">✈️</span>
                                  <div className="w-16 h-px bg-base-content/30"></div>
                                </div>
                                <p className="text-xs mt-1 text-base-content/70">
                                  {segment.carrier} {segment.flight_number}
                                </p>
                              </div>

                              <div className="text-right">
                                <p className="text-2xl font-bold">
                                  {segment.arrival?.airport}
                                </p>
                                <p className="text-sm text-base-content/70">
                                  {new Date(
                                    segment.arrival?.time
                                  ).toLocaleString()}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>

                {flight.price && (
                  <div className="ml-6 text-right">
                    <div className="stat-value text-3xl text-primary">
                      {flight.price.currency} {flight.price.total}
                    </div>
                    <div className="text-sm text-base-content/70">total</div>
                  </div>
                )}
              </div>

              <div className="card-actions justify-end mt-4">
                <button className="btn btn-primary">Book Flight</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-base-200">
      {/* Header */}
      <div className="bg-base-100 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-4xl font-bold">Travel Planner</h1>
          <p className="text-base-content/70 mt-2">
            Plan your perfect trip with AI-powered recommendations
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Planning Form */}
        {!tripData && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">Create Your Trip</h2>

              <form onSubmit={handlePlanTrip} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">
                        Destination City
                      </span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Tokyo"
                      className="input input-bordered"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Country</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Japan"
                      className="input input-bordered"
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">
                        Number of Days
                      </span>
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      className="input input-bordered"
                      value={days}
                      onChange={(e) => setDays(parseInt(e.target.value))}
                      required
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">
                        Budget (optional)
                      </span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., $3000"
                      className="input input-bordered"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">
                        Check-in Date
                      </span>
                    </label>
                    <input
                      type="date"
                      className="input input-bordered"
                      value={checkIn}
                      onChange={(e) => setCheckIn(e.target.value)}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">
                        Check-out Date
                      </span>
                    </label>
                    <input
                      type="date"
                      className="input input-bordered"
                      value={checkOut}
                      onChange={(e) => setCheckOut(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">
                      Travel Preferences
                    </span>
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(preferences).map((pref) => (
                      <button
                        key={pref}
                        type="button"
                        onClick={() => handlePreferenceToggle(pref)}
                        className={`btn btn-sm ${
                          preferences[pref] ? "btn-primary" : "btn-outline"
                        }`}
                      >
                        {pref.charAt(0).toUpperCase() + pref.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {error && (
                  <div className="alert alert-error">
                    <span>{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  className="btn btn-primary btn-lg w-full"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="loading loading-spinner"></span>
                      Generating Your Perfect Trip...
                    </>
                  ) : (
                    "Generate Trip Plan"
                  )}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Trip Results */}
        {tripData && (
          <div className="space-y-6">
            {/* Action Bar */}
            <div className="flex items-center justify-between bg-base-100 p-4 rounded-lg shadow">
              <div>
                <h2 className="text-2xl font-bold">
                  {destination}, {country}
                </h2>
                <p className="text-sm text-base-content/70">
                  {days} days • {checkIn} to {checkOut}
                </p>
              </div>
              <button
                onClick={() => {
                  setTripData(null);
                  setActiveTab("itinerary");
                }}
                className="btn btn-outline"
              >
                Plan New Trip
              </button>
            </div>

            {/* Tabs */}
            <div className="tabs tabs-boxed bg-base-100 p-2 shadow">
              <button
                className={`tab tab-lg ${
                  activeTab === "itinerary" ? "tab-active" : ""
                }`}
                onClick={() => setActiveTab("itinerary")}
              >
                📅 Daily Itinerary
              </button>
              <button
                className={`tab tab-lg ${
                  activeTab === "hotels" ? "tab-active" : ""
                }`}
                onClick={() => setActiveTab("hotels")}
              >
                🏨 Hotels ({tripData.hotels?.length || 0})
              </button>
              <button
                className={`tab tab-lg ${
                  activeTab === "flights" ? "tab-active" : ""
                }`}
                onClick={() => setActiveTab("flights")}
              >
                ✈️ Flights ({tripData.flights?.length || 0})
              </button>
            </div>

            {/* Tab Content */}
            <div className="bg-base-100 rounded-lg shadow-xl p-6">
              {activeTab === "itinerary" && renderItinerary()}
              {activeTab === "hotels" && renderHotels()}
              {activeTab === "flights" && renderFlights()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TravelPlanner;
