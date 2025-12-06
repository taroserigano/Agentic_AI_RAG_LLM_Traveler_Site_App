import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs";
import prisma from "@/utils/db";

export async function POST(request) {
  try {
    const { userId } = auth();
    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const {
      destination,
      country,
      days,
      budget,
      checkIn,
      checkOut,
      preferences,
      itinerary,
      hotels,
      heroImage,
    } = body;

    if (!destination || !itinerary) {
      return NextResponse.json(
        { error: "Missing required fields: destination and itinerary" },
        { status: 400 }
      );
    }

    // Generate a title from the itinerary or use destination
    const title =
      itinerary.title || `${destination}, ${country} - ${days} Days`;

    const tripPlan = await prisma.tripPlan.create({
      data: {
        userId,
        destination,
        country: country || "",
        days: days || 7,
        budget,
        checkIn,
        checkOut,
        preferences: preferences || [],
        itinerary,
        hotels: hotels || [],
        heroImage,
        title,
      },
    });

    return NextResponse.json({
      success: true,
      tripPlanId: tripPlan.id,
      message: "Trip plan saved successfully!",
    });
  } catch (error) {
    console.error("Error saving trip plan:", error);
    return NextResponse.json(
      { error: "Failed to save trip plan" },
      { status: 500 }
    );
  }
}
