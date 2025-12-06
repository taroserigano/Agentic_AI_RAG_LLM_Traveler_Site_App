"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

const SavedTripsPage = () => {
  const router = useRouter();
  const [trips, setTrips] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTrip, setSelectedTrip] = useState(null);

  useEffect(() => {
    fetchSavedTrips();
  }, []);

  const fetchSavedTrips = async () => {
    try {
      const response = await fetch("/api/travel/planner/saved");
      if (!response.ok) {
        throw new Error("Failed to fetch saved trips");
      }
      const data = await response.json();
      setTrips(data.tripPlans || []);
    } catch (error) {
      console.error("Error fetching trips:", error);
      toast.error("Failed to load saved trips");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTrip = async (tripId, e) => {
    e.stopPropagation(); // Prevent card click event

    if (!confirm("Are you sure you want to delete this trip?")) {
      return;
    }

    try {
      console.log("Attempting to delete trip with ID:", tripId);
      const response = await fetch(`/api/travel/planner/saved/${tripId}`, {
        method: "DELETE",
      });

      console.log("Delete response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Delete error:", errorData);
        throw new Error(errorData.error || "Failed to delete trip");
      }

      toast.success("Trip deleted successfully!");
      // Remove from local state
      setTrips(trips.filter((trip) => trip.id !== tripId));
    } catch (error) {
      console.error("Error deleting trip:", error);
      toast.error(error.message || "Failed to delete trip");
    }
  };

  const handleViewTrip = (trip) => {
    setSelectedTrip(trip);
  };

  const handleBackToList = () => {
    setSelectedTrip(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Not set";
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (selectedTrip) {
    return (
      <div className="min-h-screen bg-base-200">
        {/* Header */}
        <div className="bg-base-100 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <button onClick={handleBackToList} className="btn btn-ghost mb-4">
              ← Back to Saved Trips
            </button>
            <h1 className="text-4xl font-bold">{selectedTrip.title}</h1>
            <p className="text-base-content/70 mt-2">
              <span className="capitalize">{selectedTrip.destination}</span> •{" "}
              {selectedTrip.days} {selectedTrip.days === 1 ? "day" : "days"}
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Hero Image */}
          {selectedTrip.itinerary?.hero_image && (
            <div className="relative w-full h-80 rounded-lg overflow-hidden shadow-xl mb-6">
              <img
                src={selectedTrip.itinerary.hero_image.regular}
                alt={
                  selectedTrip.itinerary.hero_image.alt_description ||
                  `${selectedTrip.destination} travel`
                }
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                <p className="text-white text-sm">
                  Photo by{" "}
                  <a
                    href={`${selectedTrip.itinerary.hero_image.photographer_url}?utm_source=travel_planner&utm_medium=referral`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-primary-content"
                  >
                    {selectedTrip.itinerary.hero_image.photographer}
                  </a>
                  {" on "}
                  <a
                    href="https://unsplash.com?utm_source=travel_planner&utm_medium=referral"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-primary-content"
                  >
                    Unsplash
                  </a>
                </p>
              </div>
            </div>
          )}

          {/* Itinerary */}
          <div className="bg-base-100 rounded-lg shadow-xl p-6 mb-6">
            <div className="bg-base-200 p-6 rounded-lg mb-6">
              <h3 className="text-2xl font-bold mb-2">
                {selectedTrip.itinerary.title}
              </h3>
              <p className="text-base-content/70">
                {selectedTrip.itinerary.description}
              </p>
            </div>

            <div className="space-y-6">
              {selectedTrip.itinerary.daily_plans?.map((day, idx) => (
                <div
                  key={idx}
                  className="card bg-base-100 shadow-xl border border-base-300"
                >
                  <div className="card-body">
                    <h3 className="card-title text-xl">
                      Day {day.day}: {day.title}
                    </h3>
                    <p className="text-base-content/70 mb-4">{day.theme}</p>

                    <div className="space-y-4">
                      {day.activities?.map((activity, actIdx) => (
                        <div
                          key={actIdx}
                          className="border-l-4 border-primary pl-4"
                        >
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
                                  <p className="font-semibold text-sm">
                                    {activity.location.address}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hotels */}
          {selectedTrip.hotels && selectedTrip.hotels.length > 0 && (
            <div className="bg-base-100 rounded-lg shadow-xl p-6">
              <h3 className="text-2xl font-bold mb-6">🏨 Recommended Hotels</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {selectedTrip.hotels.slice(0, 5).map((hotel, idx) => (
                  <div
                    key={idx}
                    className="card bg-base-100 shadow-xl border border-base-300"
                  >
                    <div className="card-body">
                      <h4 className="card-title text-lg">{hotel.name}</h4>
                      {hotel.address && (
                        <p className="text-sm text-base-content/70">
                          📍 {hotel.address.lines?.join(", ")}
                        </p>
                      )}
                      {hotel.price && (
                        <div className="mt-2 p-3 bg-primary/10 rounded-lg">
                          <div className="text-xl font-bold text-primary">
                            {hotel.price.currency} {hotel.price.total}
                          </div>
                          <div className="text-sm">per night</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200">
      {/* Header */}
      <div className="bg-base-100 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-4xl font-bold">Saved Trip Plans</h1>
          <p className="text-base-content/70 mt-2">
            View and manage your saved travel itineraries
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {trips.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">✈️</div>
            <h2 className="text-2xl font-bold mb-2">No saved trips yet</h2>
            <p className="text-base-content/70 mb-6">
              Create your first trip plan to get started!
            </p>
            <button
              onClick={() => router.push("/planner")}
              className="btn btn-primary"
            >
              Create New Trip
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trips.map((trip) => (
              <div
                key={trip.id}
                className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer overflow-hidden"
                onClick={() => handleViewTrip(trip)}
              >
                {/* Thumbnail Image */}
                {trip.itinerary?.hero_image && (
                  <figure className="h-48 overflow-hidden">
                    <img
                      src={trip.itinerary.hero_image.small}
                      alt={
                        trip.itinerary.hero_image.alt_description || trip.title
                      }
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                  </figure>
                )}

                <div className="card-body">
                  <h2 className="card-title">{trip.title}</h2>
                  <div className="space-y-2 text-sm">
                    <p className="flex items-center gap-2">
                      <span>📍</span>
                      <span className="capitalize">{trip.destination}</span>
                    </p>
                    <p className="flex items-center gap-2">
                      <span>📅</span>
                      <span>
                        {trip.days} {trip.days === 1 ? "day" : "days"}
                      </span>
                    </p>
                    {trip.checkIn && trip.checkOut && (
                      <p className="flex items-center gap-2">
                        <span>🗓️</span>
                        <span>
                          {formatDate(trip.checkIn)} -{" "}
                          {formatDate(trip.checkOut)}
                        </span>
                      </p>
                    )}
                    {trip.budget && (
                      <p className="flex items-center gap-2">
                        <span>💰</span>
                        <span>{trip.budget}</span>
                      </p>
                    )}
                  </div>
                  <div className="text-xs text-base-content/60 mt-3">
                    Saved on {new Date(trip.createdAt).toLocaleDateString()}
                  </div>
                  <div className="card-actions justify-between mt-4">
                    <button
                      onClick={(e) => handleDeleteTrip(trip.id, e)}
                      className="btn btn-error btn-sm btn-outline"
                    >
                      🗑️ Delete
                    </button>
                    <button className="btn btn-primary btn-sm">
                      View Details →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedTripsPage;
