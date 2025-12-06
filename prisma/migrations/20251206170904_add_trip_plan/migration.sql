-- CreateTable
CREATE TABLE "TripPlan" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "destination" TEXT NOT NULL,
    "country" TEXT NOT NULL,
    "days" INTEGER NOT NULL,
    "budget" TEXT,
    "checkIn" TEXT,
    "checkOut" TEXT,
    "preferences" JSONB,
    "itinerary" JSONB NOT NULL,
    "hotels" JSONB,
    "heroImage" TEXT,
    "title" TEXT NOT NULL,

    CONSTRAINT "TripPlan_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "TripPlan_userId_idx" ON "TripPlan"("userId");

-- CreateIndex
CREATE INDEX "TripPlan_createdAt_idx" ON "TripPlan"("createdAt");
